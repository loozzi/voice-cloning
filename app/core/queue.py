from app.core.redis import get_pool, set_job_status


async def enqueue_tts_job(job_id: str, text: str, voice_id: str) -> None:
    await set_job_status(job_id, "pending")
    pool = await get_pool()
    await pool.enqueue_job(
        "process_tts_job",
        job_id=job_id,
        text=text,
        voice_id=voice_id,
        _job_id=job_id,  # dùng job_id làm ARQ job ID để tránh duplicate
    )
