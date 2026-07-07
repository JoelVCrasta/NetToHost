import os
import asyncio
from typing import Annotated, Sequence, TypedDict
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq

from dotenv import load_dotenv

load_dotenv()
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


class Agent:
    def __init__(self):
        self.client = None
        self.llm = None
        self.graph = None

    def call_llm(self, state: GraphState) -> AIMessage:
        if not self.llm:
            raise ValueError("LLM not found.")

        system_prompt = SystemMessage(
            content="You are an assistant that can call tools to help answer questions."
        )
        response = self.llm.invoke([system_prompt] + list(state["messages"]))

        return {"messages": [response]}

    def should_continue(self, state: GraphState) -> bool:
        if state["messages"][-1].tool_calls:
            return "tools"
        else:
            return END

    async def initialize(self):
        self.client = MultiServerMCPClient(
            {"local-1": {"transport": "http", "url": "http://0.0.0.0:8001/mcp"}}
        )

        tools = await self.client.get_tools()
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", temperature=0.3
        ).bind_tools(tools)

        workflow = StateGraph(GraphState)
        workflow.add_node("agent", self.call_llm)
        workflow.add_node("tools", ToolNode(tools))

        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent", self.should_continue, {"tools": "tools", END: END}
        )
        workflow.add_edge("tools", "agent")

        self.graph = workflow.compile()


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
# graph = studio_agent.gra
