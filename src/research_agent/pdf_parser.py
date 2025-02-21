import os
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)

    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"

    return text
