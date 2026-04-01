"""
Login View
============
Shown before anything else loads.
Sets st.session_state.contractor once login is successful.
"""

import streamlit as st
from db.auth import verify_login


def render():
    """
    Render the login screen.
    Returns True if logged in, False if not.
    """
    st.markdown("""
    <style>
    .stApp { background-color: #09122C; color: white; }
    .stButton > button {
        background-color: #6C63FF;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 0.6em 1.4em;
        border-radius: 10px;
        border: none;
        transition: 0.2s ease-in-out;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #4B44CC;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

    # Center the login form using columns
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("💼 Contractor Portal")
        st.markdown("#### Please log in to continue")
        st.markdown("---")

        contractor_id = st.text_input(
            "Contractor ID",
            placeholder="e.g. CTR-001",
            key="login_id"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        # Show error if login failed
        if st.session_state.get("login_failed"):
            st.error("❌ Invalid ID or password. Please try again.")
            st.session_state.login_failed = False

        if st.button("🔐 Login"):
            if not contractor_id or not password:
                st.warning("⚠️ Please enter both your ID and password.")
            else:
                contractor = verify_login(contractor_id.strip(), password.strip())
                if contractor:
                    # Save contractor info to session
                    st.session_state.contractor = contractor
                    st.rerun()
                    
                else:
                    st.session_state.login_failed = True

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Don't have access? Contact your service provider.")
