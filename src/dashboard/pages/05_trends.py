import streamlit as st
from utils.db import get_companies

st.title("Trend Analysis")
companies = get_companies()

st.success(f"{len(companies)} companies available.")