"""
Enhanced Chit Fund Analyzer with Flexible Payment Frequencies
Multi-stage Streamlit application for comprehensive chit fund analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import plotly.express as px
from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer, ScenarioAnalyzer
from google_sheets_service_auto import google_sheets_service
import json
from typing import Dict, List, Optional

# Page config
st.set_page_config(
    page_title="Chit Fund Analyzer Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'authenticated': False,
        'current_stage': 'authentication',
        'spreadsheet_created': False,
        'chit_config': {},
        'installments_data': [],
        'selected_chit_for_analysis': None,
        'show_installment_form': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

def get_frequency_details(frequency: str) -> Dict:
    """Get details for different payment frequencies"""
    frequency_map = {
        'Monthly': {'months_between': 1, 'per_year': 12, 'label': 'Monthly'},
        'Bi-monthly': {'months_between': 2, 'per_year': 6, 'label': 'Every 2 months'},
        'Quarterly': {'months_between': 3, 'per_year': 4, 'label': 'Every 3 months'},
        'Half-yearly': {'months_between': 6, 'per_year': 2, 'label': 'Every 6 months'},
        'Yearly': {'months_between': 12, 'per_year': 1, 'label': 'Yearly'}
    }
    return frequency_map.get(frequency, frequency_map['Monthly'])

def calculate_installment_dates(start_date: date, frequency: str, total_installments: int) -> List[date]:
    """Calculate all installment dates based on frequency"""
    freq_details = get_frequency_details(frequency)
    months_between = freq_details['months_between']
    
    dates = []
    current_date = start_date
    
    for i in range(total_installments):
        dates.append(current_date)
        # Add months
        if current_date.month + months_between > 12:
            new_year = current_date.year + ((current_date.month + months_between - 1) // 12)
            new_month = ((current_date.month + months_between - 1) % 12) + 1
        else:
            new_year = current_date.year
            new_month = current_date.month + months_between
        
        try:
            current_date = current_date.replace(year=new_year, month=new_month)
        except ValueError:
            # Handle cases like Feb 31 -> Feb 28/29
            import calendar
            last_day = calendar.monthrange(new_year, new_month)[1]
            current_date = current_date.replace(year=new_year, month=new_month, day=min(current_date.day, last_day))
    
    return dates

def show_authentication_page():
    """Display the automatic OAuth authentication page"""
    st.title("🔐 Chit Fund Analyzer Pro - Authentication")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### Welcome to Enhanced Chit Fund Analyzer! 
        
        **New Features:**
        - ✅ Flexible Payment Frequencies (Monthly, Quarterly, Half-yearly, etc.)
        - ✅ 3-Stage Workflow (Config → Installments → Analysis)
        - ✅ Advanced Chit Methods Support
        - ✅ Editable Installment Tables
        - ✅ Comprehensive Analysis & Scenarios
        
        **Your data security:**
        - Your data stays in your own Google Drive
        - Automatic OAuth authentication
        - No manual code copying required
        """)
        
        st.markdown("---")
        
        if google_sheets_service.is_authenticated():
            st.success("✅ Already authenticated!")
            if st.button("Continue to Configuration", type="primary"):
                st.session_state.authenticated = True
                st.session_state.current_stage = "configuration"
                st.rerun()
        else:
            st.info("Click below to start automatic authentication")
            
            if st.button("🔑 Authenticate with Google", type="primary"):
                with st.spinner("Starting authentication process..."):
                    import os
                    if not os.path.exists('oauth_credentials.json'):
                        st.error("❌ OAuth credentials file not found! Please ensure oauth_credentials.json is in the project directory.")
                        return
                    
                    if google_sheets_service.authenticate_automatically():
                        st.success("✅ Authentication successful!")
                        st.session_state.authenticated = True
                        st.session_state.current_stage = "configuration"
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Authentication failed! Please check your credentials and try again.")

def show_configuration_stage():
    """Stage 1: Basic Configuration"""
    st.title("⚙️ Stage 1: Basic Configuration")
    st.markdown("---")
    
    # Setup spreadsheet if not done
    if not st.session_state.spreadsheet_created:
        with st.spinner("Setting up your Google Sheets..."):
            spreadsheet_name = "Chit Fund Analyzer Pro Data"
            if google_sheets_service.create_or_get_spreadsheet(spreadsheet_name):
                st.session_state.spreadsheet_created = True
                st.success("✅ Google Sheets setup complete!")
                
                spreadsheet_url = google_sheets_service.get_spreadsheet_url()
                if spreadsheet_url:
                    st.info(f"📊 [Your Data Spreadsheet]({spreadsheet_url})")
            else:
                st.error("❌ Failed to setup Google Sheets. Please check authentication.")
                return
    
    # Load existing configurations
    existing_configs = google_sheets_service.get_chit_configurations()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Create New Chit Fund Configuration")
        
        # Basic parameters outside form for real-time updates
        st.markdown("### 📊 Basic Parameters")
        
        chit_name = st.text_input("Chit Fund Name*", placeholder="e.g., Quarterly Investment Chit")
        
        col_total, col_value = st.columns(2)
        with col_total:
            total_installments = st.number_input("Total Installments*", min_value=4, max_value=120, value=14, step=1)
        with col_value:
            full_chit_value = st.number_input("Full Chit Value (₹)*", min_value=10000, value=700000, step=5000)
        
        payment_frequency = st.selectbox(
            "Payment Frequency*",
            ["Monthly", "Bi-monthly", "Quarterly", "Half-yearly", "Yearly"],
            index=2  # Default to Quarterly
        )
        
        # Real-time calculated values
        freq_details = get_frequency_details(payment_frequency)
        installment_amount = full_chit_value / total_installments if total_installments > 0 else 0
        duration_months = total_installments * freq_details['months_between']
        
        st.markdown("### 📈 Calculated Values")
        col_calc1, col_calc2, col_calc3 = st.columns(3)
        with col_calc1:
            st.metric("Installment Amount", f"₹{installment_amount:,.0f}")
        with col_calc2:
            st.metric("Frequency", freq_details['label'])
        with col_calc3:
            st.metric("Total Duration", f"{duration_months} months")
        
        # Additional configuration in form
        with st.form("enhanced_chit_config"):
            st.markdown("### 🔧 Additional Settings")
            
            col_method, col_rate = st.columns(2)
            with col_method:
                chit_method = st.selectbox(
                    "Chit Method*",
                    ["Auction", "Lucky Draw", "Serial Basis", "Dividend Method", "Bidding", "Fixed Percentage", "Foreman's Choice"]
                )
            with col_rate:
                interest_rate = st.number_input("Interest/Commission Rate (%)", min_value=0.0, max_value=50.0, value=12.0, step=0.1)
            
            start_date = st.date_input("First Chit Installment Date*", value=date.today())
            
            submitted = st.form_submit_button("💾 Save Configuration & Proceed", type="primary")
            
            if submitted:
                if all([chit_name, total_installments, full_chit_value, payment_frequency, start_date]):
                    chit_frequency_per_year = freq_details['per_year']
                    
                    config_data = {
                        'chit_name': chit_name,
                        'total_installments': total_installments,
                        'full_chit_value': full_chit_value,
                        'payment_frequency': payment_frequency,
                        'chit_frequency_per_year': chit_frequency_per_year,
                        'chit_method': chit_method,
                        'interest_rate': interest_rate,
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'installment_amount': installment_amount,
                        'duration_months': duration_months
                    }
                    
                    if google_sheets_service.save_chit_configuration(config_data):
                        st.session_state.chit_config = config_data
                        st.success(f"✅ Configuration saved for '{chit_name}'!")
                        
                        # Check if this is a new chit fund (start date is today or future)
                        today = date.today()
                        if start_date >= today:
                            st.info("🚀 New chit fund detected! Proceeding directly to analysis stage.")
                            st.session_state.current_stage = "analysis"
                        else:
                            st.info("📅 Existing chit fund detected! Please enter previous installments first.")
                            st.session_state.current_stage = "installments"
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to save configuration. Please try again.")
                else:
                    st.error("⚠️ Please fill all required fields marked with *")
    
    with col2:
        st.subheader("📋 Existing Configurations")
        
        if existing_configs:
            for config in existing_configs[-5:]:  # Show last 5
                with st.expander(f"💰 {config.get('Chit Name', 'Unnamed')}"):
                    st.write(f"**Value:** ₹{config.get('Total Amount', 0):,}")
                    st.write(f"**Frequency:** {config.get('Payment Frequency', 'Monthly')}")
                    st.write(f"**Method:** {config.get('Chit Method', 'Auction')}")
                    
                    if st.button(f"📝 Edit {config.get('Chit Name', 'This')}", key=f"edit_{config.get('Chit Name', '')}"):
                        st.session_state.chit_config = config
                        st.session_state.current_stage = "installments"
                        st.rerun()
        else:
            st.info("No configurations yet. Create your first chit fund configuration!")

def show_installments_stage():
    """Stage 2: Previous Installments Entry"""
    st.title("📅 Stage 2: Previous Installments Entry")
    st.markdown("---")
    
    if not st.session_state.chit_config:
        st.error("⚠️ No configuration found. Please complete Stage 1 first.")
        if st.button("← Back to Configuration"):
            st.session_state.current_stage = "configuration"
            st.rerun()
        return
    
    config = st.session_state.chit_config
    
    # Display current configuration summary
    st.subheader(f"📊 Configuration: {config.get('chit_name', 'Unknown')}")
    
    # Get current installment from existing data
    existing_installments = google_sheets_service.get_installments(config.get('chit_name'))
    current_installment = len(existing_installments) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Value", f"₹{config.get('full_chit_value', 0):,}")
    with col2:
        st.metric("Installments", f"{current_installment}/{config.get('total_installments', 1)}")
    with col3:
        st.metric("Frequency", config.get('payment_frequency', 'Monthly'))
    with col4:
        st.metric("Per Installment", f"₹{config.get('installment_amount', 0):,.0f}")
    
    st.markdown("---")
    
    # Generate installment schedule
    start_date = datetime.strptime(config.get('start_date'), '%Y-%m-%d').date()
    installment_dates = calculate_installment_dates(
        start_date, 
        config.get('payment_frequency'), 
        config.get('total_installments')
    )
    
    # Get existing installments
    existing_installments = google_sheets_service.get_installments(config.get('chit_name'))
    
    # Create installments DataFrame
    installments_df = pd.DataFrame({
        'Installment': list(range(1, len(installment_dates) + 1)),
        'Due Date': installment_dates,
        'Status': ['Pending'] * len(installment_dates),
        'Amount Paid': [0.0] * len(installment_dates),
        'Auction Amount': [0.0] * len(installment_dates),
        'Dividend': [0.0] * len(installment_dates),
        'Net Payment': [0.0] * len(installment_dates),
        'Winner': [''] * len(installment_dates),
        'Notes': [''] * len(installment_dates)
    })
    
    # Update with existing data
    for inst in existing_installments:
        month_num = inst.get('Month', 0)
        if 1 <= month_num <= len(installments_df):
            idx = month_num - 1
            installments_df.loc[idx, 'Status'] = 'Completed'
            installments_df.loc[idx, 'Amount Paid'] = inst.get('Installment Amount', 0)
            installments_df.loc[idx, 'Auction Amount'] = inst.get('Auction Amount', 0)
            installments_df.loc[idx, 'Dividend'] = inst.get('Dividend', 0)
            installments_df.loc[idx, 'Net Payment'] = inst.get('Net Payment', 0)
            installments_df.loc[idx, 'Winner'] = inst.get('Member Name', '')
            installments_df.loc[idx, 'Notes'] = inst.get('Notes', '')
    
    # Show current progress
    current_installment = config.get('current_installment', 1)
    completed_count = len([i for i in existing_installments])
    
    st.subheader("📈 Progress Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        progress = current_installment / config.get('total_installments', 1)
        st.progress(progress)
        st.write(f"Current Progress: {current_installment}/{config.get('total_installments')} installments")
    
    with col2:
        total_paid = sum(inst.get('Net Payment', 0) for inst in existing_installments)
        st.metric("Total Paid", f"₹{total_paid:,}")
    
    # Installments entry section
    st.subheader("💳 Enter Previous Installments")
    
    # Quick entry form
    with st.form("quick_installment_entry"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            entry_installment = st.selectbox(
                "Installment Number", 
                range(1, current_installment + 1),
                index=min(completed_count, current_installment - 1)
            )
        with col2:
            entry_amount = st.number_input(
                "Amount Paid (₹)", 
                min_value=0, 
                value=int(config.get('installment_amount', 0)),
                step=100
            )
        with col3:
            entry_auction = st.number_input("Auction Amount (₹)", min_value=0, value=0, step=100)
        
        col4, col5 = st.columns(2)
        with col4:
            entry_dividend = st.number_input("Dividend (₹)", min_value=0, value=0, step=10)
        with col5:
            entry_winner = st.text_input("Winner Name", placeholder="Who won this month?")
        
        entry_notes = st.text_area("Notes", placeholder="Additional details about this installment")
        
        if st.form_submit_button("💾 Add/Update Installment", type="primary"):
            net_payment = entry_amount - entry_dividend
            
            installment_data = {
                'chit_name': config.get('chit_name'),
                'month': entry_installment,
                'date': installment_dates[entry_installment - 1].strftime('%Y-%m-%d'),
                'installment_amount': entry_amount,
                'auction_amount': entry_auction,
                'dividend': entry_dividend,
                'net_payment': net_payment,
                'member_name': entry_winner,
                'notes': entry_notes
            }
            
            if google_sheets_service.save_installment(installment_data):
                st.success(f"✅ Installment {entry_installment} saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save installment. Please try again.")
    
    # Display installments table
    st.subheader("📋 Installments Overview")
    
    # Style the dataframe
    def style_installments(df):
        def highlight_status(val):
            if val == 'Completed':
                return 'background-color: #d4edda'
            elif val == 'Pending':
                return 'background-color: #f8d7da'
            return ''
        
        return df.style.map(highlight_status, subset=['Status'])
    
    # Show only up to current installment
    display_df = installments_df.iloc[:current_installment].copy()
    styled_df = style_installments(display_df)
    
    st.dataframe(styled_df, width='stretch')
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Configuration"):
            st.session_state.current_stage = "configuration"
            st.rerun()
    
    with col3:
        if completed_count > 0:
            if st.button("Proceed to Analysis →", type="primary"):
                st.session_state.current_stage = "analysis"
                st.rerun()
        else:
            st.info("Enter at least one installment to proceed to analysis")

def show_analysis_stage():
    """Enhanced analysis interface with comprehensive features matching streamlit_app.py"""
    # Import enhanced functions
    from enhanced_analysis_functions import (
        get_enhanced_analysis_inputs, create_enhanced_config_and_analyze,
        display_enhanced_basic_results, create_enhanced_cashflow_chart,
        get_enhanced_scenario_inputs, perform_enhanced_scenario_analysis,
        create_enhanced_scenario_visualizations, create_enhanced_scenario_table,
        display_enhanced_summary_insights, export_enhanced_analysis
    )
    
    st.title("📈 Stage 3: Enhanced Chit Fund Analysis")
    st.markdown("---")
    
    if not st.session_state.chit_config:
        st.error("⚠️ No configuration found. Please complete previous stages first.")
        return
    
    config = st.session_state.chit_config
    
    # Enhanced analysis inputs in sidebar
    analysis_inputs = get_enhanced_analysis_inputs(config)
    
    # Main analysis button
    if st.sidebar.button("🔍 Run Enhanced Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing your chit fund configuration..."):
            enhanced_config, result, error = create_enhanced_config_and_analyze(config, analysis_inputs)
            
            if error:
                st.error(f"Analysis failed: {error}")
                return
            
            # Store results in session state
            st.session_state.enhanced_config = enhanced_config
            st.session_state.analysis_result = result
    
    # Display results if available
    if 'analysis_result' in st.session_state and 'enhanced_config' in st.session_state:
        enhanced_config = st.session_state.enhanced_config
        result = st.session_state.analysis_result
        
        # Basic results display
        display_enhanced_basic_results(enhanced_config, result)
        
        # Cashflow visualization
        st.header("💰 Cashflow Analysis")
        fig = create_enhanced_cashflow_chart(result)
        st.plotly_chart(fig, use_container_width=True)
        
        # Scenario analysis section
        st.divider()
        
        scenario_inputs = get_enhanced_scenario_inputs(enhanced_config)
        
        if st.button("📈 Run Scenario Analysis", type="secondary", use_container_width=True):
            with st.spinner("Running comprehensive scenario analysis..."):
                scenarios, error = perform_enhanced_scenario_analysis(
                    enhanced_config,
                    scenario_inputs['min_bid'],
                    scenario_inputs['max_bid'],
                    scenario_inputs['num_scenarios']
                )
                
                if error:
                    st.error(f"Scenario analysis failed: {error}")
                else:
                    st.session_state.scenarios = scenarios
        
        # Display scenario results if available
        if 'scenarios' in st.session_state:
            scenarios = st.session_state.scenarios
            
            st.header("📊 Scenario Analysis Results")
            
            # Scenario visualizations
            fig = create_enhanced_scenario_visualizations(scenarios)
            st.plotly_chart(fig, use_container_width=True)
            
            # Scenario table
            st.subheader("📋 Detailed Scenario Breakdown")
            scenario_df = create_enhanced_scenario_table(scenarios)
            st.dataframe(scenario_df, use_container_width=True, hide_index=True)
            
            # Enhanced insights with scenarios
            display_enhanced_summary_insights(enhanced_config, result, scenarios)
            
            # Enhanced export with scenarios
            export_enhanced_analysis(enhanced_config, result, scenarios)
        else:
            # Enhanced insights without scenarios
            display_enhanced_summary_insights(enhanced_config, result)
            
            # Enhanced export without scenarios
            export_enhanced_analysis(enhanced_config, result)
    
    else:
        # Initial state - show instructions
        st.info("👈 Configure your analysis parameters in the sidebar and click 'Run Enhanced Analysis' to begin.")
        
        # Show sample configuration
        st.subheader("📋 Current Configuration Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Installments", config.get('total_installments', 'N/A'))
            st.metric("Chit Value", f"₹{config.get('full_chit_value', 0):,}")
        
        with col2:
            st.metric("Payment Frequency", f"{config.get('chit_frequency_per_year', 'N/A')}/year")
            st.metric("Chit Method", config.get('chit_method', 'N/A'))
        
        with col3:
            st.metric("Start Date", config.get('start_date', 'N/A'))
            
            # Add configuration export
            from enhanced_analysis_functions import export_current_configuration
            export_current_configuration(config, config.get('chit_name', 'Unknown'))
    
    # Navigation footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Installments"):
            st.session_state.current_stage = "installments"
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Analysis"):
            # Clear analysis results
            keys_to_clear = ['analysis_result', 'enhanced_config', 'scenarios']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("🆕 New Configuration"):
            st.session_state.current_stage = "configuration"
            st.session_state.chit_config = {}
            st.rerun()

def apply_custom_css():
    """Apply custom CSS styling to match streamlit_app.py"""
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007acc;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card h4 {
        color: #007acc;
        margin: 0 0 0.5rem 0;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .metric-card h2 {
        color: #2c3e50;
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .success-card {
        border-left-color: #28a745;
    }
    .success-card h4 {
        color: #28a745;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        color: #495057;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #007acc;
        color: white;
    }
    .main-header {
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    .stage-description {
        color: #6c757d;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Apply custom styling
    apply_custom_css()
    
    # Sidebar navigation
    st.sidebar.title("🏦 Chit Fund Analyzer Pro")
    st.sidebar.markdown("---")
    
    if st.session_state.authenticated:
        # Show authenticated menu
        st.sidebar.success("✅ Authenticated")
        
        # Stage navigation
        stages = {
            "⚙️ Configuration": "configuration",
            "📅 Installments": "installments", 
            "📈 Analysis": "analysis"
        }
        
        st.sidebar.subheader("📋 Workflow Stages")
        
        for stage_name, stage_key in stages.items():
            # Show checkmark for completed stages
            if stage_key == "configuration" and st.session_state.chit_config:
                stage_display = f"✅ {stage_name}"
            elif stage_key == "installments" and st.session_state.chit_config:
                installments = google_sheets_service.get_installments(st.session_state.chit_config.get('chit_name', ''))
                stage_display = f"{'✅' if installments else '⏳'} {stage_name}"
            elif stage_key == "analysis" and st.session_state.chit_config:
                stage_display = f"📈 {stage_name}"
            else:
                stage_display = f"⭕ {stage_name}"
            
            if st.sidebar.button(stage_display, key=f"nav_{stage_key}"):
                if stage_key == "installments" and not st.session_state.chit_config:
                    st.sidebar.error("Complete configuration first!")
                elif stage_key == "analysis" and not st.session_state.chit_config:
                    st.sidebar.error("Complete previous stages first!")
                else:
                    st.session_state.current_stage = stage_key
                    st.rerun()
        
        st.sidebar.markdown("---")
        
        # Current config info
        if st.session_state.chit_config:
            st.sidebar.subheader("📊 Current Config")
            st.sidebar.write(f"**Name:** {st.session_state.chit_config.get('chit_name', 'N/A')}")
            st.sidebar.write(f"**Value:** ₹{st.session_state.chit_config.get('full_chit_value', 0):,}")
            st.sidebar.write(f"**Frequency:** {st.session_state.chit_config.get('payment_frequency', 'N/A')}")
        
        # Data access
        if st.session_state.spreadsheet_created:
            spreadsheet_url = google_sheets_service.get_spreadsheet_url()
            if spreadsheet_url:
                st.sidebar.markdown("---")
                st.sidebar.markdown("📊 **Your Data:**")
                st.sidebar.markdown(f"[Open Google Sheets]({spreadsheet_url})")
        
        # Logout option
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", type="secondary"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            google_sheets_service.logout()
            st.rerun()
    
    else:
        # Show login prompt
        st.sidebar.info("Please authenticate to continue")
        if st.sidebar.button("🔑 Go to Authentication"):
            st.session_state.current_stage = "authentication"
            st.rerun()
    
    # Display current stage
    if st.session_state.current_stage == "authentication":
        show_authentication_page()
    elif st.session_state.authenticated:
        if st.session_state.current_stage == "configuration":
            show_configuration_stage()
        elif st.session_state.current_stage == "installments":
            show_installments_stage()
        elif st.session_state.current_stage == "analysis":
            show_analysis_stage()
    else:
        show_authentication_page()

# Main application
if __name__ == "__main__":
    main()