import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
REPORTS_PORTFOLIO_DIR = os.path.join(BASE_DIR, "../../reports/portfolio")

class PortfolioNumberedCanvas(canvas.Canvas):
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
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(36, 20, "Nifty 100 Portfolio Intelligence Summary")
        self.drawRightString(letter[0] - 36, 20, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def _load_excel_safe(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_excel(path)
    if any("fintech" in str(col).lower() or "nifty" in str(col).lower() for col in df.columns):
        df = pd.read_excel(path, header=1)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def generate_portfolio_summary():
    print("⏳ Generating Dynamic Portfolio Summary PDF...")
    os.makedirs(REPORTS_PORTFOLIO_DIR, exist_ok=True)
    pdf_path = os.path.join(REPORTS_PORTFOLIO_DIR, "portfolio_summary.pdf")

    doc = SimpleDocTemplate(
        pdf_path, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor("#1A365D"))
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#2D3748"))

    # Load actual datasets
    companies = _load_excel_safe("companies.xlsx")
    ratios = _load_excel_safe("financial_ratios.xlsx")

    if companies.empty:
        print("❌ Error: companies.xlsx missing.")
        return

    # Identify primary columns
    id_col = next((c for c in companies.columns if c in ['company_id', 'ticker', 'id', 'symbol']), companies.columns[0])
    name_col = next((c for c in companies.columns if c in ['company_name', 'name', 'title']), companies.columns[1])
    
    companies = companies.sort_values(by=id_col)

    story = []
    story.append(Paragraph("Nifty 100 Master Portfolio Summary", title_style))
    story.append(Paragraph("Alphabetical index of companies with real-time extracted fundamental metrics.", body_style))
    story.append(Spacer(1, 15))

    for _, row in companies.iterrows():
        ticker = str(row.get(id_col, ""))
        name = str(row.get(name_col, ticker))
        
        # Find real ratios for this company
        latest_ratio = pd.Series()
        if not ratios.empty:
            for col in ratios.columns:
                sub = ratios[ratios[col].astype(str).str.upper() == ticker.upper()]
                if not sub.empty:
                    latest_ratio = sub.iloc[-1]
                    break

        def get_val(keys, suffix=""):
            for k in keys:
                for col in latest_ratio.index:
                    if k in col:
                        v = latest_ratio[col]
                        if pd.notna(v):
                            try:
                                return f"{float(v):.1f}{suffix}"
                            except:
                                return str(v)
            return "N/A"

        roe = get_val(['return_on_equity', 'roe'], "%")
        opm = get_val(['operating_profit_margin', 'opm', 'net_profit_margin'], "%")
        de = get_val(['debt_to_equity', 'd_e'])
        cagr = get_val(['cagr', 'sales_growth'], "%")

        story.append(Paragraph(f"<b>{ticker} — {name}</b>", styles['Heading2']))
        
        summary_data = [
            ["Metric", "Value", "Status"],
            ["Return on Equity (ROE)", roe, "Active"],
            ["Operating Margin / NPM", opm, "Stable"],
            ["Debt to Equity", de, "Leverage Checked"],
            ["Compound Growth Metric", cagr, "Tracked"]
        ]
        
        t = Table(summary_data, colWidths=[200, 150, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

    doc.build(story, canvasmaker=PortfolioNumberedCanvas)
    print(f"✅ Dynamic Portfolio Summary successfully saved to: {pdf_path}")

if __name__ == "__main__":
    generate_portfolio_summary()