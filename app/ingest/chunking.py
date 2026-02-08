from typing import List, Dict, Tuple

def chunk_text(
    pages: List[Tuple[int, str]],
    chunk_size_chars: int,
    overlap_chars: int
) -> List[Dict]:
    """
    Basic character-based chunking with overlap.

    Considerations:
    - Character chunking is simple and robust for beginners.
    - Overlap helps avoid splitting key info across boundaries.
    - We store page_start/page_end as an approximate range.
    """
    chunks: List[Dict] = []
    buffer = ""
    page_start = None
    page_end = None

    def flush(buf: str, ps: int, pe: int):
        if buf.strip():
            chunks.append({
                "text": buf.strip(),
                "page_start": ps,
                "page_end": pe,
            })

    for page_num, text in pages:
        cleaned = " ".join(text.split())  # whitespace normalization
        if not cleaned:
            continue

        if page_start is None:
            page_start = page_num
        page_end = page_num

        buffer = (buffer + " " + cleaned).strip()

        while len(buffer) > chunk_size_chars:
            cut = buffer[:chunk_size_chars]
            flush(cut, page_start, page_end)

            # keep overlap
            start = max(0, chunk_size_chars - overlap_chars)
            buffer = buffer[start:].strip()

    if page_start is not None:
        flush(buffer, page_start, page_end)

    return chunks
