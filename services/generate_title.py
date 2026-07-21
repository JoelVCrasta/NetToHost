import os
import logging
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import select
from groq import Groq
from groq.types.chat import ChatCompletion

from main import AsyncSessionLocal
from models.model import ChatSession

logger = logging.getLogger(__name__)

llm = Groq(api_key=os.environ.get("GROQ_API_KEY"))


async def generate_title(session_id: UUID, message: str):
    try:
        system_prompt = "Generate a 4-6 word title for a chat that starts with this message. Return ONLY the title with no quotes or punctuation."

        result: ChatCompletion = await llm.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
        )

        title = result.choices[0].message.content.strip()

        async with AsyncSessionLocal() as session:
            query = select(ChatSession).where(ChatSession.id == session_id)
            result = await session.execute(query)
            chat_session = result.scalar_one_or_none()

            if not chat_session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
                )

            chat_session.title = title
            await session.commit()

    except Exception as e:
        logger.error(f"Error generating title: {e}")
