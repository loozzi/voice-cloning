import asyncio
import logging

from arq.connections import RedisSettings

from app.core.configs import settings
from app.core.model import get_model, _gpu_semaphore
from app.core.redis import set_job_status
from app.services.tts import split_into_chunks
from app.services.voices import load_preset_voice
from app.services.audio import concat_audio, to_wav_bytes
from app.services.storage import save_audio

logger = logging.getLogger(__name__)


async def process_tts_job(ctx, *, job_id: str, text: str, voice_id: str) -> None:
    logger.info("Starting job %s (voice=%s, chars=%d)", job_id, voice_id, len(text))

    try:
        await set_job_status(job_id, "running")

        ref_audio, ref_sr, ref_text = load_preset_voice(voice_id)
        chunks = split_into_chunks(text)
        logger.info("Job %s split into %d chunk(s)", job_id, len(chunks))

        generation_config = dict(
            temperature=0.3,
            top_k=20,
            top_p=0.9,
            max_new_tokens=4096,
            repetition_penalty=2.0,
            subtalker_do_sample=True,
            subtalker_temperature=0.1,
            subtalker_top_k=20,
            subtalker_top_p=1.0,
        )

        audio_chunks = []
        sr = None

        async with _gpu_semaphore:
            loop = asyncio.get_event_loop()
            model = get_model()
            for i, chunk in enumerate(chunks):
                logger.info("Job %s: inferring chunk %d/%d", job_id, i + 1, len(chunks))
                wavs, sr = await loop.run_in_executor(
                    None,
                    lambda c=chunk: model.generate_voice_clone(
                        text=c,
                        language="Vietnamese",
                        ref_audio=ref_audio,
                        ref_text=ref_text,
                        **generation_config,
                    ),
                )
                audio_chunks.append(wavs[0])

        merged = concat_audio(audio_chunks, sr=sr)
        wav_bytes = to_wav_bytes(merged, sr)
        download_url = await save_audio(job_id, wav_bytes)

        await set_job_status(job_id, "done", download_url=download_url)
        logger.info("Job %s done", job_id)

    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        await set_job_status(job_id, "failed", error=str(exc))


class WorkerSettings:
    functions = [process_tts_job]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 1  # 1 GPU inference at a time per worker process
    job_timeout = 600
