import os
import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from services.agent import supervisor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

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
    supervisor.initialize()
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


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    logger.error(
        f"Database integrity error on {request.method} {request.url.path}: {exc}"
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid data provided or constraint violation."},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


from routes import auth, organization, host, agent, chat

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(
    organization.router, prefix="/api/organizations", tags=["Organizations"]
)
app.include_router(host.router, prefix="/api/organizations", tags=["Host Devices"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(agent.router, tags=["Agent"])


@app.get("/health")
async def health_check():
    return {"status": "online", "message": "NetToHost API is running"}
