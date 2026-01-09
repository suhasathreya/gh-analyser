"""
Export utilities for generating PDF and Word documents from markdown reports.
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

import markdown
import os
import re


def generate_pdf(analysis_id: str) -> str:
    """
    Generate a styled PDF from the markdown report using ReportLab.

    Args:
        analysis_id: Analysis ID

    Returns:
        Path to generated PDF file

    Raises:
        FileNotFoundError: If report markdown doesn't exist
    """
    report_path = f"analyses/{analysis_id}/report.md"
    pdf_path = f"analyses/{analysis_id}/report.pdf"

    # Read markdown content
    with open(report_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a1a1a',
        spaceAfter=12
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2c3e50',
        spaceAfter=10,
        spaceBefore=10
    )

    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor='#34495e',
        spaceAfter=8,
        spaceBefore=8
    )

    body_style = styles['BodyText']
    body_style.fontSize = 10
    body_style.leading = 14

    # Parse markdown line by line
    lines = md_content.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            story.append(Spacer(1, 0.1*inch))
            continue

        # Headers
        if line.startswith('# '):
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading2_style))
        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, heading3_style))
        # Horizontal rules
        elif line.startswith('---') or line.startswith('***'):
            story.append(Spacer(1, 0.2*inch))
        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
            story.append(Paragraph(f"• {text}", body_style))
        # Regular text
        else:
            # Remove/convert markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
            story.append(Paragraph(text, body_style))

    # Build PDF
    doc.build(story)

    return pdf_path


def generate_docx(analysis_id: str) -> str:
    """
    Generate a Word document from the markdown report.

    Args:
        analysis_id: Analysis ID

    Returns:
        Path to generated Word document

    Raises:
        FileNotFoundError: If report markdown doesn't exist
    """
    report_path = f"analyses/{analysis_id}/report.md"
    docx_path = f"analyses/{analysis_id}/report.docx"

    # Read markdown content
    with open(report_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Create Document
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    # Parse markdown line by line (basic parser)
    lines = md_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Heading 1
        if line.startswith('# '):
            heading = doc.add_heading(line[2:].strip(), level=1)
            heading.style.font.color.rgb = RGBColor(26, 26, 26)

        # Heading 2
        elif line.startswith('## '):
            heading = doc.add_heading(line[3:].strip(), level=2)
            heading.style.font.color.rgb = RGBColor(44, 62, 80)

        # Heading 3
        elif line.startswith('### '):
            heading = doc.add_heading(line[4:].strip(), level=3)
            heading.style.font.color.rgb = RGBColor(52, 73, 94)

        # Horizontal rule
        elif line.startswith('---') or line.startswith('***'):
            doc.add_paragraph('_' * 60)

        # Unordered list
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
            text = re.sub(r'\*(.*?)\*', r'\1', text)  # Italic
            text = re.sub(r'`(.*?)`', r'\1', text)  # Code
            doc.add_paragraph(text, style='List Bullet')

        # Ordered list
        elif re.match(r'^\d+\. ', line):
            text = re.sub(r'^\d+\. ', '', line).strip()
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = re.sub(r'`(.*?)`', r'\1', text)
            doc.add_paragraph(text, style='List Number')

        # Code block
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            code_text = '\n'.join(code_lines)
            p = doc.add_paragraph(code_text)
            p.style.font.name = 'Courier New'
            p.style.font.size = Pt(9)

        # Regular paragraph
        else:
            # Remove markdown formatting while adding to doc
            text = line

            # Simple bold and italic handling
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = re.sub(r'`(.*?)`', r'\1', text)

            # Add paragraph
            if text.strip():
                doc.add_paragraph(text.strip())

        i += 1

    # Save document
    doc.save(docx_path)

    return docx_path
