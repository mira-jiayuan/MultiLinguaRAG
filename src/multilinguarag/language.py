from __future__ import annotations


def detect_language(text: str) -> str:
    """Lightweight script-based language label for metadata, not tokenization.

    Returns `ja` when kana is present, `zh` for CJK-heavy text without kana,
    otherwise `en`. The embedding model itself handles multilingual semantics.
    """
    if not text.strip():
        return "unknown"

    kana = sum(1 for c in text if "\u3040" <= c <= "\u30ff")
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    latin = sum(1 for c in text if c.isascii() and c.isalpha())

    if kana > 0:
        return "ja"
    if cjk > max(3, latin // 4):
        return "zh"
    return "en"
