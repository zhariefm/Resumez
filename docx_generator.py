import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def add_bottom_border(paragraph):
    """Adds a crisp, thin black bottom border to a section header (Jake's Template style)."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = parse_xml(r'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                     r'<w:bottom w:val="single" w:sz="6" w:space="2" w:color="000000"/>'
                     r'</w:pBdr>')
    pPr.append(pBdr)


def create_jakes_resume_docx(resume_data: dict) -> io.BytesIO:
    """
    Builds the authentic 'Jake's Resume Template' in strict Black & White.
    Features:
    - 0.5-inch margins
    - Clean typography (Calibri / Arial)
    - Full-width uppercase section headers with thin bottom rule
    - Two-column metadata lines (Left: Company/Title, Right: Location/Dates)
    - High-impact bullet points with precise indenting
    - 100% Black and White (RGB 0,0,0)
    """
    doc = Document()

    # 0.5 inch margins for classic Jake's template single-page layout
    for section in doc.sections:
        section.top_margin = Inches(0.45)
        section.bottom_margin = Inches(0.45)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)

    COLOR_BLACK = RGBColor(0, 0, 0)
    FONT_NAME = "Calibri"

    def format_run(run, font_name=FONT_NAME, size_pt=10, bold=False, italic=False):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = COLOR_BLACK

    def add_section_header(title: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title.upper())
        format_run(run, size_pt=11, bold=True)
        add_bottom_border(p)

    def add_two_column_line(left_text: str, right_text: str, left_bold=True, right_bold=False, left_italic=False, right_italic=False, space_before=2, space_after=1):
        """Creates a clean two-column line without visible borders (Jake's template format)."""
        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Set widths (left 5.0 in, right 2.5 in)
        table.columns[0].width = Inches(5.0)
        table.columns[1].width = Inches(2.5)

        # Clear cell margins
        for cell in table.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcMar = parse_xml(r'<w:tcMar xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                              r'<w:top w:w="0" w:type="dxa"/>'
                              r'<w:bottom w:w="0" w:type="dxa"/>'
                              r'<w:left w:w="0" w:type="dxa"/>'
                              r'<w:right w:w="0" w:type="dxa"/>'
                              r'</w:tcMar>')
            tcPr.append(tcMar)

        p_left = table.rows[0].cells[0].paragraphs[0]
        p_left.paragraph_format.space_before = Pt(space_before)
        p_left.paragraph_format.space_after = Pt(space_after)
        p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_l = p_left.add_run(left_text)
        format_run(r_l, size_pt=10, bold=left_bold, italic=left_italic)

        p_right = table.rows[0].cells[1].paragraphs[0]
        p_right.paragraph_format.space_before = Pt(space_before)
        p_right.paragraph_format.space_after = Pt(space_after)
        p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_r = p_right.add_run(right_text)
        format_run(r_r, size_pt=10, bold=right_bold, italic=right_italic)

    # --- 1. HEADER (CENTERED NAME & CONTACT) ---
    personal = resume_data.get("personal_info", {})
    name = personal.get("name", "Student Name").strip()

    name_p = doc.add_paragraph()
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_p.paragraph_format.space_before = Pt(0)
    name_p.paragraph_format.space_after = Pt(2)
    name_run = name_p.add_run(name)
    format_run(name_run, size_pt=19, bold=True)

    # Contact line
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
        contact_p = doc.add_paragraph()
        contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_p.paragraph_format.space_before = Pt(0)
        contact_p.paragraph_format.space_after = Pt(6)
        c_run = contact_p.add_run("  |  ".join(contact_parts))
        format_run(c_run, size_pt=9.5)

    # --- SECTION RENDERERS ---
    def render_education():
        education_list = resume_data.get("education", [])
        if education_list:
            add_section_header("Education")
            for edu in education_list:
                inst = edu.get("institution", "")
                loc = edu.get("location", "")
                deg = edu.get("degree", "")
                dates = edu.get("dates", "")
                gpa = edu.get("gpa", "")

                add_two_column_line(inst, loc, left_bold=True, right_bold=False, space_before=2, space_after=0)
                deg_display = deg + (f"  (GPA: {gpa})" if gpa else "")
                add_two_column_line(deg_display, dates, left_bold=False, right_bold=False, left_italic=True, right_italic=True, space_before=0, space_after=1)

                cw = edu.get("relevant_coursework", [])
                if cw:
                    cw_p = doc.add_paragraph()
                    cw_p.paragraph_format.space_before = Pt(0)
                    cw_p.paragraph_format.space_after = Pt(2)
                    r_label = cw_p.add_run("Relevant Coursework: ")
                    format_run(r_label, size_pt=9.5, bold=True)
                    r_val = cw_p.add_run(", ".join(cw) if isinstance(cw, list) else str(cw))
                    format_run(r_val, size_pt=9.5)

    def render_experience():
        experiences = resume_data.get("experience", [])
        if experiences:
            add_section_header("Experience")
            for exp in experiences:
                role = exp.get("role", "")
                comp = exp.get("company", "")
                loc = exp.get("location", "")
                dates = exp.get("dates", "")

                add_two_column_line(role, dates, left_bold=True, right_bold=False, space_before=3, space_after=0)
                add_two_column_line(comp, loc, left_bold=False, right_bold=False, left_italic=True, right_italic=True, space_before=0, space_after=1)

                for bullet in exp.get("bullets", []):
                    b_p = doc.add_paragraph(style='List Bullet')
                    b_p.paragraph_format.space_before = Pt(1)
                    b_p.paragraph_format.space_after = Pt(1)
                    b_p.paragraph_format.line_spacing = 1.15
                    b_run = b_p.add_run(bullet)
                    format_run(b_run, size_pt=9.5)

    def render_projects():
        projects = resume_data.get("projects", [])
        if projects:
            add_section_header("Projects")
            for proj in projects:
                title = proj.get("title", "")
                tech = proj.get("tech_stack", "")
                dates = proj.get("dates", "")

                left_proj = f"{title}"
                if tech:
                    left_proj += f"  |  {tech}"

                add_two_column_line(left_proj, dates, left_bold=True, right_bold=False, space_before=3, space_after=1)

                for bullet in proj.get("bullets", []):
                    b_p = doc.add_paragraph(style='List Bullet')
                    b_p.paragraph_format.space_before = Pt(1)
                    b_p.paragraph_format.space_after = Pt(1)
                    b_p.paragraph_format.line_spacing = 1.15
                    b_run = b_p.add_run(bullet)
                    format_run(b_run, size_pt=9.5)

    def render_skills():
        skills = resume_data.get("skills", {})
        if skills:
            add_section_header("Technical Skills")
            if isinstance(skills, dict):
                for category, items in skills.items():
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
                    cat_run = p.add_run(f"{category}: ")
                    format_run(cat_run, size_pt=9.5, bold=True)
                    items_str = ", ".join(items) if isinstance(items, list) else str(items)
                    items_run = p.add_run(items_str)
                    format_run(items_run, size_pt=9.5)
            elif isinstance(skills, list):
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                items_run = p.add_run(", ".join(skills))
                format_run(items_run, size_pt=9.5)

    def render_certs():
        certs = resume_data.get("certifications_or_awards", [])
        if certs:
            add_section_header("Honors & Certifications")
            for cert in certs:
                c_p = doc.add_paragraph(style='List Bullet')
                c_p.paragraph_format.space_before = Pt(1)
                c_p.paragraph_format.space_after = Pt(1)
                c_run = c_p.add_run(cert if isinstance(cert, str) else str(cert))
                format_run(c_run, size_pt=9.5)

    career_level = resume_data.get("career_level", "student")
    if career_level == "experienced":
        render_experience()
        render_projects()
        render_skills()
        render_education()
        render_certs()
    else:
        render_education()
        render_experience()
        render_projects()
        render_skills()
        render_certs()

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def create_application_letter_docx(resume_data: dict) -> io.BytesIO:
    """
    Builds a matching professional Application Letter (Cover Letter) in Black & White.
    """
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    COLOR_BLACK = RGBColor(0, 0, 0)
    FONT_NAME = "Calibri"

    def format_run(run, size_pt=10.5, bold=False, italic=False):
        run.font.name = FONT_NAME
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = COLOR_BLACK

    personal = resume_data.get("personal_info", {})
    name = personal.get("name", "Student Name").strip()
    email = personal.get("email", "").strip()
    phone = personal.get("phone", "").strip()
    loc = personal.get("location", "").strip()

    letter_data = resume_data.get("application_letter", {})
    company = letter_data.get("company", "Target Employer")
    role = letter_data.get("role", "Target Position")
    recipient = letter_data.get("recipient", "Hiring Team")

    # Header: Candidate Contact
    name_p = doc.add_paragraph()
    name_p.paragraph_format.space_before = Pt(0)
    name_p.paragraph_format.space_after = Pt(2)
    r_name = name_p.add_run(name)
    format_run(r_name, size_pt=16, bold=True)

    contact_parts = [p for p in [phone, email, loc] if p]
    if contact_parts:
        c_p = doc.add_paragraph()
        c_p.paragraph_format.space_after = Pt(14)
        r_c = c_p.add_run("  |  ".join(contact_parts))
        format_run(r_c, size_pt=10)

    # Date
    date_p = doc.add_paragraph()
    date_p.paragraph_format.space_after = Pt(12)
    r_date = date_p.add_run(letter_data.get("date", "Current Date"))
    format_run(r_date, size_pt=10)

    # Recipient
    rec_p = doc.add_paragraph()
    rec_p.paragraph_format.space_after = Pt(14)
    r_rec = rec_p.add_run(f"To the {recipient}\n{company}")
    format_run(r_rec, size_pt=10.5, bold=True)

    # Subject Line
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(12)
    r_sub = sub_p.add_run(f"RE: Application for {role}")
    format_run(r_sub, size_pt=11, bold=True)

    # Salutation
    sal_p = doc.add_paragraph()
    sal_p.paragraph_format.space_after = Pt(10)
    r_sal = sal_p.add_run(f"Dear {recipient} at {company},")
    format_run(r_sal, size_pt=10.5)

    # Paragraphs
    paragraphs = [
        letter_data.get("opening", ""),
        letter_data.get("body_paragraph_1", ""),
        letter_data.get("body_paragraph_2", ""),
        letter_data.get("closing", "")
    ]

    for para in paragraphs:
        if para and para.strip():
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.2
            r = p.add_run(para.strip())
            format_run(r, size_pt=10.5)

    # Sign-off
    sign_p = doc.add_paragraph()
    sign_p.paragraph_format.space_before = Pt(12)
    sign_p.paragraph_format.space_after = Pt(2)
    r_sign = sign_p.add_run("Sincerely,")
    format_run(r_sign, size_pt=10.5)

    name_sign_p = doc.add_paragraph()
    name_sign_p.paragraph_format.space_before = Pt(14)
    r_n = name_sign_p.add_run(name)
    format_run(r_n, size_pt=11, bold=True)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
