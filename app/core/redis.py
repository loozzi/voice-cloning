import json
from typing import Any

from arq.connections import ArqRedis, create_pool, RedisSettings
from app.core.configs import settings

_pool: ArqRedis | None = None

JOB_TTL = 86400  # 24h


def _redis_settings() -> RedisSettings:
    return RedisSettings.from_dsn(settings.redis_url)


async def get_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(_redis_settings())
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None


# ---------- job state ----------

def _job_key(job_id: str) -> str:
    return f"tts:job:{job_id}"


async def set_job_status(job_id: str, status: str, **extra: Any) -> None:
    pool = await get_pool()
    data = {"status": status, **extra}
    await pool.set(_job_key(job_id), json.dumps(data), ex=JOB_TTL)


async def get_job_state(job_id: str) -> dict | None:
    pool = await get_pool()
    raw = await pool.get(_job_key(job_id))
    if raw is None:
        return None
    return json.loads(raw)
