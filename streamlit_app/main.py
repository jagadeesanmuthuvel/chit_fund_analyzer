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
from streamlit_app.utils import apply_custom_css, initialize_session_state
from streamlit_app.stages import login, dashboard, installments, analytics

# Data Manager Imports
from streamlit_app.data_manager.base import DataManager
from streamlit_app.data_manager.local import LocalDataManager
from streamlit_app.data_manager.gsheets import GoogleSheetsDataManager
from streamlit_app.data_manager.auth import GoogleAuthManager
from streamlit_app.data_manager.migration import migrate_local_to_gsheets

# Page configuration
st.set_page_config(
    page_title="Chit Fund Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def handle_oauth_callback():
    """Handle Google OAuth callback."""
    if 'code' in st.query_params:
        code = st.query_params['code']
        try:
            GoogleAuthManager.exchange_code(code)
            st.session_state['storage_type'] = 'gsheets'
            # Clear query params
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")

def initialize_app() -> DataManager:
    """
    Initialize the application and data manager.
    
    Returns:
        DataManager instance or None if configuration needed
    """
    # Initialize session state
    initialize_session_state()
    initialize_auth()
    
    # Handle OAuth Callback
    handle_oauth_callback()
    
    # Check if DB is already initialized
    if 'db_instance' in st.session_state and st.session_state['db_instance'] is not None:
        return st.session_state['db_instance']
        
    # Check storage preference
    storage_type = st.session_state.get('storage_type')
    
    if storage_type == 'local':
        db_path = Path(__file__).parent.parent / "data" / "chit_fund_db.xlsx"
        db = LocalDataManager(str(db_path))
        st.session_state['db_instance'] = db
        return db
        
    elif storage_type == 'gsheets':
        creds = GoogleAuthManager.get_credentials()
        
        if creds:
            try:
                db = GoogleSheetsDataManager(creds)
                st.session_state['db_instance'] = db
                return db
            except Exception as e:
                st.error(f"Failed to connect to Google Sheets: {str(e)}")
                # Allow retry
                if st.button("Retry Connection"):
                    st.rerun()
                return None
        else:
            return None # Need authentication
            
    return None # Need selection

def render_storage_selection():
    """Render the storage selection screen."""
    st.markdown("""
    <div style='text-align: center; padding: 50px 0;'>
        <h1>💾 Storage Configuration</h1>
        <p>Please select where you want to store your data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Local Storage")
        st.markdown("Store data in a local Excel file. Best for single-user local deployment.")
        if st.button("Use Local Storage", use_container_width=True):
            st.session_state['storage_type'] = 'local'
            st.rerun()
            
    with col2:
        st.markdown("### ☁️ Google Sheets")
        st.markdown("Store data in Google Sheets. Best for cloud access and backup.")
        if st.button("Use Google Sheets", use_container_width=True):
            st.session_state['storage_type'] = 'gsheets'
            st.rerun()

def render_google_auth():
    """Render Google Authentication screen."""
    st.markdown("""
    <div style='text-align: center; padding: 50px 0;'>
        <h1>🔐 Google Authentication</h1>
        <p>Please sign in with Google to access your Chit Fund data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        try:
            auth_url = GoogleAuthManager.get_auth_url()
            st.link_button("Sign in with Google", auth_url, use_container_width=True)
        except Exception as e:
            st.error(f"Configuration Error: {str(e)}")
            st.info("Please ensure GOOGLE_CLIENT_SECRETS_JSON or client secrets are configured in .streamlit/secrets.toml")
            
        if st.button("← Back to Storage Selection"):
            st.session_state['storage_type'] = None
            st.rerun()

def render_sidebar(db: DataManager) -> None:
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
            try:
                chits = db.get_all_chits()
                st.markdown("### 📈 Quick Stats")
                st.metric("Total Chits", len(chits))
                
                if st.session_state.get('selected_chit'):
                    st.markdown(f"**Active:** {st.session_state['selected_chit']['name'][:20]}...")
            except Exception as e:
                st.error(f"Error loading stats: {str(e)}")
            
            st.markdown("---")
            
            # Settings / Migration
            with st.expander("⚙️ Settings"):
                st.write(f"Storage: **{st.session_state.get('storage_type', 'Unknown').title()}**")
                
                if st.session_state.get('storage_type') == 'gsheets':
                    if st.button("Migrate from Local"):
                        try:
                            local_path = Path(__file__).parent.parent / "data" / "chit_fund_db.xlsx"
                            local_db = LocalDataManager(str(local_path))
                            migrate_local_to_gsheets(local_db, db)
                        except Exception as e:
                            st.error(f"Migration failed: {str(e)}")
                            
                if st.button("Reset Storage Selection"):
                    st.session_state['storage_type'] = None
                    st.session_state['db_instance'] = None
                    st.rerun()
            
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
    
    # If DB is not initialized, it means we need configuration
    if db is None:
        storage_type = st.session_state.get('storage_type')
        if not storage_type:
            render_storage_selection()
        elif storage_type == 'gsheets':
            render_google_auth()
        return

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
