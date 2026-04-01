"""
Company Wage Management System
================================
Main entry point — checks login first, then renders the app.
All logic lives in views/ and db/.
"""

import streamlit as st
from views import entry_tab, reports_tab, management_tab
from views import login

# ── Page Config ──
st.set_page_config(
    page_title="Contractor Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Hide Sidebar ──
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none }
    </style>
""", unsafe_allow_html=True)

# ── LOGIN GATE — nothing renders until this passes ──
if "contractor" not in st.session_state:
    login.render()
    st.stop()  # Blocks everything below from rendering

# ── Contractor is logged in from here onwards ──
contractor = st.session_state.contractor

# ── Session State ──
for key in [
    'employee_success', 'project_success',
    'wage_entry_success', 'expense_entry_success',
    'update_employee_success', 'update_project_success',
    'delete_employee_success', 'delete_project_success'
]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Title — shows business name of logged in contractor ──
st.title(f"💼 {contractor['business_name']} — Wage Management")
st.markdown("---")

# ── Tabs ──
tab1, tab2, tab3 = st.tabs(['🏠 Expense Entry', '📊 Reports', '⚙️ Management'])

with tab1:
    entry_tab.render()

with tab2:
    reports_tab.render()

with tab3:
    management_tab.render()