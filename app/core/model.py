from qwen_tts import Qwen3TTSModel
import torch, asyncio

_model = None
_gpu_semaphore = asyncio.Semaphore(1)

def get_model():
    global _model
    if _model is None:
        _model = Qwen3TTSModel.from_pretrained(
            "g-group-ai-lab/gwen-tts-0.6B",
            device_map="auto",
            dtype=torch.float16,
            attn_implementation="eager",
        )

    return _model