"""
Chit Fund Analyzer with Automatic Google OAuth
Multi-page Streamlit application for analyzing chit fund investments
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer, ScenarioAnalyzer
from google_sheets_service_auto import google_sheets_service
import json

# Page config
st.set_page_config(
    page_title="Chit Fund Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Authentication"
if 'spreadsheet_created' not in st.session_state:
    st.session_state.spreadsheet_created = False

def show_authentication_page():
    """Display the automatic OAuth authentication page"""
    st.title("🔐 Google Sheets Authentication")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### Welcome to Chit Fund Analyzer! 
        
        This app helps you analyze chit fund investments by storing your data in Google Sheets.
        
        **What happens when you authenticate:**
        - Your browser will open to Google's authentication page
        - You'll be asked to sign in to your Google account
        - Grant permission to access Google Sheets and Drive
        - The app will automatically handle the rest!
        
        **Your data security:**
        - Your data stays in your own Google Drive
        - No data is stored on our servers
        - You can revoke access anytime through Google Account settings
        """)
        
        st.markdown("---")
        
        # Check authentication status
        if google_sheets_service.is_authenticated():
            st.success("✅ Already authenticated!")
            if st.button("Continue to App", type="primary", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.current_page = "Configuration"
                st.rerun()
        else:
            st.info("Click below to start automatic authentication")
            
            if st.button("🔑 Authenticate with Google", type="primary", use_container_width=True):
                with st.spinner("Starting authentication process..."):
                    
                    # Check if credentials file exists
                    import os
                    if not os.path.exists('oauth_credentials.json'):
                        st.error("""
                        ❌ **OAuth credentials file not found!**
                        
                        Please ensure you have placed your `oauth_credentials.json` file in the project directory.
                        """)
                        return
                    
                    # Perform automatic authentication
                    if google_sheets_service.authenticate_automatically():
                        st.success("✅ Authentication successful!")
                        st.session_state.authenticated = True
                        st.session_state.current_page = "Configuration"
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("""
                        ❌ **Authentication failed!**
                        
                        Please check:
                        - Your OAuth credentials file is valid
                        - Your browser allows popups from this app
                        - Your internet connection is stable
                        
                        If problems persist, try refreshing the page and authenticating again.
                        """)

def show_configuration_page():
    """Display the chit fund configuration page"""
    st.title("⚙️ Chit Fund Configuration")
    st.markdown("---")
    
    # Setup spreadsheet if not done
    if not st.session_state.spreadsheet_created:
        with st.spinner("Setting up your Google Sheets..."):
            spreadsheet_name = "Chit Fund Analyzer Data"
            if google_sheets_service.create_or_get_spreadsheet(spreadsheet_name):
                st.session_state.spreadsheet_created = True
                st.success(f"✅ Google Sheets setup complete!")
                
                # Show spreadsheet link
                spreadsheet_url = google_sheets_service.get_spreadsheet_url()
                if spreadsheet_url:
                    st.info(f"📊 **Your Data Spreadsheet:** [Open in Google Sheets]({spreadsheet_url})")
            else:
                st.error("❌ Failed to setup Google Sheets. Please check authentication.")
                return
    
    # Load existing configurations
    existing_configs = google_sheets_service.get_chit_configurations()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Add New Chit Fund")
        
        with st.form("chit_config_form"):
            chit_name = st.text_input("Chit Fund Name*", placeholder="e.g., Monthly Savings Chit")
            
            col_amount, col_duration = st.columns(2)
            with col_amount:
                total_amount = st.number_input("Total Amount (₹)*", min_value=1000, value=100000, step=1000)
            with col_duration:
                duration_months = st.number_input("Duration (Months)*", min_value=6, max_value=120, value=24)
            
            monthly_installment = st.number_input(
                "Monthly Installment (₹)*", 
                min_value=100, 
                value=int(total_amount/duration_months) if duration_months > 0 else 1000,
                step=100
            )
            
            col_interest, col_method = st.columns(2)
            with col_interest:
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=50.0, value=12.0, step=0.1)
            with col_method:
                chit_method = st.selectbox("Chit Method", 
                    ["Auction", "Lucky Draw", "Serial Basis", "Dividend Method"])
            
            start_date = st.date_input("Start Date", value=date.today())
            
            submitted = st.form_submit_button("💾 Save Configuration", type="primary")
            
            if submitted:
                if chit_name and total_amount and duration_months and monthly_installment:
                    config_data = {
                        'chit_name': chit_name,
                        'total_amount': total_amount,
                        'duration_months': duration_months,
                        'monthly_installment': monthly_installment,
                        'interest_rate': interest_rate,
                        'chit_method': chit_method,
                        'start_date': start_date.strftime('%Y-%m-%d')
                    }
                    
                    if google_sheets_service.save_chit_configuration(config_data):
                        st.success(f"✅ Configuration saved for '{chit_name}'!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save configuration. Please try again.")
                else:
                    st.error("⚠️ Please fill all required fields marked with *")
    
    with col2:
        st.subheader("📋 Existing Chit Funds")
        
        if existing_configs:
            for i, config in enumerate(existing_configs):
                with st.expander(f"💰 {config.get('Chit Name', 'Unnamed')}"):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"**Total Amount:** ₹{config.get('Total Amount', 0):,}")
                        st.write(f"**Duration:** {config.get('Duration (Months)', 0)} months")
                        st.write(f"**Method:** {config.get('Chit Method', 'N/A')}")
                    with col_info2:
                        st.write(f"**Monthly Installment:** ₹{config.get('Monthly Installment', 0):,}")
                        st.write(f"**Interest Rate:** {config.get('Interest Rate (%)', 0)}%")
                        st.write(f"**Start Date:** {config.get('Start Date', 'N/A')}")
        else:
            st.info("No chit funds configured yet. Add your first chit fund using the form on the left.")

def show_installments_page():
    """Display the installments tracking page"""
    st.title("📅 Installments Tracking")
    st.markdown("---")
    
    # Get existing configurations
    existing_configs = google_sheets_service.get_chit_configurations()
    
    if not existing_configs:
        st.warning("⚠️ No chit funds configured yet. Please add a chit fund in the Configuration page first.")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💳 Add New Installment")
        
        with st.form("installment_form"):
            # Chit selection
            chit_names = [config.get('Chit Name', '') for config in existing_configs]
            selected_chit = st.selectbox("Select Chit Fund*", chit_names)
            
            col_month, col_date = st.columns(2)
            with col_month:
                month_number = st.number_input("Month Number*", min_value=1, max_value=120, value=1)
            with col_date:
                installment_date = st.date_input("Installment Date*", value=date.today())
            
            col_inst, col_auction = st.columns(2)
            with col_inst:
                installment_amount = st.number_input("Installment Amount (₹)*", min_value=0, value=1000, step=100)
            with col_auction:
                auction_amount = st.number_input("Auction Amount (₹)", min_value=0, value=0, step=100)
            
            col_dividend, col_net = st.columns(2)
            with col_dividend:
                dividend = st.number_input("Dividend (₹)", min_value=0, value=0, step=10)
            with col_net:
                net_payment = installment_amount - dividend
                st.number_input("Net Payment (₹)", value=net_payment, disabled=True)
            
            member_name = st.text_input("Member Name", placeholder="Who won the auction (if any)")
            notes = st.text_area("Notes", placeholder="Additional notes about this installment")
            
            submitted = st.form_submit_button("💾 Save Installment", type="primary")
            
            if submitted:
                if selected_chit and installment_amount:
                    installment_data = {
                        'chit_name': selected_chit,
                        'month': month_number,
                        'date': installment_date.strftime('%Y-%m-%d'),
                        'installment_amount': installment_amount,
                        'auction_amount': auction_amount,
                        'dividend': dividend,
                        'net_payment': net_payment,
                        'member_name': member_name,
                        'notes': notes
                    }
                    
                    if google_sheets_service.save_installment(installment_data):
                        st.success(f"✅ Installment saved for '{selected_chit}' - Month {month_number}!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save installment. Please try again.")
                else:
                    st.error("⚠️ Please fill all required fields marked with *")
    
    with col2:
        st.subheader("📊 Installment History")
        
        # Filter by chit fund
        chit_filter = st.selectbox("Filter by Chit Fund", ["All"] + chit_names, key="installment_filter")
        
        # Get installments
        if chit_filter == "All":
            installments = google_sheets_service.get_installments()
        else:
            installments = google_sheets_service.get_installments(chit_filter)
        
        if installments:
            # Convert to DataFrame for better display
            df = pd.DataFrame(installments)
            
            # Display summary
            st.write(f"**Total Installments:** {len(installments)}")
            if 'Net Payment' in df.columns:
                total_paid = df['Net Payment'].sum()
                st.write(f"**Total Amount Paid:** ₹{total_paid:,}")
            
            # Display recent installments
            st.write("**Recent Installments:**")
            display_columns = ['Chit Name', 'Month', 'Date', 'Installment Amount', 'Dividend', 'Net Payment']
            available_columns = [col for col in display_columns if col in df.columns]
            
            if available_columns:
                recent_installments = df[available_columns].tail(10)
                st.dataframe(recent_installments, use_container_width=True)
            else:
                st.write("No installment data to display.")
        else:
            st.info("No installments recorded yet.")

def show_analysis_page():
    """Display the analysis page"""
    st.title("📈 Chit Fund Analysis")
    st.markdown("---")
    
    # Get existing configurations
    existing_configs = google_sheets_service.get_chit_configurations()
    
    if not existing_configs:
        st.warning("⚠️ No chit funds configured yet. Please add a chit fund in the Configuration page first.")
        return
    
    # Chit fund selection
    chit_names = [config.get('Chit Name', '') for config in existing_configs]
    selected_chit = st.selectbox("Select Chit Fund for Analysis", chit_names)
    
    if selected_chit:
        # Get configuration for selected chit
        config = next((c for c in existing_configs if c.get('Chit Name') == selected_chit), None)
        
        if config:
            # Create ChitFundConfig object
            chit_config = ChitFundConfig(
                total_amount=config.get('Total Amount', 0),
                duration_months=config.get('Duration (Months)', 12),
                monthly_installment=config.get('Monthly Installment', 0),
                interest_rate=config.get('Interest Rate (%)', 12)
            )
            
            # Get installment history
            installments = google_sheets_service.get_installments(selected_chit)
            
            # Create tabs for different analyses
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 IRR Analysis", "📈 Scenarios", "📋 Detailed View"])
            
            with tab1:
                st.subheader(f"Overview: {selected_chit}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Amount", f"₹{chit_config.total_amount:,}")
                with col2:
                    st.metric("Duration", f"{chit_config.duration_months} months")
                with col3:
                    st.metric("Monthly Installment", f"₹{chit_config.monthly_installment:,}")
                with col4:
                    st.metric("Interest Rate", f"{chit_config.interest_rate}%")
                
                # Progress tracking
                if installments:
                    months_completed = len(installments)
                    progress = months_completed / chit_config.duration_months
                    
                    st.subheader("Progress Tracking")
                    st.progress(progress)
                    st.write(f"Completed: {months_completed}/{chit_config.duration_months} months ({progress*100:.1f}%)")
                    
                    # Payment summary
                    total_paid = sum(inst.get('Net Payment', 0) for inst in installments)
                    expected_paid = months_completed * chit_config.monthly_installment
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Paid", f"₹{total_paid:,}")
                    with col2:
                        st.metric("Expected Paid", f"₹{expected_paid:,}")
                    with col3:
                        difference = total_paid - expected_paid
                        st.metric("Difference", f"₹{difference:,}", delta=difference)
            
            with tab2:
                st.subheader("IRR Analysis")
                
                # Create analyzer
                analyzer = ChitFundAnalyzer(chit_config)
                
                # Different scenarios
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Best Case Scenario (Win in Month 1)**")
                    best_case = analyzer.calculate_irr_scenario(win_month=1)
                    st.metric("IRR", f"{best_case:.2f}%")
                    
                    st.write("**Worst Case Scenario (Win in Last Month)**")
                    worst_case = analyzer.calculate_irr_scenario(win_month=chit_config.duration_months)
                    st.metric("IRR", f"{worst_case:.2f}%")
                
                with col2:
                    st.write("**Average Case Scenario (Win in Middle)**")
                    avg_case = analyzer.calculate_irr_scenario(win_month=chit_config.duration_months//2)
                    st.metric("IRR", f"{avg_case:.2f}%")
                    
                    # If actual installments exist, calculate actual IRR
                    if installments:
                        st.write("**Current Scenario (Based on Actual Data)**")
                        # This would need actual cash flows from installments
                        st.info("Actual IRR calculation would require complete cash flow data")
                
                # IRR vs win month chart
                st.subheader("IRR vs Winning Month")
                months = list(range(1, chit_config.duration_months + 1))
                irr_values = [analyzer.calculate_irr_scenario(month) for month in months]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months, y=irr_values, mode='lines+markers', name='IRR'))
                fig.update_layout(
                    title="IRR vs Winning Month",
                    xaxis_title="Winning Month",
                    yaxis_title="IRR (%)",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("Scenario Analysis")
                
                # Create scenario analyzer
                scenario_analyzer = ScenarioAnalyzer(chit_config)
                
                # Interest rate scenarios
                st.write("**Interest Rate Scenarios**")
                rates = [8, 10, 12, 15, 18, 20]
                scenarios = scenario_analyzer.compare_interest_rates(rates)
                
                df_scenarios = pd.DataFrame(scenarios)
                st.dataframe(df_scenarios, use_container_width=True)
                
                # Duration scenarios
                st.write("**Duration Scenarios**")
                durations = [12, 18, 24, 30, 36]
                duration_scenarios = scenario_analyzer.compare_durations(durations)
                
                df_durations = pd.DataFrame(duration_scenarios)
                st.dataframe(df_durations, use_container_width=True)
            
            with tab4:
                st.subheader("Detailed Installment Data")
                
                if installments:
                    df = pd.DataFrame(installments)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"{selected_chit}_installments.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No installment data available yet.")

def main():
    """Main application function"""
    
    # Sidebar navigation
    st.sidebar.title("🏦 Chit Fund Analyzer")
    st.sidebar.markdown("---")
    
    if st.session_state.authenticated:
        # Show authenticated menu
        st.sidebar.success("✅ Authenticated with Google")
        
        # Navigation menu
        pages = {
            "⚙️ Configuration": "Configuration",
            "📅 Installments": "Installments", 
            "📈 Analysis": "Analysis"
        }
        
        for page_name, page_key in pages.items():
            if st.sidebar.button(page_name, use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.sidebar.markdown("---")
        
        # Show current spreadsheet
        if st.session_state.spreadsheet_created:
            spreadsheet_url = google_sheets_service.get_spreadsheet_url()
            if spreadsheet_url:
                st.sidebar.markdown("📊 **Your Data:**")
                st.sidebar.markdown(f"[Open Google Sheets]({spreadsheet_url})")
        
        # Logout option
        if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
            google_sheets_service.logout()
            st.session_state.authenticated = False
            st.session_state.current_page = "Authentication"
            st.session_state.spreadsheet_created = False
            st.rerun()
    
    else:
        # Show login prompt
        st.sidebar.info("Please authenticate to continue")
        if st.sidebar.button("🔑 Go to Authentication", use_container_width=True):
            st.session_state.current_page = "Authentication"
            st.rerun()
    
    # Display current page
    if st.session_state.current_page == "Authentication":
        show_authentication_page()
    elif st.session_state.authenticated:
        if st.session_state.current_page == "Configuration":
            show_configuration_page()
        elif st.session_state.current_page == "Installments":
            show_installments_page()
        elif st.session_state.current_page == "Analysis":
            show_analysis_page()
    else:
        show_authentication_page()

if __name__ == "__main__":
    main()