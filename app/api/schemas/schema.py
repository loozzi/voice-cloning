from pydantic import BaseModel
from enum import Enum


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class TTSRequest(BaseModel):
    text: str
    voice_id: str


class TTSJobResponse(BaseModel):
    job_id: str
    status: JobStatus
    download_url: str | None = None
    error: str | None = None
    chunks_done: int | None = None
    chunks_total: int | None = None
    eta_s: float | None = None
