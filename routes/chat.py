import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from supabase_auth import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from langchain_core.messages import HumanMessage

from main import get_session
from clients.supabase_client import get_current_user
from utils.permission import verify_permission
from models.model import ChatSession, ChatMessage, MemberRole, MessageRole
from schemas.chat import CreateChatRequest
from services.generate_title import generate_title
from services.agent import supervisor, AgentState

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
async def chat(
    payload: CreateChatRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
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
        await session.commit()
        await session.refresh(chat_session)

        user_message = ChatMessage(
            session_id=chat_session.id,
            role=MessageRole.USER,
            sender_id=user.id,
            content=payload.message,
        )
        session.add(user_message)
        await session.commit()
        await session.refresh(user_message)

        background_tasks.add_task(generate_title, chat_session.id, payload.message)

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
        result = await supervisor.graph.ainvoke(input=initial_state, config=config)

        ai_message = ChatMessage(
            session_id=chat_session.id,
            role=MessageRole.ASSISTANT,
            content=result["messages"][-1].content,
            tokens=result.get("tokens_used", 0),
        )

        session.add(ai_message)
        await session.commit()
        await session.refresh(ai_message)

        return {
            "session_id": chat_session.id,
            "user_message": user_message,
            "ai_message": ai_message,
        }

    except HTTPException:
        raise
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error creating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data provided.",
        )
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
