from PyPDF2 import PdfReader

def parse_resume(file_stream):
    try:
        pdf_reader = PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
