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
