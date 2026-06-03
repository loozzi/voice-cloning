import os
from pathlib import Path
from typing import NamedTuple

import soundfile as sf
import numpy as np

from app.core.configs import settings


class VoicePreset(NamedTuple):
    voice_id: str
    name: str


def _voice_dir(voice_id: str) -> Path:
    return Path(settings.voices_dir) / voice_id


def list_preset_voices() -> list[VoicePreset]:
    base = Path(settings.voices_dir)
    if not base.exists():
        return []
    return [
        VoicePreset(voice_id=d.name, name=d.name.replace("_", " ").title())
        for d in sorted(base.iterdir())
        if d.is_dir() and (d / "audio.wav").exists()
    ]


def load_preset_voice(voice_id: str) -> tuple[np.ndarray, int, str]:
    """Returns (audio_array, sample_rate, transcript)."""
    d = _voice_dir(voice_id)
    audio_path = d / "audio.wav"
    transcript_path = d / "transcript.txt"

    if not audio_path.exists():
        raise ValueError(f"Voice '{voice_id}' not found")

    audio, sr = sf.read(str(audio_path), dtype="float32")
    transcript = transcript_path.read_text(encoding="utf-8").strip() if transcript_path.exists() else ""
    return audio, sr, transcript
