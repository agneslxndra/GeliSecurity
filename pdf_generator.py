from io import BytesIO
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Preformatted
)


BRAND_DARK = colors.HexColor("#111827")
BRAND_BLUE = colors.HexColor("#2563EB")
BRAND_LIGHT = colors.HexColor("#EFF6FF")
TEXT_DARK = colors.HexColor("#1F2937")
BORDER = colors.HexColor("#D1D5DB")
CODE_BG = colors.HexColor("#F3F4F6")


def clean_text(text):
    if text is None:
        return "-"

    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("\n", "<br/>")

    # markdown bold **text** -> <b>text</b>
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    # markdown inline code `text` -> monospace-ish bold
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)

    return text


def get_severity_color(severity):
    severity = str(severity).lower()

    if severity == "critical":
        return colors.HexColor("#DC2626")
    if severity == "high":
        return colors.HexColor("#EA580C")
    if severity == "medium":
        return colors.HexColor("#D97706")
    if severity == "low":
        return colors.HexColor("#16A34A")

    return colors.HexColor("#6B7280")


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    page_text = f"GeliSecure | Page {doc.page}"
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, page_text)
    canvas.restoreState()


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#DBEAFE"),
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=20,
        textColor=BRAND_BLUE,
        spaceBefore=14,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=7
    ))

    styles.add(ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4B5563")
    ))

    styles.add(ParagraphStyle(
        name="CustomBullet",
        parent=styles["BodyText"],
        fontSize=9.2,
        leading=13,
        leftIndent=14,
        firstLineIndent=-8,
        textColor=TEXT_DARK,
        spaceAfter=5
    ))

    return styles


def add_cover(story, styles, selected):
    severity = selected["Severity"]
    severity_color = get_severity_color(severity)

    cover_table = Table(
        [
            [Paragraph("GeliSecure", styles["CoverTitle"])],
            [Paragraph("AI-Powered Vulnerability Remediation Report", styles["CoverSubtitle"])]
        ],
        colWidths=[17 * cm],
        rowHeights=[1.2 * cm, 0.8 * cm]
    )

    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_DARK),
        ("BOX", (0, 0), (-1, -1), 0.5, BRAND_DARK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
    ]))

    story.append(cover_table)
    story.append(Spacer(1, 18))

    badge = Table(
        [[Paragraph(f"<b>{severity}</b>", styles["Body"])]],
        colWidths=[4 * cm]
    )
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), severity_color),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, severity_color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(badge)
    story.append(Spacer(1, 12))

    summary_data = [
        ["Application", clean_text(selected["Application"])],
        ["Finding", clean_text(selected["Finding"])],
        ["Severity", clean_text(selected["Severity"])],
        ["Risk Score", clean_text(selected.get("Score", "-"))],
        ["Status", clean_text(selected["Status"])],
        ["Affected URL", clean_text(selected["Affected URL"])],
        ["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]

    table = Table(summary_data, colWidths=[4 * cm, 12.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BRAND_LIGHT),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_DARK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(table)
    story.append(Spacer(1, 16))


def add_section_box(story, styles, title, content):
    story.append(Paragraph(title, styles["SectionTitle"]))

    box_style = ParagraphStyle(
        name=f"BoxStyle_{title.replace(' ', '_')}",
        parent=styles["Body"],
        backColor=colors.HexColor("#F9FAFB"),
        borderColor=BORDER,
        borderWidth=0.5,
        borderPadding=8,
        spaceAfter=8
    )

    text = clean_text(content)

    # pecah konten panjang supaya tidak jadi 1 flowable terlalu tinggi
    chunks = []
    plain_text = str(content) if content is not None else "-"

    max_chars = 1200
    for i in range(0, len(plain_text), max_chars):
        chunks.append(plain_text[i:i + max_chars])

    for chunk in chunks:
        story.append(Paragraph(clean_text(chunk), box_style))
        story.append(Spacer(1, 4))

def add_code_block(story, styles, code):
    code = str(code).strip()
    code = code.replace("\t", "    ")

    code_style = ParagraphStyle(
        name="CodeStyleSafe",
        fontName="Courier",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#111827"),
        backColor=CODE_BG,
        borderColor=colors.HexColor("#CBD5E1"),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    # wrap line panjang biar nggak keluar halaman
    wrapped_lines = []
    max_chars = 88

    for line in code.splitlines():
        if len(line) <= max_chars:
            wrapped_lines.append(line)
        else:
            for i in range(0, len(line), max_chars):
                wrapped_lines.append(line[i:i + max_chars])

    # ini bagian penting:
    # code panjang dipecah per 35 baris supaya tidak jadi 1 flowable raksasa
    chunk_size = 35

    for i in range(0, len(wrapped_lines), chunk_size):
        chunk = "\n".join(wrapped_lines[i:i + chunk_size])

        story.append(Preformatted(chunk, code_style))
        story.append(Spacer(1, 4))


def add_markdown_content(story, styles, markdown_text):
    if not markdown_text:
        story.append(Paragraph("-", styles["Body"]))
        return

    lines = str(markdown_text).splitlines()
    in_code = False
    code_lines = []
    paragraph_buffer = []

    def flush_paragraph():
        if paragraph_buffer:
            text = " ".join(paragraph_buffer).strip()
            if text:
                story.append(Paragraph(clean_text(text), styles["Body"]))
            paragraph_buffer.clear()

    for line in lines:
        raw = line.rstrip()
        stripped = raw.strip()

        if stripped.startswith("```"):
            if not in_code:
                flush_paragraph()
                in_code = True
                code_lines = []
            else:
                in_code = False
                add_code_block(story, styles, "\n".join(code_lines))
                code_lines = []
            continue

        if in_code:
            code_lines.append(raw)
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            title = stripped.replace("## ", "", 1)
            story.append(Paragraph(title, styles["SectionTitle"]))
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            title = stripped.replace("# ", "", 1)
            story.append(Paragraph(title, styles["SectionTitle"]))
            continue

        if stripped.startswith("* ") or stripped.startswith("- "):
            flush_paragraph()
            bullet_text = stripped[2:].strip()
            story.append(Paragraph(f"• {clean_text(bullet_text)}", styles["CustomBullet"]))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            story.append(Paragraph(clean_text(stripped), styles["CustomBullet"]))
            continue


        if stripped == "":
            flush_paragraph()
            story.append(Spacer(1, 4))
            continue

        paragraph_buffer.append(stripped)

    flush_paragraph()

    if in_code and code_lines:
        add_code_block(story, styles, "\n".join(code_lines))


def generate_pdf_report(selected):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm
    )

    styles = build_styles()
    story = []

    add_cover(story, styles, selected)

    add_section_box(story, styles, "Finding Description", selected["Description"])
    add_section_box(story, styles, "Evidence", selected["Evidence"])

    story.append(PageBreak())

    story.append(Paragraph("AI Remediation Analysis", styles["SectionTitle"]))
    story.append(Paragraph(
        "Generated by GeliSecure AI Engine. The content below is intended to help developers understand, prioritize, fix, and retest the vulnerability.",
        styles["Small"]
    ))
    story.append(Spacer(1, 10))

    add_markdown_content(story, styles, selected["AI Result"])

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def add_autofix_cover(story, styles, data):
    severity = data.get("Severity", "-")
    severity_color = get_severity_color(severity)

    cover_table = Table(
        [
            [Paragraph("GeliSecure", styles["CoverTitle"])],
            [Paragraph("AI-Powered AutoFix Security Report", styles["CoverSubtitle"])]
        ],
        colWidths=[17 * cm],
        rowHeights=[1.2 * cm, 0.8 * cm]
    )

    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_DARK),
        ("BOX", (0, 0), (-1, -1), 0.5, BRAND_DARK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
    ]))

    story.append(cover_table)
    story.append(Spacer(1, 18))

    badge = Table(
        [[Paragraph(f"<b>{severity}</b>", styles["Body"])]],
        colWidths=[4 * cm]
    )

    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), severity_color),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, severity_color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(badge)
    story.append(Spacer(1, 12))

    summary_data = [
        ["Finding Title", clean_text(data.get("Finding Title", "-"))],
        ["Severity", clean_text(data.get("Severity", "-"))],
        ["Programming Language", clean_text(data.get("Language", "-"))],
        ["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]

    table = Table(summary_data, colWidths=[4.5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BRAND_LIGHT),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_DARK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(table)
    story.append(Spacer(1, 16))


def generate_autofix_pdf_report(data):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm
    )

    styles = build_styles()
    story = []

    add_autofix_cover(story, styles, data)

    add_section_box(
        story,
        styles,
        "Original Vulnerable Code",
        data.get("Vulnerable Code", "-")
    )

    story.append(PageBreak())

    story.append(Paragraph("AI AutoFix Analysis", styles["SectionTitle"]))
    story.append(Paragraph(
        "Generated by GeliSecure AutoFix Engine. The content below provides a safer code suggestion, security improvement explanation, and retesting guidance.",
        styles["Small"]
    ))
    story.append(Spacer(1, 10))

    add_markdown_content(story, styles, data.get("AutoFix Result", "-"))

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    pdf = buffer.getvalue()
    buffer.close()

    return pdf