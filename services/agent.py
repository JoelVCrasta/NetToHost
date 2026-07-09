import os
import asyncio
import logging
from typing import Annotated, Sequence, TypedDict, Optional, Literal
from dotenv import load_dotenv
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

load_dotenv()


class Agent(str, Enum):
    GENERAL = "general_agent"
    HOST = "host_agent"


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    session_id: UUID
    host_id: Optional[str]
    active_agent: str
    pending_approval: bool


class RouteDecision(BaseModel):
    target: Literal[Agent.GENERAL, Agent.HOST] = Field(
        description=f"Choose {Agent.GENERAL} for general questions and casual chat. Choose {Agent.HOST} if the user wants to execute commands."
    )


class Supervisor:
    def __init__(self):
        self.client = None
        self.llm: ChatGroq = None
        self.graph = None

    async def router_node(self, state: AgentState):
        logger.info("Router is evaluating the request...")

        structured_llm = self.llm.with_structured_output(RouteDecision)
        messages = [
            {
                "role": "system",
                "content": "You are a routing assistant that decides which agent should handle the user's request.",
            },
            {
                "role": "user",
                "content": state["messages"][-1].content,
            },
        ]
        result: RouteDecision = await structured_llm.invoke(messages)

        logger.info(f"Router decision: {result.target}")
        return result.target

    async def initialize(self):
        pass


# class Agent:
#     def __init__(self):
#         self.client = None
#         self.llm = None
#         self.graph = None

#     def call_llm(self, state: AgentState) -> AIMessage:
#         if not self.llm:
#             raise ValueError("LLM not found.")

#         system_prompt = SystemMessage(
#             content="You are an assistant that can call tools to help answer questions."
#         )
#         response = self.llm.invoke([system_prompt] + list(state["messages"]))

#         return {"messages": [response]}

#     def should_continue(self, state: GraphState) -> bool:
#         if state["messages"][-1].tool_calls:
#             return "tools"
#         else:
#             return END

#     async def initialize(self):
#         self.client = MultiServerMCPClient(
#             {"local-1": {"transport": "http", "url": "http://0.0.0.0:8001/mcp"}}
#         )

#         tools = await self.client.get_tools()
#         self.llm = ChatGroq(
#             model="llama-3.3-70b-versatile", temperature=0.3
#         ).bind_tools(tools)

#         workflow = StateGraph(GraphState)
#         workflow.add_node("agent", self.call_llm)
#         workflow.add_node("tools", ToolNode(tools))

#         workflow.add_edge(START, "agent")
#         workflow.add_conditional_edges(
#             "agent", self.should_continue, {"tools": "tools", END: END}
#         )
#         workflow.add_edge("tools", "agent")

#         self.graph = workflow.compile()


# ---------------------------------------------------------------------------------------------------

# agent = Agent()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await agent.initialize()
#     yield

# app = FastAPI(lifespan=lifespan)

# class ChatRequest(BaseModel):
#     message: str

# @app.post("/chat")
# async def handle_chat(payload: ChatRequest):
#     initial_state = {"messages": [HumanMessage(content=payload.message)]}
#     response = await agent.graph.ainvoke(initial_state)

#     return { "response": response["messages"][-1].content }

# studio_agent = Agent()
# asyncio.run(studio_agent.initialize())
# graph = studio_agent.graph
