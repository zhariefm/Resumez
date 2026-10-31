import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def create_jakes_resume_pdf(resume_data: dict) -> io.BytesIO:
    """
    Builds the authentic 'Jake's Resume Template' directly in PDF.
    Features:
    - 0.45 inch margins
    - Strict ATS-compliant Black & White (RGB 0,0,0)
    - Full-width uppercase section headers with clean black horizontal rules
    - Two-column metadata rows
    - Indented bullets
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=32,
        rightMargin=32,
        topMargin=28,
        bottomMargin=28
    )

    styles = getSampleStyleSheet()

    # Base typography (Helvetica standard for pure ATS compatibility)
    name_style = ParagraphStyle(
        'JakeName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=21,
        alignment=1,  # Centered
        textColor=colors.black
    )

    contact_style = ParagraphStyle(
        'JakeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.black
    )

    header_style = ParagraphStyle(
        'JakeHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.black,
        spaceBefore=7,
        spaceAfter=2
    )

    left_bold = ParagraphStyle(
        'LeftBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.black
    )

    left_italic = ParagraphStyle(
        'LeftItalic',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=11.5,
        textColor=colors.black
    )

    right_text = ParagraphStyle(
        'RightText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11.5,
        alignment=2,  # Right-aligned
        textColor=colors.black
    )

    right_italic = ParagraphStyle(
        'RightItalic',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        alignment=2,
        textColor=colors.black
    )

    bullet_style = ParagraphStyle(
        'JakeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        leftIndent=14,
        textColor=colors.black,
        spaceAfter=1
    )

    cw_style = ParagraphStyle(
        'JakeCoursework',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
        spaceBefore=1,
        spaceAfter=2
    )

    elements = []

    # --- 1. HEADER (NAME & CONTACT) ---
    personal = resume_data.get("personal_info", {})
    name = personal.get("name", "Student Name").strip()
    elements.append(Paragraph(name, name_style))
    elements.append(Spacer(1, 2))

    contact_parts = []
    if personal.get("phone"):
        contact_parts.append(personal["phone"].strip())
    if personal.get("email"):
        contact_parts.append(personal["email"].strip())
    if personal.get("linkedin"):
        contact_parts.append(personal["linkedin"].strip())
    if personal.get("github"):
        contact_parts.append(personal["github"].strip())
    if personal.get("portfolio"):
        contact_parts.append(personal["portfolio"].strip())

    if contact_parts:
        elements.append(Paragraph(" | ".join(contact_parts), contact_style))
        elements.append(Spacer(1, 4))

    def add_section(title: str):
        elements.append(Paragraph(title.upper(), header_style))
        elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceBefore=1, spaceAfter=4))

    # --- 2. EDUCATION ---
    education_list = resume_data.get("education", [])
    if education_list:
        add_section("Education")
        for edu in education_list:
            inst = edu.get("institution", "")
            loc = edu.get("location", "")
            deg = edu.get("degree", "")
            dates = edu.get("dates", "")
            gpa = edu.get("gpa", "")

            # Line 1: Institution | Location
            row1 = [[Paragraph(inst, left_bold), Paragraph(loc, right_text)]]
            t1 = Table(row1, colWidths=[380, 168])
            t1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)]))
            elements.append(t1)

            # Line 2: Degree | Dates
            deg_display = deg + (f" (GPA: {gpa})" if gpa else "")
            row2 = [[Paragraph(deg_display, left_italic), Paragraph(dates, right_italic)]]
            t2 = Table(row2, colWidths=[380, 168])
            t2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)]))
            elements.append(t2)

            cw = edu.get("relevant_coursework", [])
            if cw:
                cw_str = ", ".join(cw) if isinstance(cw, list) else str(cw)
                elements.append(Paragraph(f"<b>Relevant Coursework:</b> {cw_str}", cw_style))

    # --- 3. EXPERIENCE ---
    experiences = resume_data.get("experience", [])
    if experiences:
        add_section("Experience")
        for exp in experiences:
            role = exp.get("role", "")
            comp = exp.get("company", "")
            loc = exp.get("location", "")
            dates = exp.get("dates", "")

            row1 = [[Paragraph(f"<b>{role}</b>", left_bold), Paragraph(dates, right_text)]]
            t1 = Table(row1, colWidths=[380, 168])
            t1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)]))
            elements.append(t1)

            row2 = [[Paragraph(comp, left_italic), Paragraph(loc, right_italic)]]
            t2 = Table(row2, colWidths=[380, 168])
            t2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)]))
            elements.append(t2)

            for bullet in exp.get("bullets", []):
                elements.append(Paragraph(f"• {bullet}", bullet_style))

    # --- 4. PROJECTS ---
    projects = resume_data.get("projects", [])
    if projects:
        add_section("Projects")
        for proj in projects:
            title = proj.get("title", "")
            tech = proj.get("tech_stack", "")
            dates = proj.get("dates", "")
            title_line = f"<b>{title}</b>" + (f" | <i>{tech}</i>" if tech else "")

            row = [[Paragraph(title_line, left_bold), Paragraph(dates, right_text)]]
            t = Table(row, colWidths=[380, 168])
            t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)]))
            elements.append(t)

            for bullet in proj.get("bullets", []):
                elements.append(Paragraph(f"• {bullet}", bullet_style))

    # --- 5. TECHNICAL SKILLS ---
    skills = resume_data.get("skills", {})
    if skills:
        add_section("Technical Skills")
        if isinstance(skills, dict):
            for cat, items in skills.items():
                items_str = ", ".join(items) if isinstance(items, list) else str(items)
                elements.append(Paragraph(f"<b>{cat}:</b> {items_str}", bullet_style))
        elif isinstance(skills, list):
            elements.append(Paragraph(f"<b>Skills:</b> {', '.join(skills)}", bullet_style))

    # --- 6. HONORS / AWARDS ---
    certs = resume_data.get("certifications_or_awards", [])
    if certs:
        add_section("Honors & Certifications")
        for cert in certs:
            elements.append(Paragraph(f"• {cert if isinstance(cert, str) else str(cert)}", bullet_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def create_application_letter_pdf(resume_data: dict) -> io.BytesIO:
    """
    Builds the tailored Application Letter (Cover Letter) in PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle('LetterName', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18)
    contact_style = ParagraphStyle('LetterContact', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor('#475569'))
    body_style = ParagraphStyle('LetterBody', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, spaceAfter=10)
    bold_style = ParagraphStyle('LetterBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, spaceAfter=8)

    personal = resume_data.get("personal_info", {})
    name = personal.get("name", "Student Name").strip()
    email = personal.get("email", "").strip()
    phone = personal.get("phone", "").strip()
    loc = personal.get("location", "").strip()

    letter_data = resume_data.get("application_letter", {})
    company = letter_data.get("company", "Target Employer")
    role = letter_data.get("role", "Target Position")
    recipient = letter_data.get("recipient", "Hiring Team")

    elements = [
        Paragraph(name, name_style),
        Paragraph(" | ".join([p for p in [phone, email, loc] if p]), contact_style),
        Spacer(1, 14),
        Paragraph(letter_data.get("date", "October 31, 2026"), body_style),
        Spacer(1, 4),
        Paragraph(f"<b>To:</b> {recipient}<br/><b>Company:</b> {company}", body_style),
        Spacer(1, 4),
        Paragraph(f"<b>Subject: Application for {role}</b>", bold_style),
        Spacer(1, 6),
        Paragraph(f"Dear {recipient} at {company},", body_style),
        Paragraph(letter_data.get("opening", ""), body_style),
        Paragraph(letter_data.get("body_paragraph_1", ""), body_style),
        Paragraph(letter_data.get("body_paragraph_2", ""), body_style),
        Paragraph(letter_data.get("closing", ""), body_style),
        Spacer(1, 8),
        Paragraph("Sincerely,<br/><b>" + name + "</b>", body_style)
    ]

    doc.build(elements)
    buffer.seek(0)
    return buffer

