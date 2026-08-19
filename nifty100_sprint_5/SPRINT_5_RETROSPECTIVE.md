# Sprint 5 Retrospective: Intelligence, NLP & PDF Reporting

## Summary of Accomplishments
* **NLP Parser:** Successfully implemented a Regex text parser (`src/nlp/parser.py`) to extract structured CAGR values from unstructured descriptive text fields.
* **Auto Pros/Cons Generator:** Developed logic rules identifying baseline financial strengths and risks, ensuring every company outputs a robust list of pros and cons with confidence metrics.
* **Cash Flow Intelligence:** Built cash-to-earnings quality grading, CapEx intensity classifications, and financial distress signal detectors (`src/analytics/cashflow_kpis.py`).
* **PDF Report Generation & Batch Processing:** Built dynamic 2-page company tearsheets, unique landscape sector intelligence reports, and master portfolio summaries using ReportLab with custom page numbering and auto-wrapping.
* **Frontend UI Integration:** Connected all generated PDF deliverables directly into the Streamlit dashboard (`08_reports.py`) for interactive web viewing and downloads.

## Technical Findings & Data Quality
* Regex matching successfully isolated granular metrics, allowing structured cross-validation against underlying ratio tables.
* ReportLab layout constraints required defensive padding and explicit column sizing to avoid overlapping text blocks during batch execution.
* Implemented robust multi-column cross-referencing and URL-filtering logic to resolve primary key mismatches and eliminate logo link artifacts from company names.

---
**Status:** Sprint 5 Fully Completed, Bug-Tested, and Ready for Sign-Off.