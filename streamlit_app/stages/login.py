"""
Stage 0: Login Page

Simple mock login for Version 1.
"""

import streamlit as st
from streamlit_app.auth import login, is_authenticated
from streamlit_app.utils import apply_custom_css


def render() -> None:
    """Render the login page."""
    apply_custom_css()
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # App header
        st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #1f2937; font-size: 42px; margin-bottom: 10px;'>
                💰 Chit Fund Manager
            </h1>
            <p style='color: #6b7280; font-size: 18px; margin-bottom: 40px;'>
                Professional Chit Fund Analysis & Management
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login card
        with st.container():
            st.markdown("""
            <div style='
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            '>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <h3 style='text-align: center; color: #374151; margin-bottom: 30px;'>
                Welcome Back
            </h3>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <p style='text-align: center; color: #6b7280; margin-bottom: 30px;'>
                Version 1.0 - Local Mode
            </p>
            """, unsafe_allow_html=True)
            
            # Login button
            if st.button("🔐 Login to Continue", use_container_width=True, type="primary"):
                login('local_admin')
                st.session_state['current_stage'] = 1
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <p style='text-align: center; color: #9ca3af; font-size: 14px;'>
            Built with Streamlit • Powered by chit_fund_analyzer
        </p>
        """, unsafe_allow_html=True)
