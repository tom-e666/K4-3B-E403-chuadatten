"""Phát hiện học viên chép nguyên văn slide thay vì tự diễn đạt.

Feynman chỉ có tác dụng khi người học NÓI RA bằng lời của mình. Dán lại nguyên đoạn slide
cũng qua được bài chấm ngữ nghĩa — đúng kiểu "illusion of competence" mà sản phẩm sinh ra để chống.
Module này so câu trả lời với chính text của trang slide tương ứng (đọc bằng pypdf, cache sẵn).
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

SLIDES_DIR = Path(__file__).resolve().parent.parent / "data" / "vlearn-pack" / "slides"

_PAGE_TEXT_CACHE: dict[tuple[str, int], str] = {}

NGRAM = 6              # chuỗi 6 từ liên tiếp — đủ dài để không báo nhầm cụm thuật ngữ thường gặp
COPY_RATIO = 0.45      # >=45% số cụm trong câu trả lời trùng slide -> coi là chép
MIN_WORDS = 25         # câu ngắn thì bỏ qua, không đủ cơ sở kết luận


def _normalize(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text or "").lower()
    text = re.sub(r"[^0-9a-zà-ỹ\s]+", " ", text)
    return [w for w in text.split() if w]


def get_page_text(pdf_file: str, page: int) -> str:
    """Text của đúng một trang slide (cache lại, đọc PDF chỉ một lần cho mỗi trang)."""
    key = (pdf_file, int(page or 0))
    if key in _PAGE_TEXT_CACHE:
        return _PAGE_TEXT_CACHE[key]

    path = SLIDES_DIR / pdf_file
    text = ""
    if pdf_file and page and path.exists():
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            if 1 <= page <= len(reader.pages):
                text = reader.pages[page - 1].extract_text() or ""
        except Exception:
            text = ""
    _PAGE_TEXT_CACHE[key] = text
    return text


def _ngrams(words: list[str], n: int = NGRAM) -> set[str]:
    return {" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def copy_ratio(answer: str, slide_text: str) -> float:
    """Tỉ lệ cụm 6 từ của câu trả lời xuất hiện nguyên vẹn trong text slide (0..1)."""
    ans_words = _normalize(answer)
    if len(ans_words) < MIN_WORDS:
        return 0.0
    slide_words = _normalize(slide_text)
    if len(slide_words) < NGRAM:
        return 0.0

    ans_grams = _ngrams(ans_words)
    if not ans_grams:
        return 0.0
    slide_grams = _ngrams(slide_words)
    return len(ans_grams & slide_grams) / len(ans_grams)


def looks_copied(answer: str, pdf_file: str | None, page: int | None) -> tuple[bool, float]:
    """(có phải chép không, tỉ lệ trùng). Không đọc được slide thì luôn trả False."""
    if not pdf_file or not page:
        return False, 0.0
    ratio = copy_ratio(answer, get_page_text(pdf_file, int(page)))
    return ratio >= COPY_RATIO, ratio
