from io import BytesIO
from fpdf import FPDF
import os

from streamlit import pdf



FONT_PATH = r"d:/Startup/Project/ai-career-coach/src/fonts/DejaVuSans.ttf"

def text_to_pdf(text_content):
    """
    Convert text to PDF and return bytes for Streamlit download.
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Unicode font
    pdf.add_font("DejaVu", "", FONT_PATH)

    pdf.set_font("DejaVu", size=12)

    # Title
    pdf.set_font("DejaVu", size=16)
    pdf.cell(
        w=0,
        h=10,
        text="AI Career Report",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C"
    )

    pdf.ln(5)

    # Body
    pdf.set_font("DejaVu", size=12)

    pdf.multi_cell(
        w=0,
        h=8,
        text=text_content
    )

    # Return PDF as bytes
    return bytes(pdf.output())