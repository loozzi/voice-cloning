import re
from app.core.configs import settings


_SENTENCE_END = re.compile(r'(?<=[.!?。！？،؟])\s+')


def split_into_chunks(text: str, max_chars: int | None = None) -> list[str]:
    """
    Split text at sentence boundaries, then merge short sentences so each
    chunk stays under max_chars.  Never splits mid-sentence.
    """
    max_chars = max_chars or settings.chunk_max_chars
    sentences = _SENTENCE_END.split(text.strip())

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Single sentence already too long — hard-split at max_chars
        if not current and len(sentence) > max_chars:
            for i in range(0, len(sentence), max_chars):
                chunks.append(sentence[i : i + max_chars])
            continue

        if current and len(current) + 1 + len(sentence) > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = (current + " " + sentence).strip() if current else sentence

    if current:
        chunks.append(current)

    return chunks
