from fastapi import APIRouter
from pydantic import BaseModel

from app.services.voices import list_preset_voices

router = APIRouter(prefix="/voices", tags=["voices"])


class VoiceItem(BaseModel):
    voice_id: str
    name: str


@router.get("", response_model=list[VoiceItem])
async def list_voices() -> list[VoiceItem]:
    return [VoiceItem(voice_id=v.voice_id, name=v.name) for v in list_preset_voices()]
