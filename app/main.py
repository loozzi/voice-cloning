from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import setup_logging
from app.core.redis import close_pool

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()


app = FastAPI(title="Voice Cloning TTS", version="0.1.0", lifespan=lifespan)

from app.api.routes import tts, voices  # noqa: E402

app.include_router(tts.router)
app.include_router(voices.router)
