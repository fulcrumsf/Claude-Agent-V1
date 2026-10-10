import re
import subprocess
from pathlib import Path

from pypdf import PdfReader


AMOUNT_PATTERN = re.compile(r"(USD|EUR|GBP|CAD|AUD|\$|€|£)\s*([0-9][0-9,]*\.[0-9]{2})\b")
SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}
DATE_PATTERN = re.compile(r"\b(20[0-9]{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12][0-9]|3[01])\b")
INVOICE_PATTERN = re.compile(r"(?:invoice|receipt|order|billing)\s*(?:number|no\.?|#)?\s*[:=-]?\s*([A-Z0-9-]{3,})", re.I)


def extract_text(path):
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            reader = PdfReader(path)
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            if text.strip():
                return {"text": text, "confidence": "text", "source": "pdf"}
        except Exception:
            pass
    command = ["/usr/local/bin/tesseract", str(path), "stdout"]
    if not Path(command[0]).exists():
        command[0] = "/opt/homebrew/bin/tesseract"
    if not Path(command[0]).exists():
        command[0] = "tesseract"
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
        return {"text": result.stdout, "confidence": "ocr", "source": "ocr"}
    except Exception:
        return {"text": "", "confidence": "none", "source": "none"}


def parse_extraction(text):
    money = [(SYMBOLS.get(currency, currency), float(value.replace(",", ""))) for currency, value in AMOUNT_PATTERN.findall(text)]
    amounts = [amount for _, amount in money]
    dates = [f"{int(year):04d}-{int(month):02d}-{int(day):02d}" for year, month, day in DATE_PATTERN.findall(text)]
    invoices = INVOICE_PATTERN.findall(text)
    return {"amounts": amounts, "money": money, "dates": dates, "invoice_numbers": invoices}
