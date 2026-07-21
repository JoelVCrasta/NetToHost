import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from supabase_auth import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from langchain_core.messages import HumanMessage, AIMessage

from main import get_session
from clients.supabase_client import get_current_user
from utils.permission import verify_permission
from models.model import ChatSession, ChatMessage, MemberRole, MessageRole
from schemas.chat import CreateChatRequest, AddMessageRequest
from services.generate_title import generate_title
from services.agent import supervisor, AgentState

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
async def create_chat(
    payload: CreateChatRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await verify_permission(
        payload.organization_id,
        user.id,
        session,
        "create chat",
        [MemberRole.OWNER, MemberRole.ADMIN],
    )

    chat_session = ChatSession(
        org_id=payload.organization_id,
        created_by=user.id,
        title="New Chat",
        is_private=payload.is_private,
    )
    session.add(chat_session)
    await session.flush()

    user_message = ChatMessage(
        session_id=chat_session.id,
        role=MessageRole.USER,
        sender_id=user.id,
        content=payload.message,
    )
    session.add(user_message)
    await session.flush()

    initial_state: AgentState = {
        "messages": [HumanMessage(content=payload.message)],
        "session_id": chat_session.id,
        "connected_hosts": {},
        "target_host_ids": [],
        "tokens_used": 0,
    }

    config = {
        "configurable": {
            "thread_id": str(chat_session.id),
        }
    }

    prev_state = await supervisor.graph.aget_state(config)
    prev_tokens = (
        prev_state.values.get("tokens_used", 0)
        if prev_state and prev_state.values
        else 0
    )

    result = await supervisor.graph.ainvoke(input=initial_state, config=config)

    current_tokens = result.get("tokens_used", 0)
    turn_tokens = max(0, current_tokens - prev_tokens)

    ai_message = ChatMessage(
        session_id=chat_session.id,
        role=MessageRole.ASSISTANT,
        content=result["messages"][-1].content,
        tokens=turn_tokens,
    )

    session.add(ai_message)
    await session.commit()
    await session.refresh(ai_message)

    background_tasks.add_task(generate_title, chat_session.id, payload.message)

    return {
        "id": ai_message.id,
        "session_id": chat_session.id,
        "role": ai_message.role,
        "content": ai_message.content,
        "tokens": ai_message.tokens,
        "created_at": ai_message.created_at,
    }


@router.post("/{session_id}")
async def send_message(
    session_id: UUID,
    payload: AddMessageRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    chat_session_query = select(ChatSession).where(ChatSession.id == session_id)
    result = await session.execute(chat_session_query)
    chat_session = result.scalar_one_or_none()

    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found."
        )

    await verify_permission(
        chat_session.org_id,
        user.id,
        session,
        "chat",
        [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.VIEWER],
    )

    new_message = ChatMessage(
        session_id=session_id,
        role=MessageRole.USER,
        sender_id=user.id,
        content=payload.message,
    )
    session.add(new_message)
    await session.flush()

    config = {
        "configurable": {
            "thread_id": str(chat_session.id),
        }
    }

    prev_state = await supervisor.graph.aget_state(config)
    prev_tokens = (
        prev_state.values.get("tokens_used", 0)
        if prev_state and prev_state.values
        else 0
    )

    # Rehydrate messages from DB if in-memory checkpoint was cleared
    if not (prev_state and prev_state.values and prev_state.values.get("messages")):
        history_query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        history_result = await session.execute(history_query)
        past_messages = history_result.scalars().all()

        formatted_messages = []
        for msg in past_messages:
            if msg.role == MessageRole.USER:
                formatted_messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                formatted_messages.append(AIMessage(content=msg.content))

        input_state = {
            "messages": formatted_messages,
            "session_id": chat_session.id,
            "connected_hosts": {},
            "target_host_ids": [],
            "tokens_used": 0,
        }
    else:
        input_state = {"messages": [HumanMessage(content=payload.message)]}

    result = await supervisor.graph.ainvoke(input=input_state, config=config)

    current_tokens = result.get("tokens_used", 0)
    turn_tokens = max(0, current_tokens - prev_tokens)

    ai_message = ChatMessage(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        content=result["messages"][-1].content,
        tokens=turn_tokens,
    )

    session.add(ai_message)
    await session.commit()
    await session.refresh(ai_message)

    return {
        "id": ai_message.id,
        "session_id": session_id,
        "role": ai_message.role,
        "content": ai_message.content,
        "tokens": ai_message.tokens,
        "created_at": ai_message.created_at,
    }


@router.get("/organization/{organization_id}")
async def get_chats(
    organization_id: UUID,
    limit: int = Query(default=10, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await verify_permission(
        organization_id,
        user.id,
        session,
        "view chats",
        [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.VIEWER],
    )

    query = (
        select(ChatSession)
        .where(ChatSession.org_id == organization_id)
        .order_by(ChatSession.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    sessions = result.scalars().all()
    return sessions


@router.get("/{session_id}")
async def get_chat_session(
    session_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    chat_session_query = select(ChatSession).where(ChatSession.id == session_id)
    result = await session.execute(chat_session_query)
    chat_session = result.scalar_one_or_none()

    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found."
        )

    await verify_permission(
        chat_session.org_id,
        user.id,
        session,
        "view chat",
        [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.VIEWER],
    )

    messages_query = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    result = await session.execute(messages_query)
    messages = result.scalars().all()

    chat_session.messages = messages

    return chat_session


@router.delete("/{session_id}")
async def delete_chat_session(
    session_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    chat_session_query = select(ChatSession).where(ChatSession.id == session_id)
    result = await session.execute(chat_session_query)
    chat_session = result.scalar_one_or_none()

    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found."
        )

    await verify_permission(
        chat_session.org_id,
        user.id,
        session,
        "delete chat",
        [MemberRole.OWNER, MemberRole.ADMIN],
    )

    await session.delete(chat_session)
    await session.commit()

    return {"message": "Chat deleted successfully."}
