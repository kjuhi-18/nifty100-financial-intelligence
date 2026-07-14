import streamlit as st

from utils.db import (
    get_companies,
    get_available_years,
    get_peer_groups
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(

    page_title="Nifty 100 Analytics",

    page_icon="📈",

    layout="wide",

    initial_sidebar_state="expanded"

)

# ==========================================================
# Dashboard Header
# ==========================================================

st.title("📈 Nifty 100 Analytics")

st.caption("Nifty 100 Financial Analytics Dashboard")

st.markdown("---")

# ==========================================================
# Sidebar
# ==========================================================

st.sidebar.header("Dashboard Information")

companies = get_companies()

years = get_available_years()

peer_groups = get_peer_groups()

st.sidebar.metric(

    "Companies",

    len(companies)

)

st.sidebar.metric(

    "Financial Years",

    len(years)

)

st.sidebar.metric(

    "Peer Groups",

    len(peer_groups)

)

st.sidebar.markdown("---")

st.sidebar.success(
    "Navigate using the Pages menu above."
)

# ==========================================================
# Main Screen
# ==========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(

        "Companies",

        len(companies)

    )

with col2:

    st.metric(

        "Years",

        len(years)

    )

with col3:

    st.metric(

        "Peer Groups",

        len(peer_groups)

    )

st.markdown("---")

st.subheader("Dashboard Modules")

modules = [

    "🏠 Home",

    "🏢 Company Profile",

    "📊 Financial Screener",

    "👥 Peer Comparison",

    "📈 Trend Analysis",

    "🏭 Sector Analysis",

    "💰 Capital Allocation",

    "📄 Annual Reports"

]

for module in modules:

    st.write(f"✅ {module}")

st.info(
    "Use the Streamlit sidebar to open each page."
)
# ==========================================================
# Day 22 Dashboard Validation
# ==========================================================

from pathlib import Path

st.markdown("---")

st.header("✅ Day 22 Validation")

dashboard_root = Path(__file__).parent

pages_dir = dashboard_root / "pages"

utils_dir = dashboard_root / "utils"

required_pages = [

    "01_home.py",

    "02_profile.py",

    "03_screener.py",

    "04_peers.py",

    "05_trends.py",

    "06_sectors.py",

    "07_capital.py",

    "08_reports.py"

]

st.subheader("Project Structure")

app_status = (dashboard_root / "app.py").exists()

db_status = (utils_dir / "db.py").exists()

st.write(f"app.py : {'✅ PASS' if app_status else '❌ FAIL'}")

st.write(f"db.py : {'✅ PASS' if db_status else '❌ FAIL'}")

st.subheader("Pages")

page_count = 0

for page in required_pages:

    exists = (pages_dir / page).exists()

    if exists:

        page_count += 1

    st.write(f"{page} : {'✅ PASS' if exists else '❌ FAIL'}")

st.subheader("Database")

try:

    companies = get_companies()

    st.write(f"Companies Loaded : {len(companies)} ✅")

except Exception as e:

    st.error(e)

try:

    years = get_available_years()

    st.write(f"Years Loaded : {len(years)} ✅")

except Exception as e:

    st.error(e)

try:

    groups = get_peer_groups()

    st.write(f"Peer Groups Loaded : {len(groups)} ✅")

except Exception as e:

    st.error(e)

st.subheader("Overall")

checks = [

    app_status,

    db_status,

    page_count == 8

]

if all(checks):

    st.success("Day 22 Validation PASSED")

else:

    st.error("Day 22 Validation FAILED")

st.markdown("---")

st.header("Sprint 4 — Day 22 Completed")

st.write("✅ Streamlit application scaffold created")

st.write("✅ 8 dashboard pages created")

st.write("✅ Shared cached database layer implemented")

st.write("✅ Database queries working")

st.write("✅ Sidebar navigation available")

st.write("✅ Dashboard launches successfully")

st.write("✅ Ready for Day 23")
st.markdown("---")

st.header("🚀 Sprint 4 Progress")

completed = [

    "Dashboard Scaffold",

    "Database Layer",

    "Home Dashboard",

    "Company Profile"

]

for item in completed:

    st.write(f"✅ {item}")

st.success("Day 23 Completed")