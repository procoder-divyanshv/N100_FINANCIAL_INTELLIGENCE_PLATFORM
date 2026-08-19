# Sprint 4 Retrospective: Nifty 100 Financial Analytics & Valuation System

## Executive Summary
Sprint 4 focused on delivering a fully functional 8-screen financial intelligence dashboard. The sprint successfully met all exit criteria, including the implementation of the Streamlit dashboard, valuation logic, and data processing utilities.

## Key UX Decisions
* **Unified Sidebar:** Organized all 8 screens in the sidebar for intuitive navigation. Capitalized naming conventions for a professional appearance.
* **Screener Optimization:** Relocated custom metric sliders to the sidebar in the Screener screen. This significantly increased the vertical viewport for data tables, improving readability.
* **Search UX:** Implemented combined Ticker/Company Name dropdowns across Profile, Trends, and Reports screens to accommodate users searching by either identifier.

## Data Edge Cases & Technical Challenges
* **ID Mapping:** Encountered inconsistent identifier naming across datasets (e.g., `id` vs `company_id` vs `ticker`). Implemented a `f_col` smart-loading utility to dynamically detect and map these columns without hardcoding.
* **Type Mismatches:** Experienced critical merge errors during data integration due to `str` vs `int` type mismatches in primary key columns. Resolved by forcing type casting to `string` in the data utility layer before all `pd.merge()` operations.
* **Merge Conflicts:** Encountered `MergeError` when merging datasets with overlapping column names. Implemented a `safe_merge` function that surgically selects target columns and drops duplicates prior to merging.

## Performance Findings
* **Caching Strategy:** Applied `@st.cache_data(ttl=600)` to all data-loading functions in `db.py`. This ensured that the Company Profile screen and heavy computations load in under 3 seconds, meeting the sprint performance requirement.
* **Memory Management:** Streamlit’s rerendering can be memory-intensive with 92 companies. By utilizing standard file loading and caching, the memory footprint remains stable during user interaction.

## Definition of Done (DoD) Verification
* [x] **8-Screen Dashboard:** Verified all screens (`Home` through `Reports`) load correctly.
* [x] **Valuation Module:** Functional; exports `valuation_summary.xlsx` and `valuation_flags.csv`.
* [x] **Performance:** Load times verified to be under 3 seconds.
* [x] **Screener Export:** Verified CSV download produces correct headers and filtered data.
* [x] **Demo:** Ready for sign-off.

---
**Status:** Sprint 4 Completed. Ready for transition to Sprint 5.