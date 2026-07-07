import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL is missing.")
async_db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    async_db_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await agent.initialize()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan, title="NetToHost API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes import auth, organization, host, agent

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(
    organization.router, prefix="/api/organizations", tags=["Organizations"]
)
app.include_router(host.router, prefix="/api/organizations", tags=["Host Devices"])
app.include_router(agent.router, tags=["Agent"])


@app.get("/health")
async def health_check():
    return {"status": "online", "message": "NetToHost API is running"}
