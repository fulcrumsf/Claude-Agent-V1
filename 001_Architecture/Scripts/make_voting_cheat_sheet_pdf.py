"""Generate Tony's single-page Wake County 2026 general election voting cheat sheet (ballot style B0144).

Content is exactly the choices Tony explicitly selected; nothing inferred or added.
Run with: /tmp/pdfvenv/bin/python 001_Architecture/Scripts/make_voting_cheat_sheet_pdf.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = "007_Resource_Library/Personal/Wake-County-2026-Personal-Voting-Cheat-Sheet-B0144.pdf"

pdfmetrics.registerFont(TTFont("Arial", "/System/Library/Fonts/Supplemental/Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial", boldItalic="Arial-Bold")

INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#555555")
LINE = colors.HexColor("#BBBBBB")
ACCENT = colors.HexColor("#0B3D6B")
PICK = colors.HexColor("#0A6B2E")

TITLE = ParagraphStyle("title", fontName="Arial-Bold", fontSize=17, leading=20,
                       alignment=TA_CENTER, textColor=ACCENT, spaceAfter=2)
SUB = ParagraphStyle("sub", fontName="Arial", fontSize=10.5, leading=13,
                     alignment=TA_CENTER, textColor=MUTED)
HEAD = ParagraphStyle("head", fontName="Arial-Bold", fontSize=11.5, leading=14,
                      textColor=ACCENT, spaceBefore=0, spaceAfter=4)
OFFICE = ParagraphStyle("office", fontName="Arial-Bold", fontSize=7.2, leading=8.6,
                        textColor=MUTED, spaceAfter=0)
PICKST = ParagraphStyle("pick", fontName="Arial-Bold", fontSize=11.8, leading=13.6,
                        textColor=PICK, spaceAfter=3.5)
NOTE = ParagraphStyle("note", fontName="Arial", fontSize=7.4, leading=9.2, textColor=MUTED)
FOOT = ParagraphStyle("foot", fontName="Arial", fontSize=7.6, leading=9.6,
                      alignment=TA_CENTER, textColor=MUTED)

# (number, office label, selected name(s)) -- exact user order
RACES = [
    ("1", "U.S. Senate", "Roy Cooper"),
    ("2", "U.S. House of Representatives — District 2", "Deborah K. Ross"),
    ("3", "N.C. Supreme Court — Associate Justice, Seat 1", "Anita Earls"),
    ("4", "N.C. Court of Appeals — Seat 1", "John S. Arrowood"),
    ("5", "N.C. Court of Appeals — Seat 2", "Tobias (Toby) Hampson"),
    ("6", "N.C. Court of Appeals — Seat 3", "Christine Marie Walczyk"),
    ("7", "N.C. Senate — District 13", "Lisa Grafstein"),
    ("8", "N.C. House of Representatives — District 33", "Monika Johnson-Hostler"),
    ("9", "N.C. District Court Judge — District 10E, Seat 1", "Ms. Sam Hamadani"),
    ("10", "N.C. District Court Judge — District 10E, Seat 2", "Louis Meyer"),
    ("11", "District Attorney — District 10", "Wiley Nickel"),
    ("12", "County Commissioner — At-Large (Vote for 2)", "Mona Singh and Christine Kushner"),
    ("13", "Clerk of Superior Court", "Claudia C. Croom"),
    ("14", "Sheriff", "Willie Rowe"),
    ("15", "Soil &amp; Water Conservation District Supervisor (Vote for 2)", "Samantha Krop and Cece Grant"),
]

AMENDMENTS = [
    ("AGAINST", "Expanded photo ID"),
    ("FOR", "Income tax cap 3.5%"),
    ("FOR", "Property tax limit"),
]

BONDS = [
    ("YES", "Wake County Public Schools, $680M"),
    ("YES", "Wake Tech, $149.1M"),
]


def races_block():
    flow = [Paragraph("MY SELECTIONS", HEAD)]
    rows = []
    for num, office, name in RACES:
        cell = [Paragraph(f"{num}. {office}", OFFICE), Paragraph(name, PICKST)]
        rows.append([cell])
    t = Table(rows, colWidths=[3.75 * inch])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flow.append(t)
    return flow


def ballot_block():
    flow = []
    flow.append(Paragraph("BALLOT MEASURES", HEAD))
    rows = []
    for stance, label in AMENDMENTS:
        rows.append([Paragraph(f"<b>{stance}</b>", PICKST), Paragraph(label, NOTE)])
    t = Table(rows, colWidths=[0.95 * inch, 2.85 * inch])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 10))

    flow.append(Paragraph("BONDS", HEAD))
    rows = []
    for stance, label in BONDS:
        rows.append([Paragraph(f"<b>{stance}</b>", PICKST), Paragraph(label, NOTE)])
    t2 = Table(rows, colWidths=[0.95 * inch, 2.85 * inch])
    t2.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flow.append(t2)
    return flow


def build():
    doc = SimpleDocTemplate(OUT, pagesize=letter,
                            leftMargin=0.55 * inch, rightMargin=0.55 * inch,
                            topMargin=0.45 * inch, bottomMargin=0.42 * inch,
                            title="Personal Voting Cheat Sheet — Not an Official Ballot",
                            author="Tony")
    story = [
        Paragraph("Personal Voting Cheat Sheet — Not an Official Ballot", TITLE),
        Paragraph("Wake County, NC &nbsp;·&nbsp; 2026 General Election &nbsp;·&nbsp; Ballot Style B0144", SUB),
        Spacer(1, 6),
    ]
    body = Table([[races_block(), ballot_block()]], colWidths=[3.85 * inch, 3.85 * inch])
    body.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 12),
        ("LEFTPADDING", (1, 0), (1, 0), 12),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("LINEBEFORE", (1, 0), (1, 0), 0.7, LINE),
    ]))
    story.append(body)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Personal reference only — not an official ballot. Bring your official sample ballot or use your "
        "county-issued ballot at the polls; verify every contest and measure before casting your vote.", FOOT))
    doc.build(story)


if __name__ == "__main__":
    build()
    print("Wrote", OUT)
