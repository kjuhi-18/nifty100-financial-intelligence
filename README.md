# Nifty 100 Analytics Dashboard

A comprehensive financial analytics platform for Nifty 100 companies built using **Python**, **SQLite**, **Streamlit**, and **Plotly**. The dashboard provides company analysis, peer comparison, financial screening, trend analysis, valuation, and interactive visualizations.

---

# Features

- Financial Screener
- Company Profile
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation Map
- Annual Reports
- Valuation Module

---

# Project Structure

```
N100/

│

├── src/

│ ├── analytics/

│ ├── dashboard/

│ └── screener/

│

├── db/

│ └── nifty100.db

│

├── data/

│ ├── market_cap.xlsx

│ ├── sectors.xlsx

│ └── companies.xlsx

│

├── output/

│ ├── screener_output.xlsx

│ ├── peer_comparison.xlsx

│ ├── valuation_summary.xlsx

│ └── valuation_flags.csv

│

├── reports/

│ └── radar_charts/

│

└── README.md
```

---

# Installation

Clone the repository

```bash
git clone <repository-url>
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Run Dashboard

```bash
streamlit run src/dashboard/app.py
```

The application will open in your browser at

```
http://localhost:8501
```

---
---

# Dashboard Screens

The dashboard consists of **8 interactive screens** for analyzing Nifty 100 companies.

---

## 1. Home Dashboard

**Features**

- Summary KPI cards
- Sector distribution
- Top Quality Companies
- Year Selector
- Company Statistics

**Screenshot**

> *(Add screenshot here)*

---

## 2. Company Profile

**Features**

- Company Search
- Company Information
- Financial KPI Cards
- Revenue & Profit Trends
- ROE / ROCE Trends
- Pros & Cons

**Screenshot**

> *(Add screenshot here)*

---

## 3. Financial Screener

**Features**

- 10 Interactive Filters
- 6 Investment Presets
- Live Filtering
- Composite Quality Score
- CSV Export

**Screenshot**

> *(Add screenshot here)*

---

## 4. Peer Comparison

**Features**

- Peer Group Selection
- Company Comparison
- Radar Chart
- Peer Average Overlay
- Benchmark Highlighting

**Screenshot**

> *(Add screenshot here)*

---

## 5. Trend Analysis

**Features**

- Company Selection
- Multi-Metric Comparison
- Interactive Plotly Charts
- Historical Financial Trends
- Trend Data Table

**Screenshot**

> *(Add screenshot here)*

---

## 6. Sector Analysis

**Features**

- Sector Dropdown
- Bubble Chart
- Sector Median KPI Chart
- Company Comparison Table

**Screenshot**

> *(Add screenshot here)*

---

## 7. Capital Allocation Map

**Features**

- Interactive Treemap
- Capital Allocation Classification
- Pattern Distribution
- Company Explorer

**Screenshot**

> *(Add screenshot here)*

---

## 8. Annual Reports

**Features**

- Company Search
- Annual Report Links
- Report Availability
- BSE Profile Links

**Screenshot**

> *(Add screenshot here)*

---

# Dashboard Highlights

- Interactive Plotly Visualizations
- Cached Database Queries
- SQLite Backend
- 92 Nifty 100 Companies
- 11 Peer Groups
- Financial Screening Engine
- Peer Ranking Engine
- Valuation Module
- Radar Charts
- CSV & Excel Export Support

# Technologies Used

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- OpenPyXL
- Matplotlib

---

# Data Sources

- Financial Statements
- Market Capitalization
- Peer Groups
- Sector Mapping
- Annual Reports
---

# Sprint 4 Retrospective

## Sprint Goal

The objective of Sprint 4 was to develop a complete **Streamlit-based Financial Analytics Dashboard** for Nifty 100 companies and implement a **Valuation Module** capable of identifying potentially overvalued and undervalued companies using financial metrics.

---

## Completed Work

- Developed a multi-page Streamlit dashboard with **8 interactive screens**
- Implemented a cached database layer for improved performance
- Added interactive company search and financial visualizations
- Built an advanced financial screener with configurable filters and investment presets
- Integrated peer comparison with radar charts and benchmark highlighting
- Implemented sector analysis and capital allocation visualizations
- Added annual report lookup functionality
- Developed a valuation engine with FCF Yield, Sector Median P/E and valuation flags
- Generated valuation reports in Excel and CSV formats
- Completed integration testing across all dashboard modules

---

## UX Decisions

The dashboard was designed with usability and simplicity in mind.

- Wide layout for better utilization of screen space
- Sidebar navigation for quick access to all modules
- Interactive Plotly charts for better user experience
- KPI cards for quick financial summaries
- Search-based company selection instead of long dropdowns
- Consistent layout across all dashboard pages
- Responsive tables with full-width display

---

## Data Edge Cases

During development several data quality issues were identified and handled.

- Missing financial metrics are displayed as **N/A**
- Companies with partial historical data display available records without errors
- Empty datasets show informative messages instead of blank charts
- Division-by-zero situations are handled safely
- Radar charts normalize available values while ignoring missing metrics
- Valuation calculations skip invalid or missing values where appropriate

---

## Performance Findings

Several optimizations were implemented to improve responsiveness.

- Streamlit caching (`@st.cache_data`) reduced repeated database queries
- Database operations were centralized through shared utility functions
- Plotly charts render efficiently for all supported companies
- Dashboard pages load within the target response time under normal usage
- Financial screening remains responsive even with multiple active filters

---

## Challenges Faced

- Merging data from multiple sources with different schemas
- Standardizing company identifiers across datasets
- Handling incomplete financial data
- Building dynamic radar charts for peer comparison
- Ensuring consistent formatting across Excel reports
- Maintaining dashboard responsiveness while displaying large datasets

---

## Solutions Implemented

- Standardized company identifiers before merging datasets
- Added validation checks before exporting reports
- Introduced cached database queries
- Implemented safe handling of missing values
- Added reusable utility functions for database access
- Performed integration testing across all dashboard pages

---

## Lessons Learned

Sprint 4 provided practical experience in:

- Building production-style Streamlit applications
- Designing reusable database utility modules
- Interactive data visualization with Plotly
- Financial ratio analysis and valuation techniques
- Integration testing and quality assurance
- Structuring scalable analytics projects

---

## Sprint Outcome

**Sprint 4 was successfully completed.**

All planned dashboard modules, valuation features, reports and validation tasks were implemented successfully and are ready for demonstration.
