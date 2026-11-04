import io
import re
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file bytes with robust layout and standard fallbacks."""
    if not file_bytes:
        raise ValueError("Uploaded PDF file is empty.")

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []

        for page in reader.pages:
            page_content = ""
            # Try layout extraction first
            try:
                page_content = page.extract_text(extraction_mode="layout") or ""
            except Exception:
                page_content = ""

            # Fallback to standard extraction
            if not page_content.strip():
                try:
                    page_content = page.extract_text() or ""
                except Exception:
                    page_content = ""

            if page_content.strip():
                clean_page = page_content.replace("\x00", "").replace("\r\n", "\n")
                pages_text.append(clean_page.strip())

        full_extracted = "\n\n".join(pages_text).strip()

        if not full_extracted:
            raise ValueError(
                "Unable to extract text from this PDF. It may be a scanned image or encrypted. "
                "Please copy and paste your resume text directly into the box."
            )

        full_extracted = re.sub(r'[ \t]+', ' ', full_extracted)
        return full_extracted

    except Exception as e:
        if "scanned image" in str(e):
            raise
        raise ValueError(f"Failed to extract text from PDF: {e}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX file bytes."""
    if not file_bytes:
        raise ValueError("Uploaded DOCX file is empty.")

    try:
        doc = Document(io.BytesIO(file_bytes))
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_data:
                    full_text.append(" | ".join(row_data))
        result = "\n".join(full_text).strip()
        if not result:
            raise ValueError("The uploaded DOCX file contains no readable text.")
        return result
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {e}")


def extract_resume_text(uploaded_file) -> str:
    """
    Dispatch file extraction based on extension/type.
    Supports Werkzeug FileStorage (.filename), Streamlit UploadedFile (.name),
    and raw file-like objects with magic byte detection.
    """
    filename = (
        getattr(uploaded_file, "filename", None)
        or getattr(uploaded_file, "name", None)
        or ""
    ).lower()

    if hasattr(uploaded_file, "seek"):
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

    content = uploaded_file.read() if hasattr(uploaded_file, "read") else b""

    if isinstance(content, str):
        content = content.encode("utf-8")

    # Extension-based dispatch
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(content)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(content)
    elif filename.endswith(".txt") or filename.endswith(".md"):
        return content.decode("utf-8", errors="ignore").strip()

    # Magic byte inspection fallback
    if content.startswith(b"%PDF"):
        return extract_text_from_pdf(content)
    elif content.startswith(b"PK\x03\x04"):
        return extract_text_from_docx(content)
    else:
        try:
            decoded = content.decode("utf-8").strip()
            if decoded:
                return decoded
        except Exception:
            pass
        raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
