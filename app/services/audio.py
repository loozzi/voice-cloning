import io

import numpy as np
import soundfile as sf


def concat_audio(chunks: list[np.ndarray], silence_ms: int = 300, sr: int = 24000) -> np.ndarray:
    """Concatenate audio arrays, inserting a short silence between chunks."""
    silence = np.zeros(int(sr * silence_ms / 1000), dtype=np.float32)
    parts: list[np.ndarray] = []
    for i, chunk in enumerate(chunks):
        parts.append(chunk.astype(np.float32))
        if i < len(chunks) - 1:
            parts.append(silence)
    return np.concatenate(parts) if parts else np.array([], dtype=np.float32)


def to_wav_bytes(audio: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format="WAV", subtype="PCM_16")
    return buf.getvalue()
