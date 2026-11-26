from pathlib import Path
from typing import Tuple
from pypdf import PdfReader
from docx import Document


def parse_document(file_path: str, file_type: str) -> Tuple[str, int, str, str]:
    """
    Parse PDF, DOCX, or TXT document into plain text.
    Returns: (extracted_text, page_count, parse_status, parse_note)
    """
    path = Path(file_path)
    if not path.exists():
        return "", 0, "failed", "Uploaded file not found on disk."

    try:
        if file_type == "pdf":
            reader = PdfReader(str(path))
            pages_text = []
            for idx, page in enumerate(reader.pages, start=1):
                txt = (page.extract_text() or "").strip()
                if txt:
                    pages_text.append(f"[Page {idx}]\n{txt}")
            full_text = "\n\n".join(pages_text).strip()
            page_count = len(reader.pages)
            if len(full_text) < 40:
                return (
                    "",
                    page_count,
                    "scanned_fallback",
                    "No selectable text could be extracted from this PDF (it may be scanned or image-based). Please paste the tender text directly.",
                )
            return full_text, page_count, "parsed", f"Extracted text from {page_count} PDF page(s)."

        if file_type == "docx":
            doc = Document(str(path))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    cells = [c.text.strip() for c in row.cells if c.text and c.text.strip()]
                    if cells:
                        paragraphs.append(" | ".join(cells))
            full_text = "\n".join(paragraphs).strip()
            if not full_text:
                return "", 1, "scanned_fallback", "DOCX contains no readable text. Please paste the tender text directly."
            return full_text, 1, "parsed", "Extracted text from DOCX document."

        if file_type == "txt":
            full_text = path.read_text(encoding="utf-8", errors="replace").strip()
            if not full_text:
                return "", 1, "failed", "Text file is empty."
            return full_text, 1, "parsed", "Read plain text document."

        return "", 0, "failed", f"Unsupported file type: {file_type}"
    except Exception as exc:
        return "", 0, "failed", f"Document parsing error: {str(exc)}"
