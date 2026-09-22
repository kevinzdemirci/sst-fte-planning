import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and display total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header on later pages
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 26, 8.5 * inch - 36, 11 * inch - 26)
            self.drawString(36, 11 * inch - 22, "SST Public Schools — Superintendent's Executive Weekly Briefing")
            self.drawRightString(8.5 * inch - 36, 11 * inch - 22, "August 26, 2026")

        # Footer on all pages
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 28, 8.5 * inch - 36, 28)
        self.drawString(36, 17, "CONFIDENTIAL — For SST Leadership & Executive Committee Use Only")
        self.drawRightString(8.5 * inch - 36, 17, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(filename="SST_Superintendent_Executive_Updates_8_26_2026.pdf"):
    pdf_path = os.path.join(os.path.dirname(__file__), filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Colors
    NAVY = colors.HexColor("#002B49")
    BLUE = colors.HexColor("#0284C7")
    DARK_BLUE = colors.HexColor("#003366")
    RED = colors.HexColor("#DC2626")
    SLATE_DARK = colors.HexColor("#0F172A")
    SLATE_BODY = colors.HexColor("#334155")
    SLATE_MUTED = colors.HexColor("#64748B")
    BG_LIGHT = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Typography styles
    styles.add(ParagraphStyle('DocHeaderTitle', fontName='Helvetica-Bold', fontSize=17, leading=21, textColor=colors.white))
    styles.add(ParagraphStyle('DocHeaderSubtitle', fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor("#94A3B8")))
    styles.add(ParagraphStyle('BrandTag', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=colors.HexColor("#93C5FD")))
    styles.add(ParagraphStyle('BrandTagSub', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor("#CBD5E1")))
    styles.add(ParagraphStyle('ConfidentialBar', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=RED))
    styles.add(ParagraphStyle('ConfidentialRight', fontName='Helvetica', fontSize=8, leading=10, textColor=SLATE_MUTED, alignment=2))
    styles.add(ParagraphStyle('DateBadge', fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=colors.white, alignment=2))

    styles.add(ParagraphStyle('SectionCategory', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=BLUE))
    styles.add(ParagraphStyle('SectionTitle', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=SLATE_DARK))
    styles.add(ParagraphStyle('BodyTextCustom', fontName='Helvetica', fontSize=8.5, leading=12, textColor=SLATE_BODY))
    styles.add(ParagraphStyle('BulletText', fontName='Helvetica', fontSize=8.5, leading=12, textColor=SLATE_BODY))
    styles.add(ParagraphStyle('HighlightHeader', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor("#0369A1")))
    
    styles.add(ParagraphStyle('ActionDesc', fontName='Helvetica', fontSize=8, leading=11, textColor=SLATE_BODY))

    styles.add(ParagraphStyle('CalMonth', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=RED, alignment=1))
    styles.add(ParagraphStyle('CalTitle', fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=SLATE_DARK, alignment=1))
    styles.add(ParagraphStyle('CalSub', fontName='Helvetica', fontSize=7, leading=9, textColor=SLATE_MUTED, alignment=1))

    styles.add(ParagraphStyle('FooterHeading', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white))
    styles.add(ParagraphStyle('FooterText', fontName='Helvetica', fontSize=7.5, leading=11, textColor=colors.HexColor("#CBD5E1")))

    story = []
    page_width = 8.5 * inch - 72 # 540 pt available width

    # 1. TOP BRAND ACCENT BAR
    accent_bar = Table([[""]], colWidths=[page_width], rowHeights=[4])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('PADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(accent_bar)

    # 2. CONFIDENTIALITY BAR
    conf_table = Table([
        [
            Paragraph("&bull; <b>CONFIDENTIAL &bull; EXECUTIVE &amp; CAMPUS LEADERSHIP BRIEFING</b>", styles['ConfidentialBar']),
            Paragraph("INTERNAL DISTRIBUTION ONLY", styles['ConfidentialRight'])
        ]
    ], colWidths=[page_width * 0.72, page_width * 0.28])
    conf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#FEE2E2")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(conf_table)

    # 3. HEADER BANNER
    header_content = [
        [
            Paragraph("<b>SCHOOL OF SCIENCE &amp; TECHNOLOGY</b>", styles['BrandTag']),
            Paragraph("<b>August 26, 2026</b>", styles['DateBadge'])
        ],
        [
            Paragraph("Better Education, Better Future", styles['BrandTagSub']),
            Paragraph("", styles['BrandTagSub'])
        ],
        [
            Paragraph("Superintendent's Weekly Executive Briefing", styles['DocHeaderTitle']),
            Paragraph("", styles['DocHeaderTitle'])
        ],
        [
            Paragraph("Recap of Executive Meeting Decisions, Operational Directives &amp; Campus Deadlines", styles['DocHeaderSubtitle']),
            Paragraph("", styles['DocHeaderSubtitle'])
        ]
    ]
    header_table = Table(header_content, colWidths=[page_width * 0.74, page_width * 0.26])
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (1, 0), 8),
        ('BOTTOMPADDING', (0, 3), (1, 3), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # 4. EXECUTIVE HIGHLIGHTS AT A GLANCE
    highlights_data = [
        [Paragraph("<b>EXECUTIVE HIGHLIGHTS AT A GLANCE</b>", styles['HighlightHeader'])],
        [Paragraph("• <b>Academic Accountability:</b> Domain 3 TELPAS deep-dive analysis underway; leadership support session scheduled.<br/>"
                   "• <b>T-PESS / T-TESS:</b> Appraiser certification rollout announced for Principals &amp; REDs; walkthrough deadlines set.<br/>"
                   "• <b>Operations &amp; Staffing:</b> Exploring Teacher Aide FTE for substitute coverage; standardized email signature rollout.<br/>"
                   "• <b>Enrollment Milestone:</b> 4 SST campuses surpassed the <b>800+ student</b> milestone!", styles['BulletText'])]
    ]
    highlights_box = Table(highlights_data, colWidths=[page_width])
    highlights_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('LINELEFT', (0, 0), (0, -1), 3.5, BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(highlights_box)
    story.append(Spacer(1, 8))

    # 5. IMMEDIATE ACTION ITEMS (CHECKLIST CARD)
    action_items_header = [
        [
            Paragraph("<b>IMMEDIATE ACTION ITEMS &amp; RESPONSIBILITIES</b>", ParagraphStyle('ActH', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
            Paragraph("REQUIRED ACTION", ParagraphStyle('ActBadge', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white, alignment=2))
        ]
    ]
    action_header_table = Table(action_items_header, colWidths=[page_width * 0.75, page_width * 0.25])
    action_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SLATE_DARK),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    def check_cell():
        c_tab = Table([["v"]], colWidths=[14], rowHeights=[14])
        c_tab.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#10B981")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#059669")),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 0),
        ]))
        return c_tab

    actions_body = [
        [
            check_cell(),
            Paragraph("<b>Register for T-PESS Appraiser Certification</b><br/>"
                      "<font color='#475569'>All Principals and REDs must register for in-person or online certification sessions.</font><br/>"
                      "<font color='#0369A1'><b>Owners:</b> REDs &amp; Principals</font> &nbsp;|&nbsp; <font color='#991B1B'><b>Due:</b> Earliest Fall Session</font>", styles['ActionDesc'])
        ],
        [
            check_cell(),
            Paragraph("<b>Implement Campus Academic Improvement Plans (ESF Self-Assessment)</b><br/>"
                      "<font color='#475569'>Identified campuses must build an ESF-aligned improvement plan with Regional Academics.</font><br/>"
                      "<font color='#0369A1'><b>Owners:</b> Principals &amp; RDAs</font> &nbsp;|&nbsp; <font color='#991B1B'><b>Due:</b> Thursday, September 10, 2026</font>", styles['ActionDesc'])
        ],
        [
            check_cell(),
            Paragraph("<b>T-TESS Phase 1 Walkthrough Form in DMAC</b><br/>"
                      "<font color='#475569'>Complete at least one Phase 1 Walkthrough form in DMAC for every teacher.</font><br/>"
                      "<font color='#0369A1'><b>Owners:</b> Campus Leadership Teams</font> &nbsp;|&nbsp; <font color='#991B1B'><b>Due:</b> Friday, September 4, 2026</font>", styles['ActionDesc'])
        ],
        [
            check_cell(),
            Paragraph("<b>Standardize Campus &amp; Staff Email Signatures</b><br/>"
                      "<font color='#475569'>Remove personal quotes; insert district values and standardized Assistant Principal titles.</font><br/>"
                      "<font color='#0369A1'><b>Owners:</b> All Staff &amp; Leadership</font> &nbsp;|&nbsp; <font color='#92400E'><b>Due:</b> Immediate</font>", styles['ActionDesc'])
        ]
    ]
    actions_body_table = Table(actions_body, colWidths=[20, page_width - 20])
    actions_body_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, BORDER_COLOR),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, BORDER_COLOR),
        ('LINEBELOW', (0, 2), (-1, 2), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(KeepTogether([action_header_table, actions_body_table]))
    story.append(Spacer(1, 8))

    # 6. SECTION: ACADEMICS & ACCOUNTABILITY
    sec1_data = [
        [Paragraph("<font color='#1D4ED8'><b>ACADEMICS &amp; ACCOUNTABILITY</b></font>", styles['SectionCategory'])],
        [Paragraph("Domain 3 — TELPAS Impact &amp; Campus Improvement Plans", styles['SectionTitle'])],
        [Paragraph(
            "The Executive Committee reviewed the district-created <b>Domain 3: Closing the Gaps dashboard</b>. Certain campuses scored 0/4 on the TELPAS (English Language Proficiency) component, requiring targeted intervention support.<br/><br/>"
            "• <b>Leadership Support Series:</b> Wednesday, Aug 26 (9:00 AM – 10:00 AM) to review dashboards and intervention strategies.<br/>"
            "• <b>ESF Self-Assessment:</b> Identified campuses will draft customized improvement plans supported by the Regional Director of Academics by <b>Thursday, September 10, 2026</b>.<br/><br/>"
            "<i>Attached Resources: '26 TELPAS Deep Dive, ESF Campus Self Assessment Tool (.xlsx), ESF Brochure (.pdf)</i>", styles['BodyTextCustom']
        )]
    ]
    sec1_table = Table(sec1_data, colWidths=[page_width])
    sec1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('LINELEFT', (0, 0), (0, -1), 3.5, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([sec1_table]))
    story.append(Spacer(1, 8))

    # 7. SECTION: LEADERSHIP & APPRAISALS (T-PESS / T-TESS)
    sec2_data = [
        [Paragraph("<font color='#92400E'><b>LEADERSHIP &amp; APPRAISALS</b></font>", styles['SectionCategory'])],
        [Paragraph("T-PESS &amp; T-TESS Evaluation Framework Rollout", styles['SectionTitle'])],
        [Paragraph(
            "T-PESS certification is mandatory for anyone conducting formal principal or assistant principal evaluations under the Enhanced TIA framework. REDs will evaluate Principals, and Principals evaluate Assistant Principals.<br/><br/>"
            "<b>Training Options:</b><br/>"
            "• <b>In-Person (ESC Region 20, San Antonio):</b> Sept 24, 2026 (#117104) &amp; Oct 22, 2026 (#117106)<br/>"
            "• <b>Online Options:</b> Region 4 ESC (Oct 28, 2026) &amp; Region 13 ESC (Jan 28, 2027)<br/><br/>"
            "<b>T-TESS Walkthroughs:</b> Complete Phase 1 DMAC walkthroughs for all teachers by <b>Sept 4</b>. 2nd semester observations will follow a semi-announced 2-week notification window.", styles['BodyTextCustom']
        )]
    ]
    sec2_table = Table(sec2_data, colWidths=[page_width])
    sec2_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('LINELEFT', (0, 0), (0, -1), 3.5, colors.HexColor("#F59E0B")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([sec2_table]))
    story.append(Spacer(1, 8))

    # 8. SECTION: OPERATIONS, STAFFING & POLICY
    sec3_data = [
        [Paragraph("<font color='#475569'><b>OPERATIONS &amp; POLICIES</b></font>", styles['SectionCategory'])],
        [Paragraph("Staffing, Title Alignment &amp; Email Signature Guidelines", styles['SectionTitle'])],
        [Paragraph(
            "• <b>Teacher Aide FTE Model:</b> Developing a plan to utilize dedicated Teacher Aide FTEs to mitigate daily substitute shortages. Guidance will be shared by Dr. Demirci and Talent Acquisition.<br/>"
            "• <b>Title Alignment:</b> Transitioning from 'Dean' to 'Assistant Principal' titles (e.g., <i>AP of Academics</i>, <i>AP of Discipline &amp; Safety</i>, <i>AP of CCMR</i>).<br/>"
            "• <b>Standardized Email Signatures:</b> All staff must update signatures with district/campus core values in place of personal quotes. Central office staff supporting shared agreements must use approved multi-logo signatures.<br/>"
            "&nbsp;&nbsp;<i>Sample Format:</i> <b>[Staff Name]</b> | [Title] | School of Science and Technology<br/>"
            "&nbsp;&nbsp;<i>Values:</i> Accountability, Citizenship, Dedication, Honesty, Integrity, Kindness, Leadership, Respectfulness, and Responsibility.", styles['BodyTextCustom']
        )]
    ]
    sec3_table = Table(sec3_data, colWidths=[page_width])
    sec3_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('LINELEFT', (0, 0), (0, -1), 3.5, colors.HexColor("#64748B")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([sec3_table]))
    story.append(Spacer(1, 8))

    # 9. TWO COLUMN: ENROLLMENT CELEBRATION & FUNDRAISING
    col_w = (page_width - 8) / 2
    card_kudos = Table([
        [Paragraph("<b>ENROLLMENT MILESTONE</b>", ParagraphStyle('KudoH', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.HexColor("#A7F3D0")))],
        [Paragraph("<b>800+ Students Club!</b>", ParagraphStyle('KudoB', fontName='Helvetica-Bold', fontSize=11, textColor=colors.white))],
        [Paragraph("Congratulations to:<br/>• SST Champions<br/>• SST Champions College Prep<br/>• SST Sugar Land College Prep<br/>• Compass Rose Ingenuity", ParagraphStyle('KudoList', fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=colors.HexColor("#ECFDF5")))]
    ], colWidths=[col_w])
    card_kudos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#047857")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    card_funds = Table([
        [Paragraph("<b>ATTENDANCE &amp; TRUST FUND</b>", ParagraphStyle('FundH', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.HexColor("#D97706")))],
        [Paragraph("<b>Fundraising &amp; Truancy</b>", ParagraphStyle('FundB', fontName='Helvetica-Bold', fontSize=10.5, textColor=SLATE_DARK))],
        [Paragraph("• <b>Attendance Tracking:</b> Daily monitoring resumes Sept 1st.<br/>• <b>Trust Fund Goals:</b> Campuses should review fundraising targets ahead of the fall campaign.", ParagraphStyle('FundList', fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=SLATE_BODY))]
    ], colWidths=[col_w])
    card_funds.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('LINELEFT', (0, 0), (0, -1), 3.5, colors.HexColor("#D97706")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    two_col_table = Table([[card_kudos, card_funds]], colWidths=[col_w, col_w])
    two_col_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(KeepTogether([two_col_table]))
    story.append(Spacer(1, 8))

    # 10. MARK YOUR CALENDAR (DATE TILES)
    cal_header = [Paragraph("<b>MARK YOUR CALENDAR: KEY UPCOMING DATES</b>", ParagraphStyle('CalH', fontName='Helvetica-Bold', fontSize=8, textColor=SLATE_DARK))]
    
    tile_w = (page_width - 18) / 4
    def make_tile(m, t, s, c):
        t_tab = Table([
            [Paragraph(m, ParagraphStyle('M', fontName='Helvetica-Bold', fontSize=7.5, textColor=c, alignment=1))],
            [Paragraph(t, styles['CalTitle'])],
            [Paragraph(s, styles['CalSub'])]
        ], colWidths=[tile_w])
        t_tab.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))
        return t_tab

    t1 = make_tile("SEPT 7", "Labor Day", "No School", RED)
    t2 = make_tile("SEPT 16–30", "Home Visits", "District Drive", BLUE)
    t3 = make_tile("OCT 12–13", "District PD", "Staff Training", BLUE)
    t4 = make_tile("OCT 14–16", "Fall Break", "All Campuses", colors.HexColor("#059669"))

    cal_tiles = Table([[t1, t2, t3, t4]], colWidths=[tile_w, tile_w, tile_w, tile_w])
    cal_tiles.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))

    cal_box = Table([
        cal_header,
        [cal_tiles]
    ], colWidths=[page_width])
    cal_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([cal_box]))
    story.append(Spacer(1, 8))

    # 11. RESOURCES & FOOTER
    footer_data = [
        [
            Paragraph("<b>From the Superintendent's Office &bull; SST Public Schools</b>", styles['FooterHeading']),
        ],
        [
            Paragraph("This executive briefing is compiled following weekly Executive Committee meetings.<br/>"
                      "<b>Editorial Team:</b> Maskat Altiyev (Chief of Staff) &bull; Annabelle Mendiola (Sr. Director) &bull; Anna Ruiz (Communications)<br/>"
                      "<b>Resource Archive:</b> Access weekly documents &amp; slide decks via the central Google Drive portal.", styles['FooterText'])
        ]
    ]
    footer_table = Table(footer_data, colWidths=[page_width])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([footer_table]))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully rebuilt PDF: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
