from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def render_pdf(title: str, lines: list[str]) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, title)
    y -= 30
    c.setFont("Helvetica", 11)
    for line in lines:
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50
        c.drawString(40, y, str(line))
        y -= 18
    c.save()
    buffer.seek(0)
    return buffer.read()
