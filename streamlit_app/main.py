"""
Chit Fund Manager - Main Application Entry Point

A comprehensive Streamlit application for managing and analyzing chit funds.
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_app.auth import initialize_auth, is_authenticated, logout
from streamlit_app.db import ChitFundDB
from streamlit_app.utils import apply_custom_css, initialize_session_state
from streamlit_app.stages import login, dashboard, installments, analytics


# Page configuration
st.set_page_config(
    page_title="Chit Fund Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_app() -> ChitFundDB:
    """
    Initialize the application.
    
    Returns:
        Database instance
    """
    # Initialize session state
    initialize_session_state()
    initialize_auth()
    
    # Initialize database
    if 'db_instance' not in st.session_state or st.session_state['db_instance'] is None:
        db_path = Path(__file__).parent.parent / "data" / "chit_fund_db.xlsx"
        st.session_state['db_instance'] = ChitFundDB(str(db_path))
    
    return st.session_state['db_instance']


def render_sidebar(db: ChitFundDB) -> None:
    """Render the application sidebar."""
    
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: #f9fafb; font-size: 28px; margin: 0;'>💰</h1>
            <h2 style='color: #f9fafb; font-size: 20px; margin: 10px 0;'>Chit Fund Manager</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Show user info if authenticated
        if is_authenticated():
            user = st.session_state.get('user', 'User')
            st.markdown(f"""
            <div style='text-align: center; color: #d1d5db;'>
                <p>👤 Logged in as<br><strong>{user}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### 📍 Navigation")
            
            current_stage = st.session_state.get('current_stage', 0)
            
            # Stage indicators
            stages = [
                ("🏠 Dashboard", 1),
                ("📝 Installments", 2),
                ("📊 Analytics", 3)
            ]
            
            for stage_name, stage_num in stages:
                if stage_num == current_stage:
                    st.markdown(f"**▶ {stage_name}**")
                else:
                    if st.button(stage_name, key=f"nav_{stage_num}", use_container_width=True):
                        st.session_state['current_stage'] = stage_num
                        st.rerun()
            
            st.markdown("---")
            
            # Quick stats
            chits = db.get_all_chits()
            st.markdown("### 📈 Quick Stats")
            st.metric("Total Chits", len(chits))
            
            if st.session_state.get('selected_chit'):
                st.markdown(f"**Active:** {st.session_state['selected_chit']['name'][:20]}...")
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                logout()
                st.rerun()
        
        else:
            st.markdown("""
            <div style='text-align: center; color: #d1d5db; padding: 20px;'>
                <p>Please login to continue</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #9ca3af; font-size: 12px;'>
            <p>Version 1.0.0<br>© 2024 Chit Fund Manager</p>
        </div>
        """, unsafe_allow_html=True)


def main() -> None:
    """Main application logic."""
    
    # Initialize
    db = initialize_app()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Render sidebar
    render_sidebar(db)
    
    # Get current stage
    current_stage = st.session_state.get('current_stage', 0)
    
    # Route to appropriate stage
    if not is_authenticated():
        login.render()
    else:
        if current_stage == 1:
            dashboard.render(db)
        elif current_stage == 2:
            installments.render(db)
        elif current_stage == 3:
            analytics.render(db)
        else:
            # Default to dashboard
            st.session_state['current_stage'] = 1
            st.rerun()


if __name__ == "__main__":
    main()
