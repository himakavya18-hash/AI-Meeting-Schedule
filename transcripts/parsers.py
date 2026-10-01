import os
import io
import logging

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB limit

def parse_txt(file_obj):
    """Parses plain text file."""
    try:
        content = file_obj.read()
        if isinstance(content, bytes):
            return content.decode('utf-8', errors='ignore')
        return content
    except Exception as e:
        logger.error(f"Error parsing TXT file: {e}")
        raise ValueError("Failed to parse TXT file.")

def parse_pdf(file_obj):
    """Parses PDF file using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_obj)
        text_pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text_pages.append(text)
        return "\n".join(text_pages)
    except Exception as e:
        logger.error(f"Error parsing PDF file: {e}")
        raise ValueError(f"Failed to parse PDF file: {str(e)}")

def parse_docx(file_obj):
    """Parses DOCX file using python-docx."""
    try:
        import docx
        doc = docx.Document(file_obj)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error(f"Error parsing DOCX file: {e}")
        raise ValueError(f"Failed to parse DOCX file: {str(e)}")

def extract_transcript_text(file_obj):
    """
    Determines file type and extracts text accordingly.
    """
    if file_obj.size > MAX_FILE_SIZE:
        raise ValueError("File size exceeds maximum allowed limit of 10 MB.")

    filename = file_obj.name.lower()
    if filename.endswith('.txt'):
        return parse_txt(file_obj)
    elif filename.endswith('.pdf'):
        return parse_pdf(file_obj)
    elif filename.endswith('.docx') or filename.endswith('.doc'):
        return parse_docx(file_obj)
    else:
        # Fallback to text decoding
        return parse_txt(file_obj)
