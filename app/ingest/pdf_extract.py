from pypdf import PdfReader

def extract_pdf_text_and_pages(path: str):
    """
    Returns list of (page_number, text).
    Note: If a PDF is scanned (image-only), extract_text may return empty.
    """
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append((i + 1, text))
    return pages
