import asyncio
from pathlib import Path

from app.core.configs import settings


def _output_path(job_id: str) -> Path:
    return Path(settings.output_dir) / f"{job_id}.wav"


async def save_audio(job_id: str, wav_bytes: bytes) -> str:
    path = _output_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(path.write_bytes, wav_bytes)
    return f"/tts/{job_id}/file"


def get_audio_path(job_id: str) -> Path:
    return _output_path(job_id)
