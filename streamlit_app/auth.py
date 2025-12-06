"""
Authentication module for Chit Fund Manager.

Version 1 uses simple mock authentication to preserve application flow.
This will be replaced with OAuth in Version 2.
"""

from typing import Optional
import streamlit as st


def initialize_auth() -> None:
    """Initialize authentication state in session."""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = None


def is_authenticated() -> bool:
    """
    Check if user is authenticated.
    
    Returns:
        True if user is authenticated, False otherwise
    """
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[str]:
    """
    Get the current authenticated user.
    
    Returns:
        Username or None if not authenticated
    """
    return st.session_state.get('user', None)


def login(username: str = 'local_admin') -> None:
    """
    Perform mock login.
    
    Args:
        username: Username to log in as (default: 'local_admin')
    """
    st.session_state['authenticated'] = True
    st.session_state['user'] = username


def logout() -> None:
    """Perform logout and clear session state."""
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    
    # Clear other session state
    keys_to_clear = [
        'selected_chit', 
        'current_stage', 
        'installments_data',
        'analysis_result'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
