# N100 Financial Analytics Platform

A comprehensive financial analytics platform for analyzing **Nifty 100**
companies using an automated ETL pipeline, SQLite database, FastAPI
backend, and Streamlit dashboard.

------------------------------------------------------------------------

# Features

-   Automated ETL Pipeline
-   SQLite Database
-   Streamlit Dashboard
-   FastAPI REST API
-   Company Financial Statements
-   Financial Ratio Analysis
-   Stock Screener
-   Peer Comparison
-   Sector Analysis
-   PDF Tearsheet Generation
-   Automated Data Validation
-   Unit, Integration and Performance Testing

------------------------------------------------------------------------

# System Architecture

``` text
Excel Data Files
        │
        ▼
ETL Pipeline
        │
        ▼
SQLite Database
        │
 ┌──────┴──────┐
 ▼             ▼
FastAPI     Streamlit
        │
        ▼
Financial Analysts
```

------------------------------------------------------------------------

# Project Structure

``` text
N100/
├── data/
├── db/
├── docs/
├── output/
├── src/
│   ├── api/
│   ├── dashboard/
│   ├── etl/
│   ├── services/
│   ├── utils/
│   └── validation/
├── tests/
├── README.md
└── requirements.txt
```

------------------------------------------------------------------------

# Installation

Clone the repository

``` bash
git clone <repository-url>
cd N100
```

Install dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# Running the ETL Pipeline

``` bash
python src/etl/load_data.py
```

Expected outcome:

-   Database created
-   Financial data loaded
-   Validation completed
-   Ready for dashboard and API

------------------------------------------------------------------------

# Launch the Streamlit Dashboard

``` bash
streamlit run src/dashboard/app.py
```

Dashboard Modules:

-   Home
-   Company Profile
-   Stock Screener
-   Peer Comparison
-   Sector Analysis
-   Capital Allocation

------------------------------------------------------------------------

# Run the FastAPI Server

``` bash
uvicorn src.api.main:app --reload
```

Swagger Documentation:

``` text
http://127.0.0.1:8000/docs
```

------------------------------------------------------------------------

# API Endpoints

  Endpoint                                  Description
  ----------------------------------------- ------------------
  `/api/v1/health`                          Health check
  `/api/v1/companies`                       Company list
  `/api/v1/companies/{company_id}`          Company details
  `/api/v1/companies/{company_id}/ratios`   Financial ratios
  `/api/v1/screener`                        Stock screener
  `/api/v1/sectors/{sector}/companies`      Sector companies

------------------------------------------------------------------------

# Database

The application stores processed financial information inside an
optimized SQLite database with indexes for faster query execution.

Main tables include:

-   companies
-   profitandloss
-   balancesheet
-   cashflow
-   financial_ratios
-   stock_prices
-   peer_groups
-   documents
-   sectors

------------------------------------------------------------------------

# Testing

Run all tests:

``` bash
pytest
```

API tests

``` bash
pytest tests/api
```

Integration tests

``` bash
pytest tests/integration
```

Performance tests

``` bash
pytest tests/performance
```

------------------------------------------------------------------------

# Performance Summary

  Test                  Status
  --------------------- -----------
  ETL Validation        ✅ Passed
  API Testing           ✅ Passed
  Dashboard Testing     ✅ Passed
  Integration Testing   ✅ Passed
  Performance Testing   ✅ Passed

------------------------------------------------------------------------

# Technologies Used

-   Python
-   SQLite
-   FastAPI
-   Streamlit
-   Pandas
-   Plotly
-   Pytest
-   Black
-   Ruff

------------------------------------------------------------------------

# Screenshots

Add screenshots in this section.

``` text
docs/images/dashboard.png
docs/images/screener.png
docs/images/company_profile.png
docs/images/swagger.png
docs/images/tearsheet.png
```

------------------------------------------------------------------------

# Future Enhancements

-   User Authentication
-   Cloud Database Support
-   Portfolio Tracking
-   Machine Learning Insights
-   Scheduled ETL
-   Power BI Integration
-   Email Reporting

------------------------------------------------------------------------

# Contributors

**N100 Development Team**

------------------------------------------------------------------------

# License

This project is intended for academic and educational purposes.
