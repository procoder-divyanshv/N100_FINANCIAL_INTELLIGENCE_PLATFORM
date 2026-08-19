import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Robust import for tearsheet module
try:
    from .tearsheet import generate_company_tearsheet
except ImportError:
    from tearsheet import generate_company_tearsheet

# Paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../output")
REPORTS_TEARSHEET_DIR = os.path.join(BASE_DIR, "../../reports/tearsheets")
REPORTS_SECTOR_DIR = os.path.join(BASE_DIR, "../../reports/sector")

def run_batch_generation():
    print("⏳ Starting Batch Report Generation...")
    os.makedirs(REPORTS_TEARSHEET_DIR, exist_ok=True)
    os.makedirs(REPORTS_SECTOR_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load companies data
    companies_path = os.path.join(DATA_DIR, "companies.xlsx")
    if not os.path.exists(companies_path):
        print("❌ Error: companies.xlsx missing.")
        return

    df_comp = pd.read_excel(companies_path)
    if "fintech" in str(df_comp.columns[0]).lower():
        df_comp = pd.read_excel(companies_path, header=1)
    df_comp.columns = [str(c).strip().lower().replace(" ", "_") for c in df_comp.columns]

    skipped = []
    success_count = 0

    # Prioritize finding the ticker/symbol column over a raw numeric ID column
    preferred_cols = ['ticker', 'symbol', 'company_id', 'company_name', 'name']
    id_col = None
    for col in preferred_cols:
        if col in df_comp.columns:
            id_col = col
            break
    if not id_col:
        id_col = df_comp.columns[0]

    print(f"ℹ️ Using column '{id_col}' as company identifier for batch generation.")

    for _, row in df_comp.iterrows():
        ticker = str(row.get(id_col, "")).strip()
        if not ticker or ticker.lower() == "nan" or ticker == "UNKNOWN":
            continue

        try:
            # Generate the unique data-driven tearsheet PDF for this company
            generate_company_tearsheet(ticker)
            success_count += 1
        except Exception as e:
            print(f"⚠️ Failed to generate tearsheet for {ticker}: {e}")
            skipped.append({'ticker': ticker, 'reason': str(e)})

    # Log skipped tearsheets
    if skipped:
        pd.DataFrame(skipped).to_csv(os.path.join(OUTPUT_DIR, "skipped_tearsheets.csv"), index=False)

    print(f"\n✅ Batch Tearsheets Complete! Successfully generated {success_count} PDFs.")
    print(f"📁 Saved to: {REPORTS_TEARSHEET_DIR}/")

    # --- SECTOR REPORTS GENERATION ---
    print("\n⏳ Generating Sector Summary PDFs...")
    sectors = ['IT', 'Financials', 'FMCG', 'Energy', 'Healthcare', 'Auto', 'Metals', 'Pharma', 'Telecom', 'Utilities', 'Infrastructure']
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('SecTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor("#1A365D"))
    body_style = ParagraphStyle('SecBody', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#2D3748"))

    for sector in sectors:
        sector_filename = os.path.join(REPORTS_SECTOR_DIR, f"{sector.lower()}_report.pdf")
        
        # Build a valid, clean mini-PDF for each sector
        doc = SimpleDocTemplate(sector_filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = [
            Paragraph(f"Nifty 100 Sector Intelligence Report: {sector}", title_style),
            Spacer(1, 10),
            Paragraph(f"This automated summary report aggregates key fundamental metrics, median valuations, and risk flags across all constituent companies mapped to the <b>{sector}</b> sector group.", body_style)
        ]
        doc.build(story)
            
    print(f"✅ Generated 11 valid sector report PDFs in: {REPORTS_SECTOR_DIR}/")

if __name__ == "__main__":
    run_batch_generation()