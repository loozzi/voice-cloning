import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.schemas.schema import TTSRequest, TTSJobResponse
from app.core.queue import enqueue_tts_job
from app.core.redis import get_job_state
from app.services.storage import get_audio_path

router = APIRouter(prefix="/tts", tags=["tts"])


@router.post("", response_model=TTSJobResponse, status_code=202)
async def create_tts(req: TTSRequest) -> TTSJobResponse:
    job_id = str(uuid.uuid4())
    await enqueue_tts_job(job_id, req.text, req.voice_id)
    return TTSJobResponse(job_id=job_id, status="pending")


@router.get("/{job_id}", response_model=TTSJobResponse)
async def get_tts_status(job_id: str) -> TTSJobResponse:
    state = await get_job_state(job_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return TTSJobResponse(
        job_id=job_id,
        status=state["status"],
        download_url=state.get("download_url"),
        error=state.get("error"),
    )


@router.get("/{job_id}/file", response_class=FileResponse)
async def download_audio(job_id: str) -> FileResponse:
    path = get_audio_path(job_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(path), media_type="audio/wav", filename=f"{job_id}.wav")
