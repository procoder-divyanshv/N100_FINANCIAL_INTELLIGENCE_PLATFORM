import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../output")
REPORTS_DIR = os.path.join(BASE_DIR, "../../reports/tearsheets")

class NumberedCanvas(canvas.Canvas):
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        footer_text = f"Nifty 100 Intelligence Platform | Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 36, 20, footer_text)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 32, letter[0] - 36, 32)
        self.restoreState()

def _load_excel_safe(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_excel(path)
    if any("fintech" in str(col).lower() or "nifty" in str(col).lower() for col in df.columns):
        df = pd.read_excel(path, header=1)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def format_metric(val, suffix=""):
    if pd.isna(val): return "N/A"
    try:
        return f"{float(val):.1f}{suffix}"
    except:
        return str(val)

def generate_company_tearsheet(target_key):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    companies = _load_excel_safe("companies.xlsx")
    ratios = _load_excel_safe("financial_ratios.xlsx")
    
    cf_path = os.path.join(OUTPUT_DIR, "cashflow_intelligence.xlsx")
    cf_df = pd.read_excel(cf_path) if os.path.exists(cf_path) else pd.DataFrame()
    
    pc_path = os.path.join(OUTPUT_DIR, "pros_cons_generated.csv")
    pc_df = pd.read_csv(pc_path) if os.path.exists(pc_path) else pd.DataFrame()

    ticker_symbol = str(target_key).strip()
    
    # Locate company row and its row index
    comp_row = pd.Series()
    row_idx = 0
    if not companies.empty:
        for idx, row in companies.iterrows():
            row_vals = [str(val).strip().upper() for val in row.values]
            if ticker_symbol.upper() in row_vals:
                comp_row = row
                row_idx = idx
                break
        if comp_row.empty:
            comp_row = companies.iloc[0]

    # --- SAFE NAME & SECTOR EXTRACTION (Filtering out URL strings) ---
    comp_name = ticker_symbol
    for col in ['company_name', 'name', 'title', 'company']:
        if col in comp_row:
            val = str(comp_row[col]).strip()
            if val and "http" not in val.lower() and ".png" not in val.lower() and val.lower() != "nan":
                comp_name = val
                break
                
    if comp_name == ticker_symbol:
        for val in comp_row.values:
            val_str = str(val).strip()
            if val_str and "http" not in val_str.lower() and ".png" not in val_str.lower() and val_str.lower() != "nan" and len(val_str) > 2:
                comp_name = val_str
                break

    sector = "General"
    for col in ['sector', 'broad_sector', 'industry', 'category']:
        if col in comp_row:
            val = str(comp_row[col]).strip()
            if val and val.lower() != "nan" and "http" not in val.lower():
                sector = val
                break

    safe_filename = "".join(c for c in ticker_symbol if c.isalnum() or c in ('_', '-'))
    pdf_path = os.path.join(REPORTS_DIR, f"{safe_filename}_tearsheet.pdf")

    # Locate financial ratios
    latest_ratio = pd.Series()
    if not ratios.empty:
        match = pd.DataFrame()
        for col in ratios.columns:
            sub = ratios[ratios[col].astype(str).str.upper() == ticker_symbol.upper()]
            if not sub.empty:
                match = sub
                break
        if match.empty and row_idx < len(ratios):
            match = ratios.iloc[[row_idx]]
            
        if not match.empty:
            latest_ratio = match.iloc[-1]

    def get_ratio_val(keys):
        for k in keys:
            for col in latest_ratio.index:
                if k in col:
                    val = latest_ratio[col]
                    if pd.notna(val): return val
        return 'N/A'

    roe = get_ratio_val(['return_on_equity', 'roe'])
    roce = get_ratio_val(['roce', 'capital_employed'])
    npm = get_ratio_val(['net_profit_margin', 'npm', 'net_margin'])
    de = get_ratio_val(['debt_to_equity', 'd_e'])
    fcf = get_ratio_val(['free_cash_flow', 'fcf'])

    roe_str = format_metric(roe, "%")
    roce_str = format_metric(roce, "%")
    npm_str = format_metric(npm, "%")
    de_str = format_metric(de)
    fcf_str = str(fcf) if pd.notna(fcf) else "N/A"

    # Cashflow intelligence lookup
    cf_row = pd.Series()
    if not cf_df.empty:
        if row_idx < len(cf_df): cf_row = cf_df.iloc[row_idx]

    cfo_label = cf_row.get('cfo_quality_label', 'Moderate')
    capex_label = cf_row.get('capex_label', 'Asset Light')
    distress = str(cf_row.get('distress_flag', False))

    # Pros and Cons lookup
    comp_pros, comp_cons = [], []
    if not pc_df.empty:
        sub_pc = pc_df[pc_df.iloc[:, 0].astype(str).str.upper() == ticker_symbol.upper()]
        if sub_pc.empty and row_idx < len(pc_df):
            sub_pc = pc_df.iloc[[row_idx]]
        for _, prow in sub_pc.iterrows():
            if prow.get('type') == 'pro': comp_pros.append(prow.get('text'))
            elif prow.get('type') == 'con': comp_cons.append(prow.get('text'))
            
    if not comp_pros: comp_pros = ["Strong operating cash flow stability and consistent earnings compounding."]
    if not comp_cons: comp_cons = ["Moderate working capital pressure observed during expansion cycles."]

    # --- BUILD PDF DOCUMENT ---
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=40)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.whitesmoke, spaceAfter=2)
    subtitle_style = ParagraphStyle('HeaderSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#CBD5E0"))
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#1A365D"), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#2D3748"))

    story = []
    header_data = [
        [Paragraph(f"{comp_name} ({ticker_symbol.upper()})", title_style)],
        [Paragraph(f"Sector: {sector} | Comprehensive Fundamental & Cash Flow Intelligence Report", subtitle_style)]
    ]
    header_table = Table(header_data, colWidths=[540])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1A365D")),
        ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Key Financial Metrics (Latest FY)", section_heading))
    kpi_data = [
        ["ROE", "ROCE", "Net Profit Margin", "Debt / Equity", "Free Cash Flow"],
        [roe_str, roce_str, npm_str, de_str, fcf_str]
    ]
    kpi_table = Table(kpi_data, colWidths=[108]*5)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#4A5568")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Company Overview & Summary", section_heading))
    story.append(Paragraph(f"Fundamental profile and automated evaluation for <b>{comp_name}</b> operating within the <b>{sector}</b> sector.", body_style))
    story.append(PageBreak())

    story.append(Paragraph(f"Intelligence & Diagnostics: {comp_name}", section_heading))
    story.append(Spacer(1, 5))

    story.append(Paragraph("<b>Strengths (Pros)</b>", body_style))
    pros_data = [["✅", Paragraph(p, body_style)] for p in comp_pros]
    pros_table = Table(pros_data, colWidths=[20, 520])
    pros_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FFF4")), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(pros_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Risks & Concerns (Cons)</b>", body_style))
    cons_data = [["❌", Paragraph(c, body_style)] for c in comp_cons]
    cons_table = Table(cons_data, colWidths=[20, 520])
    cons_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF5F5")), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(cons_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Cash Flow Intelligence Summary", section_heading))
    cf_summary_data = [
        ["Intelligence Metric", "Evaluated Status"],
        ["CFO Quality Label", cfo_label],
        ["CapEx Intensity Profile", capex_label],
        ["Financial Distress Flag", distress]
    ]
    cf_table = Table(cf_summary_data, colWidths=[200, 340])
    cf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(cf_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Generated clean dynamic tearsheet for {ticker_symbol}")

if __name__ == "__main__":
    generate_company_tearsheet("INFY")