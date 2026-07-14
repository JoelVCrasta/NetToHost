from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Literal, Any, Optional


class ActionType(str, Enum):
    EXECUTE_TOOL = "execute_tool"
    GET_TOOLS = "get_tools"


class GetToolsRequest(BaseModel):
    action: Literal[ActionType.GET_TOOLS] = ActionType.GET_TOOLS
    message_id: str


class ExecuteToolRequest(BaseModel):
    action: Literal[ActionType.EXECUTE_TOOL] = ActionType.EXECUTE_TOOL
    message_id: str
    name: str
    args: dict[str, Any] = Field(default_factory=dict)


class GetToolsResponse(BaseModel):
    message_id: str
    result: list[dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None


class ExecuteToolResponse(BaseModel):
    message_id: str
    result: Optional[Any] = None
    error: Optional[str] = None
