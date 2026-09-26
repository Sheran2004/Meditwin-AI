"""
Text extraction from uploaded medical reports.
Strategy: try native PDF text extraction first (fast, accurate for
digitally-generated reports); if that yields almost nothing, the PDF is
probably a scanned image, so fall back to OCR page-by-page.
"""
import io

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

MIN_NATIVE_TEXT_CHARS = 40  # below this, assume it's a scan and OCR instead


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        native_text = "\n".join(page.get_text() for page in doc)
        if len(native_text.strip()) >= MIN_NATIVE_TEXT_CHARS:
            return native_text.strip()

        # Fall back to OCR: rasterize each page and run Tesseract.
        ocr_text_parts = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text_parts.append(pytesseract.image_to_string(image))
        return "\n".join(ocr_text_parts).strip()
    finally:
        doc.close()


def extract_text_from_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image).strip()
