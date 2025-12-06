"""
Utility functions for the Streamlit UI.

This module provides helper functions for UI components, formatting,
and common operations.
"""

from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import date, datetime
import streamlit as st
import pandas as pd


def format_currency(amount: float | Decimal, currency: str = '₹') -> str:
    """
    Format a number as currency.
    
    Args:
        amount: The amount to format
        currency: Currency symbol (default: ₹)
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return f"{currency}0.00"
    
    amount_float = float(amount) if isinstance(amount, Decimal) else amount
    return f"{currency}{amount_float:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a decimal value as percentage.
    
    Args:
        value: The value to format (e.g., 0.15 for 15%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "0.00%"
    
    return f"{value * 100:.{decimals}f}%"


def show_metric_card(label: str, value: str, delta: Optional[str] = None) -> None:
    """
    Display a metric card.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta/change value
    """
    st.metric(label=label, value=value, delta=delta)


def show_success(message: str) -> None:
    """Display a success message."""
    st.success(f"✅ {message}")


def show_error(message: str) -> None:
    """Display an error message."""
    st.error(f"❌ {message}")


def show_warning(message: str) -> None:
    """Display a warning message."""
    st.warning(f"⚠️ {message}")


def show_info(message: str) -> None:
    """Display an info message."""
    st.info(f"ℹ️ {message}")


def apply_custom_css() -> None:
    """Apply custom CSS for professional financial dashboard styling."""
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
        color: #1f2937;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Cards and containers */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 10px 20px !important;
        white-space: normal !important;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Buttons with use_container_width */
    [data-testid="column"] .stButton > button {
        width: 100% !important;
    }
    
    /* Tables */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1f2937;
        font-weight: 600;
    }
    
    /* Sidebar Main */
    [data-testid="stSidebar"] {
        background-color: #1f2937 !important;
        min-width: 300px;
    }
    
    [data-testid="stSidebar"] > div {
        padding: 16px;
    }
    
    /* Sidebar - Text and Paragraphs */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #f3f4f6 !important;
        white-space: normal;
        overflow-wrap: break-word;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #f3f4f6 !important;
    }
    
    [data-testid="stSidebar"] strong {
        color: #f9fafb !important;
        font-weight: 600;
    }
    
    /* Sidebar Buttons */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left;
        padding: 12px 16px !important;
        margin: 6px 0 !important;
        background-color: #374151 !important;
        border: 1px solid #4b5563 !important;
        color: #f3f4f6 !important;
        border-radius: 6px;
        font-weight: 500;
        white-space: normal !important;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #4b5563 !important;
        border-color: #6b7280 !important;
    }
    
    /* Sidebar Metric Display */
    [data-testid="stSidebar"] [data-testid="stMetricValue"],
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #f3f4f6 !important;
    }
    
    /* Sidebar Divider */
    [data-testid="stSidebar"] hr {
        border-color: #4b5563 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 6px;
        border: 1px solid #d1d5db;
    }
    
    /* Success/Error styling */
    .stSuccess {
        background-color: #d1fae5;
        border-left-color: #10b981;
    }
    
    .stError {
        background-color: #fee2e2;
        border-left-color: #ef4444;
    }
    
    .stWarning {
        background-color: #fef3c7;
        border-left-color: #f59e0b;
    }
    
    .stInfo {
        background-color: #dbeafe;
        border-left-color: #3b82f6;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)


def validate_positive_number(value: Any, field_name: str) -> bool:
    """
    Validate that a value is a positive number.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        True if valid, False otherwise (shows error)
    """
    try:
        num_value = float(value) if value else 0
        if num_value <= 0:
            show_error(f"{field_name} must be a positive number")
            return False
        return True
    except (ValueError, TypeError):
        show_error(f"{field_name} must be a valid number")
        return False


def validate_positive_integer(value: Any, field_name: str) -> bool:
    """
    Validate that a value is a positive integer.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        True if valid, False otherwise (shows error)
    """
    try:
        int_value = int(value) if value else 0
        if int_value <= 0:
            show_error(f"{field_name} must be a positive integer")
            return False
        return True
    except (ValueError, TypeError):
        show_error(f"{field_name} must be a valid integer")
        return False


def create_downloadable_df(df: pd.DataFrame, filename: str) -> bytes:
    """
    Create a downloadable Excel file from a DataFrame.
    
    Args:
        df: DataFrame to convert
        filename: Name for the file
        
    Returns:
        Bytes object containing the Excel file
    """
    from io import BytesIO
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    return buffer.getvalue()


def get_frequency_label(frequency: int) -> str:
    """
    Get a human-readable label for payment frequency.
    
    Args:
        frequency: Frequency per year
        
    Returns:
        Label string
    """
    frequency_map = {
        1: "Yearly",
        2: "Half-Yearly",
        3: "Quarterly (4 months)",
        4: "Quarterly",
        6: "Bi-Monthly",
        12: "Monthly"
    }
    return frequency_map.get(frequency, f"{frequency} times/year")


def calculate_installment_amount(
    total_value: Decimal,
    discount: Decimal,
    total_installments: int,
    current_installment: int
) -> Decimal:
    """
    Calculate amount to be paid by non-winner candidates.
    
    Formula: (Total Value - Discount) / (Total Installments - Current Installment + 1)
    
    Args:
        total_value: Full chit value
        discount: Discount (bid amount)
        total_installments: Total number of installments
        current_installment: Current installment number
        
    Returns:
        Calculated amount per person
    """
    remaining_installments = total_installments - current_installment + 1
    if remaining_installments <= 0:
        return Decimal('0')
    
    amount = (total_value - discount) / remaining_installments
    return amount


def initialize_session_state() -> None:
    """Initialize all required session state variables."""
    defaults = {
        'authenticated': False,
        'user': None,
        'current_stage': 0,
        'selected_chit': None,
        'installments_data': None,
        'analysis_result': None,
        'db_instance': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
