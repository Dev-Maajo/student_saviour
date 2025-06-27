from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import textwrap
from datetime import datetime

# ✅ Generate Career Advice PDF (returns buffer for Flask download)
def generate_advice_pdf(prompt, response, timestamp=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='QuestionStyle', fontSize=12, spaceAfter=10, leading=16))
    styles.add(ParagraphStyle(name='ResponseStyle', fontSize=12, spaceAfter=10, leading=16))
    styles.add(ParagraphStyle(name='BoldTitle', fontSize=13, leading=18, spaceAfter=6, fontName="Helvetica-Bold"))

    content = []

    # Use current time if not provided
    if not timestamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Date
    content.append(Paragraph(f"<b>Date:</b> {timestamp}", styles["Normal"]))
    content.append(Spacer(1, 0.2 * inch))

    # Prompt section
    content.append(Paragraph("<b>Your Question:</b>", styles["BoldTitle"]))
    content.append(Paragraph(prompt.replace('\n', '<br/>'), styles["QuestionStyle"]))
    content.append(Spacer(1, 0.3 * inch))

    # Response section
    content.append(Paragraph("<b>AI Response:</b>", styles["BoldTitle"]))
    content.append(Paragraph(response.replace('\n', '<br/>'), styles["ResponseStyle"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

# ✅ Generate Resume Feedback PDF (LLaMA Suggestions)
def generate_feedback_pdf(resume_text, llama_suggestions):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    max_width = width - 2 * margin
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Resume Analysis Result")

    # Resume Text
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Extracted Resume Text:")
    y -= 20
    c.setFont("Helvetica", 10)
    for line in resume_text.split("\n"):
        if y < 60:
            c.showPage()
            y = height - margin
        line_clean = line.encode("ascii", "ignore").decode()
        wrapped_lines = textwrap.wrap(line_clean, width=100)
        for wline in wrapped_lines:
            c.drawString(margin, y, wline)
            y -= 15

    # Suggestions
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "AI Suggestions (via LLaMA):")
    y -= 20
    c.setFont("Helvetica", 10)
    for fb in llama_suggestions:
        if y < 60:
            c.showPage()
            y = height - margin
        # ✅ Format suggestions
        if isinstance(fb, tuple):
            text = f"{fb[0]}: {fb[1]}"
        else:
            text = str(fb)
        text_clean = text.encode("ascii", "ignore").decode()
        wrapped_lines = textwrap.wrap(f"- {text_clean}", width=100)
        for wline in wrapped_lines:
            if y < 60:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, wline)
            y -= 15
        y -= 5  # space between suggestions

    c.save()
    buffer.seek(0)
    return buffer
