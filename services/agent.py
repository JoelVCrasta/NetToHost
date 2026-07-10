import os
import asyncio
import json
import logging
from typing import Annotated, Sequence, TypedDict, Optional, Literal
from dotenv import load_dotenv
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from services.connection_manager import conn_manager

logger = logging.getLogger(__name__)

load_dotenv()


class Node(str, Enum):
    ROUTER = "router"
    GENERAL = "general"
    HOST = "host"
    GUARDRAIL = "guardrail"
    TOOL = "tool"
    APPROVAL = "approval"


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    session_id: UUID
    connected_hosts: dict[str, str]
    target_host_ids: list[str]
    active_host_tools: dict[str, list[dict]]
    active_node: str
    pending_approval: bool
    approved: Optional[bool]
    reason: Optional[str]


class RouteDecision(BaseModel):
    target: Literal[Node.GENERAL, Node.HOST] = Field(
        description=f"Choose {Node.GENERAL} for general questions and casual chat. Choose {Node.HOST} if the user wants to execute commands."
    )


class SafetyAssessment(BaseModel):
    is_dangerous: bool = Field(
        description="Indicates whether the user's request is dangerous to execute."
    )
    reason: Optional[str] = Field(
        description="If the request is dangerous, provide a reason why."
    )


@tool
async def execute_remote_mcp_tool(name: str, args: dict, target_host_id: str) -> str:
    """
    Executes a tool on a remote host.

    Args:
        name (str): The name of the tool to execute.
        args (dict): A dictionary containing the arguments for the tool.
        target_host_id (str): The ID of the target host.
    """
    message_id = str(uuid4())
    payload = {
        "message_id": message_id,
        "action": "execute_tool",
        "tool_name": name,
        "args": args,
    }

    logger.info(f"Sending tool execution request to host {target_host_id}")

    try:
        result = await conn_manager.send_and_wait(target_host_id, message_id, payload)
        return str(result.get("result", result.get("error", "No result returned")))
    except Exception as e:
        logger.error(f"Error executing tool on host {target_host_id}: {e}")
        return f"Error executing tool on host: {str(e)}"


class Supervisor:
    def __init__(self):
        self.client = None
        self.llm: ChatGroq = None
        self.tool_llm: ChatGroq = None
        self.graph = None

    async def router_node(self, state: AgentState):
        logger.info("Router is evaluating the request...")

        structured_llm = self.llm.with_structured_output(RouteDecision)
        system_prompt = SystemMessage(
            content="You are a routing assistant that decides which agent should handle the user's request."
        )
        user_prompt = HumanMessage(content=state["messages"][-1].content)
        result: RouteDecision = await structured_llm.ainvoke(
            [system_prompt, user_prompt]
        )

        logger.info(f"Router decision: {result.target}")
        return {"active_node": result.target}

    async def general_node(self, state: AgentState):
        logger.info("General agent is handling the request...")

        system_prompt = SystemMessage(
            content="You are a helpful AI assistant. Answer the user's question directly. Do not attempt to use tools."
        )
        result = await self.llm.ainvoke([system_prompt] + list(state["messages"]))

        return {"messages": [result]}

    async def host_node(self, state: AgentState):
        logger.info("Host agent is handling the request...")

        connected_hosts_str = json.dumps(state.get("connected_hosts", {}))
        target_hosts = state.get("target_host_ids", ["None Selected"])

        tools_info = []
        for host_id in target_hosts:
            tools = state.get("active_host_tools", {}).get(host_id, [])
            tool_list = (
                "\n".join([f"- {t['name']}: {t['description']}" for t in tools])
                if tools
                else "No tools available"
            )
            tools_info.append(f"Tools for {host_id}:\n{tool_list}")

        tools_str = (
            "\n\n".join(tools_info)
            if tools_info
            else "No tools available for the target hosts."
        )

        system_prompt = SystemMessage(
            content="You are host machine control assistant with access to remote tools."
            f"The user's connected hosts are: {connected_hosts_str}."
            f"The target hosts are: {', '.join(target_hosts)}."
            f"{tools_str}"
            "Rules:"
            "1. If the user wants to execute commands, you must send the command to the target host."
            "2. If the user asks to run a command but hasn't specified a target host, you must ask them which machine to use."
            "3. If the target host name is specified, then use the corresponding host_id while calling execute_remote_mcp_tool."
        )
        result = await self.tool_llm.ainvoke([system_prompt] + list(state["messages"]))

        return {"messages": [result]}

    async def guardrail_node(self, state: AgentState):
        logger.info("Guadrail is assessing the safety of the request...")

        last_message = state["messages"][-1]
        if not (isinstance(last_message, AIMessage) and last_message.tool_calls):
            return {"pending_approval": False}

        structured_llm = self.llm.with_structured_output(SafetyAssessment)
        system_prompt = SystemMessage(
            content="You are a safety assessment assistant. Determine if the proposed tool execution is safe or dangerous."
            "Give a short reason why its dangerous."
            "Dangerous actions include any write or modification to the host system like deleting files, stopping services, "
            "restarting machines, executing raw terminal commands, or modifying configurations. Read-only commands are safe."
        )
        user_prompt = HumanMessage(
            content="\n\n".join(
                f"Tool Name: {tool_call['name']}\nArguments: {tool_call['args']}"
                for tool_call in last_message.tool_calls
            )
        )
        assessment: SafetyAssessment = await structured_llm.ainvoke(
            [system_prompt, user_prompt]
        )

        logger.info(
            f"Safety assessment: is_dangerous={assessment.is_dangerous}, reason={assessment.reason}"
        )
        return {
            "pending_approval": assessment.is_dangerous,
            "reason": assessment.reason,
        }

    async def approval_node(self, state: AgentState):
        logger.info("Handling approval response...")

        update = {"approved": None, "pending_approval": False}
        if state.get("approved") is False:
            last_message = state["messages"][-1]
            tool_messages = []

            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    tool_messages.append(
                        ToolMessage(
                            content="Tool execution rejected by user.",
                            tool_call_id=tool_call["id"],
                            name=tool_call["name"],
                        )
                    )
            update["messages"] = tool_messages

        return update

    def should_continue(self, state: AgentState):
        """Check if the host agent decided to call a tool"""
        last_message = state["messages"][-1]

        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return Node.GUARDRAIL

        return END

    def initialize(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

        tools = [execute_remote_mcp_tool]
        self.tool_llm = self.llm.bind_tools(tools)

        workflow = StateGraph(AgentState)

        workflow.add_node("router_node", self.router_node)
        workflow.add_node("general_node", self.general_node)
        workflow.add_node("host_node", self.host_node)
        workflow.add_node("guardrail_node", self.guardrail_node)
        workflow.add_node("approval_node", self.approval_node)
        workflow.add_node("tools_node", ToolNode(tools))

        workflow.add_edge(START, "router_node")
        workflow.add_conditional_edges(
            "router_node",
            lambda state: state.get("active_node", Node.GENERAL),
            {
                Node.GENERAL: "general_node",
                Node.HOST: "host_node",
            },
        )
        workflow.add_edge("general_node", END)
        workflow.add_conditional_edges(
            "host_node",
            self.should_continue,
            {
                Node.GUARDRAIL: "guardrail_node",
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "guardrail_node",
            lambda state: (
                Node.APPROVAL if state.get("pending_approval") else Node.TOOL
            ),
            {
                Node.APPROVAL: "approval_node",
                Node.TOOL: "tools_node",
            },
        )
        workflow.add_conditional_edges(
            "approval_node",
            lambda state: (Node.TOOL if state.get("approved") is True else Node.HOST),
            {
                Node.TOOL: "tools_node",
                Node.HOST: "host_node",
            },
        )
        workflow.add_edge("tools_node", "host_node")

        memory = MemorySaver()
        self.graph = workflow.compile(
            checkpointer=memory, interrupt_before=["approval_node"]
        )
