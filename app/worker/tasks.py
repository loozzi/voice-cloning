import asyncio
import logging
import time

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

        ref_audio_arr, ref_sr, ref_text = load_preset_voice(voice_id)
        ref_audio = (ref_audio_arr, ref_sr)
        chunks = split_into_chunks(text)
        logger.info("Job %s split into %d chunk(s)", job_id, len(chunks))

        generation_config = dict(
            temperature=0.3,
            top_k=20,
            top_p=0.9,
            max_new_tokens=4096,
            repetition_penalty=1.3,
            subtalker_do_sample=True,
            subtalker_temperature=0.1,
            subtalker_top_k=20,
            subtalker_top_p=1.0,
        )

        audio_chunks = []
        sr = None
        n = len(chunks)

        async with _gpu_semaphore:
            loop = asyncio.get_event_loop()
            model = get_model()
            chunk_times: list[float] = []
            for i, chunk in enumerate(chunks):
                logger.info("Job %s: inferring chunk %d/%d", job_id, i + 1, n)
                t0 = time.monotonic()
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
                chunk_times.append(time.monotonic() - t0)
                audio_chunks.append(wavs[0])

                avg = sum(chunk_times) / len(chunk_times)
                eta = avg * (n - i - 1)
                logger.info("Job %s: chunk %d done in %.1fs, eta=%.1fs", job_id, i + 1, chunk_times[-1], eta)
                await set_job_status(job_id, "running", chunks_done=i + 1, chunks_total=n, eta_s=round(eta, 1))

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
