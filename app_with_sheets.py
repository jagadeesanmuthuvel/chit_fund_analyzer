"""
Multi-page Chit Fund Analyzer Streamlit App with Google Sheets Integration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
from typing import Dict, List, Optional

# Import custom modules
from google_sheets_service import sheets_service
from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer, ScenarioAnalyzer

# Configure page
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
    st.session_state.current_page = 'Authentication'
if 'spreadsheet_name' not in st.session_state:
    st.session_state.spreadsheet_name = None
if 'selected_chit' not in st.session_state:
    st.session_state.selected_chit = None


def show_authentication_page():
    """Display Google OAuth authentication page"""
    st.title("🔐 Google OAuth Authentication")
    st.write("Authenticate with your Google account to access Google Sheets directly.")
    
    # Information section
    with st.expander("📋 Setup Instructions", expanded=True):
        st.markdown("""
        ### How to get Google OAuth credentials:
        
        1. **Go to Google Cloud Console**: Visit [Google Cloud Console](https://console.cloud.google.com/)
        2. **Create/Select Project**: Create a new project or select existing one
        3. **Enable APIs**: Enable Google Sheets API and Google Drive API
        4. **Create OAuth Client**: 
           - Go to APIs & Services → Credentials
           - Click "Create Credentials" → "OAuth 2.0 Client IDs"
           - Application type: "Desktop application"
           - Name: "Chit Fund Analyzer OAuth"
        5. **Download JSON**: Download the OAuth client credentials
        6. **Copy JSON Content**: Paste the entire JSON content below
        
        ### Benefits of OAuth:
        - ✅ Access your personal Google Drive
        - ✅ Create spreadsheets directly in your Drive
        - ✅ No manual spreadsheet sharing required
        - ✅ Familiar Google authentication flow
        """)
    
    # Authentication form
    st.subheader("🔑 Enter OAuth Credentials")
    
    # OAuth credentials input
    oauth_credentials_json = st.text_area(
        "OAuth Client Credentials (JSON)",
        height=200,
        placeholder='{\n  "installed": {\n    "client_id": "your-client-id",\n    "client_secret": "your-secret",\n    ...\n  }\n}',
        help="Paste the OAuth client credentials JSON from Google Cloud Console"
    )
    
    spreadsheet_name = st.text_input(
        "Spreadsheet Name",
        value="Chit Fund Analyzer Data",
        help="Name for your Google Sheets spreadsheet (will be created in your Drive)"
    )
    
    # OAuth authentication flow
    if 'oauth_auth_url' not in st.session_state:
        st.session_state.oauth_auth_url = None
    if 'oauth_config' not in st.session_state:
        st.session_state.oauth_config = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start OAuth Flow", type="primary"):
            if not oauth_credentials_json.strip():
                st.error("Please enter your OAuth credentials first")
            else:
                try:
                    import json
                    oauth_config = json.loads(oauth_credentials_json)
                    
                    with st.spinner("Initializing OAuth flow..."):
                        success, auth_url = sheets_service.authenticate_with_oauth(oauth_config)
                        
                        if success and auth_url:
                            st.session_state.oauth_auth_url = auth_url
                            st.session_state.oauth_config = oauth_config
                            st.success("✅ OAuth flow started!")
                            st.info("Please complete the authorization in the next step.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to start OAuth flow. Check your credentials.")
                
                except json.JSONDecodeError:
                    st.error("Invalid JSON format. Please check your OAuth credentials.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("🧪 Test OAuth Config"):
            if not oauth_credentials_json.strip():
                st.error("Please enter OAuth credentials first")
            else:
                try:
                    import json
                    oauth_config = json.loads(oauth_credentials_json)
                    
                    # Check if it has the right structure
                    if 'installed' in oauth_config or 'web' in oauth_config:
                        st.success("✅ OAuth configuration format is valid!")
                    else:
                        st.error("❌ Invalid OAuth configuration format")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format")
    
    # Show authorization URL and code input
    if st.session_state.oauth_auth_url:
        st.subheader("🔗 Authorization Required")
        st.write("**Step 1**: Click the link below to authorize the application:")
        st.link_button("🔐 Authorize Application", st.session_state.oauth_auth_url)
        
        st.write("**Step 2**: Copy the authorization code and paste it below:")
        auth_code = st.text_input(
            "Authorization Code",
            help="After clicking the link above, you'll get a code. Paste it here."
        )
        
        if st.button("✅ Complete Authentication", type="primary"):
            if not auth_code.strip():
                st.error("Please enter the authorization code")
            else:
                with st.spinner("Completing OAuth authentication..."):
                    success = sheets_service.complete_oauth_flow(st.session_state.oauth_config, auth_code)
                    
                    if success:
                        # Create/open spreadsheet
                        spreadsheet_success = sheets_service.create_or_get_spreadsheet(spreadsheet_name, try_create=True)
                        
                        if spreadsheet_success:
                            st.session_state.authenticated = True
                            st.session_state.spreadsheet_name = spreadsheet_name
                            st.session_state.current_page = 'Configuration'
                            st.success("🎉 OAuth authentication successful!")
                            st.info(f"📊 Spreadsheet: {spreadsheet_name}")
                            if sheets_service.get_spreadsheet_url():
                                st.info(f"🔗 URL: {sheets_service.get_spreadsheet_url()}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Failed to create/access spreadsheet")
                    else:
                        st.error("❌ OAuth authentication failed. Please try again.")
    
    # Security note
    st.info("🔒 **Security Note**: Your credentials are only used for this session and are not stored permanently.")


def show_configuration_page():
    """Display chit configuration input page"""
    st.title("📊 Chit Fund Configuration")
    
    # Header with spreadsheet info
    if st.session_state.spreadsheet_name:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"📊 Connected to: **{st.session_state.spreadsheet_name}**")
        with col2:
            if sheets_service.get_spreadsheet_url():
                st.link_button("🔗 Open Sheets", sheets_service.get_spreadsheet_url())
        with col3:
            if st.button("🔄 Switch Sheets"):
                st.session_state.authenticated = False
                st.session_state.current_page = 'Authentication'
                st.rerun()
    
    st.write("Configure your chit fund details and add previous installment data.")
    
    # Main configuration form
    with st.form("chit_config_form"):
        st.subheader("🏦 Basic Chit Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chit_name = st.text_input(
                "Chit Fund Name *",
                placeholder="e.g., Family Chit 2024",
                help="Unique name for this chit fund"
            )
            
            chit_amount = st.number_input(
                "Total Chit Amount (₹) *",
                min_value=1000,
                max_value=10000000,
                value=100000,
                step=1000,
                help="Total amount of the chit fund"
            )
            
            total_months = st.number_input(
                "Total Months *",
                min_value=6,
                max_value=120,
                value=20,
                help="Duration of the chit fund in months"
            )
        
        with col2:
            monthly_installment = st.number_input(
                "Monthly Installment (₹) *",
                min_value=100,
                max_value=1000000,
                value=int(chit_amount / total_months) if chit_amount and total_months else 5000,
                step=100,
                help="Fixed monthly installment amount"
            )
            
            commission_rate = st.number_input(
                "Commission Rate (%) *",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.1,
                help="Commission rate charged by organizer"
            )
            
            chit_method = st.selectbox(
                "Chit Method *",
                ["Auction/Bidding", "Lucky Draw", "Fixed Order"],
                help="Method used to determine monthly winners"
            )
        
        # Description
        description = st.text_area(
            "Description (Optional)",
            placeholder="Add any additional details about this chit fund...",
            height=100
        )
        
        st.subheader("📅 Previous Installments")
        st.write("Add details of installments that have already been completed:")
        
        # Dynamic installment input
        if 'installments' not in st.session_state:
            st.session_state.installments = []
        
        # Add installment button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.form_submit_button("➕ Add Installment", type="secondary"):
                st.session_state.installments.append({
                    'month': len(st.session_state.installments) + 1,
                    'date': date.today(),
                    'amount_paid': monthly_installment,
                    'bid_amount': 0,
                    'winner': '',
                    'notes': ''
                })
                st.rerun()
        
        with col2:
            if st.form_submit_button("🗑️ Clear All", type="secondary"):
                st.session_state.installments = []
                st.rerun()
        
        # Display installments
        if st.session_state.installments:
            st.write("**Current Installments:**")
            
            for i, installment in enumerate(st.session_state.installments):
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**Month {installment['month']}**")
                    
                    with col2:
                        installment['date'] = st.date_input(
                            "Date",
                            value=installment['date'],
                            key=f"date_{i}"
                        )
                    
                    with col3:
                        installment['amount_paid'] = st.number_input(
                            "Amount Paid (₹)",
                            value=installment['amount_paid'],
                            min_value=0,
                            key=f"amount_{i}"
                        )
                    
                    with col4:
                        installment['bid_amount'] = st.number_input(
                            "Bid Amount (₹)",
                            value=installment['bid_amount'],
                            min_value=0,
                            key=f"bid_{i}"
                        )
                    
                    with col5:
                        installment['winner'] = st.text_input(
                            "Winner",
                            value=installment['winner'],
                            key=f"winner_{i}"
                        )
                    
                    with col6:
                        if st.button("❌", key=f"remove_{i}", help="Remove this installment"):
                            st.session_state.installments.pop(i)
                            st.rerun()
                    
                    # Notes for this installment
                    installment['notes'] = st.text_input(
                        f"Notes for Month {installment['month']}",
                        value=installment['notes'],
                        key=f"notes_{i}"
                    )
                    
                    st.divider()
        else:
            st.info("No installments added yet. Click 'Add Installment' to add previous installment data.")
        
        # Save button
        st.subheader("💾 Save Configuration")
        submitted = st.form_submit_button("💾 Save to Google Sheets", type="primary")
        
        if submitted:
            # Validation
            if not chit_name.strip():
                st.error("Please enter a chit fund name")
                return
            
            if not all([chit_amount, total_months, monthly_installment]):
                st.error("Please fill in all required fields")
                return
            
            # Prepare configuration data
            config_data = {
                'chit_name': chit_name.strip(),
                'chit_amount': chit_amount,
                'total_months': total_months,
                'monthly_installment': monthly_installment,
                'commission_rate': commission_rate,
                'chit_method': chit_method,
                'description': description.strip(),
                'status': 'Active'
            }
            
            # Prepare installment data
            installment_data = []
            for installment in st.session_state.installments:
                installment_data.append({
                    'chit_name': chit_name.strip(),
                    'month': installment['month'],
                    'installment_date': installment['date'].strftime('%Y-%m-%d'),
                    'amount_paid': installment['amount_paid'],
                    'bid_amount': installment['bid_amount'],
                    'winner': installment['winner'],
                    'commission': installment['bid_amount'] * commission_rate / 100 if installment['bid_amount'] else 0,
                    'net_amount': installment['bid_amount'] - (installment['bid_amount'] * commission_rate / 100) if installment['bid_amount'] else 0,
                    'payment_status': 'Paid',
                    'notes': installment['notes']
                })
            
            # Save to Google Sheets
            with st.spinner("Saving to Google Sheets..."):
                config_saved = sheets_service.save_chit_configuration(config_data)
                installments_saved = True
                
                if installment_data:
                    installments_saved = sheets_service.save_installment_data(installment_data)
                
                if config_saved and installments_saved:
                    st.success("✅ Configuration saved successfully!")
                    st.session_state.installments = []  # Clear form
                    st.session_state.current_page = 'Analysis'
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to save configuration. Please try again.")


def show_analysis_page():
    """Display chit selection and analysis page"""
    st.title("📈 Chit Fund Analysis")
    
    # Header
    if st.session_state.spreadsheet_name:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.info(f"📊 Data Source: **{st.session_state.spreadsheet_name}**")
        with col2:
            if sheets_service.get_spreadsheet_url():
                st.link_button("🔗 Open Sheets", sheets_service.get_spreadsheet_url())
        with col3:
            if st.button("➕ Add New Chit"):
                st.session_state.current_page = 'Configuration'
                st.rerun()
        with col4:
            if st.button("🔄 Switch Sheets"):
                st.session_state.authenticated = False
                st.session_state.current_page = 'Authentication'
                st.rerun()
    
    # Get available chits
    chit_names = sheets_service.get_chit_names()
    
    if not chit_names:
        st.warning("No chit funds found. Please add a chit fund configuration first.")
        if st.button("➕ Add First Chit Fund"):
            st.session_state.current_page = 'Configuration'
            st.rerun()
        return
    
    # Chit selection
    selected_chit = st.selectbox(
        "📋 Select Chit Fund",
        chit_names,
        key="chit_selector",
        help="Choose a chit fund to analyze"
    )
    
    if selected_chit:
        # Load configuration and history
        config_data = sheets_service.get_chit_configuration(selected_chit)
        installment_history = sheets_service.get_installment_history(selected_chit)
        
        if not config_data:
            st.error("Failed to load chit configuration")
            return
        
        # Display basic info
        with st.expander("📊 Chit Fund Information", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Amount", f"₹{config_data['chit_amount']:,.0f}")
                st.metric("Total Months", config_data['total_months'])
            
            with col2:
                st.metric("Monthly Installment", f"₹{config_data['monthly_installment']:,.0f}")
                st.metric("Commission Rate", f"{config_data['commission_rate']}%")
            
            with col3:
                st.metric("Method", config_data['chit_method'])
                st.metric("Status", config_data['status'])
            
            with col4:
                completed_months = len(installment_history)
                remaining_months = config_data['total_months'] - completed_months
                st.metric("Completed Months", completed_months)
                st.metric("Remaining Months", remaining_months)
        
        # Create ChitFundConfig for analysis
        try:
            # Prepare installment amounts for the analyzer
            installment_amounts = []
            for month in range(1, config_data['total_months'] + 1):
                # Find if this month has data
                month_data = next((inst for inst in installment_history if inst['month'] == month), None)
                if month_data:
                    installment_amounts.append(month_data['amount_paid'])
                else:
                    installment_amounts.append(config_data['monthly_installment'])  # Default amount
            
            # Create configuration object
            chit_config = ChitFundConfig(
                chit_amount=config_data['chit_amount'],
                total_months=config_data['total_months'],
                installment_amounts=installment_amounts,
                commission_rate=config_data['commission_rate'] / 100  # Convert to decimal
            )
            
            # Create analyzer
            analyzer = ChitFundAnalyzer(chit_config)
            
            # Analysis tabs
            tab1, tab2, tab3, tab4 = st.tabs(["💰 Current Analysis", "📊 Scenario Analysis", "📈 Cashflow", "📋 History"])
            
            with tab1:
                st.subheader("Current Investment Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Bid amount input
                    st.write("**Enter your bid amount for analysis:**")
                    bid_amount = st.number_input(
                        "Your Bid Amount (₹)",
                        min_value=0,
                        max_value=int(config_data['chit_amount']),
                        value=0,
                        step=1000,
                        help="Amount you plan to bid (0 for never winning scenario)"
                    )
                    
                    winning_month = st.number_input(
                        "Winning Month",
                        min_value=1,
                        max_value=config_data['total_months'],
                        value=min(10, config_data['total_months']),
                        help="Month when you plan to win the chit"
                    )
                
                with col2:
                    if bid_amount >= 0:
                        # Calculate IRR
                        irr_result = analyzer.calculate_irr_for_bid(bid_amount, winning_month)
                        
                        if irr_result['success']:
                            irr_value = irr_result['irr'] * 100
                            
                            # Color based on IRR value
                            if irr_value > 15:
                                color = "green"
                            elif irr_value > 10:
                                color = "orange"
                            else:
                                color = "red"
                            
                            st.markdown(f"### IRR: <span style='color:{color}'>{irr_value:.2f}%</span>", 
                                      unsafe_allow_html=True)
                            
                            # Additional metrics
                            net_amount = bid_amount - (bid_amount * config_data['commission_rate'] / 100)
                            total_paid = winning_month * config_data['monthly_installment']
                            
                            st.metric("Net Amount Received", f"₹{net_amount:,.0f}")
                            st.metric("Total Amount Paid", f"₹{total_paid:,.0f}")
                            st.metric("Net Benefit", f"₹{net_amount - total_paid:,.0f}")
                        else:
                            st.error("Unable to calculate IRR. Please check your inputs.")
                
                # Investment insights
                with st.expander("💡 Investment Insights"):
                    if bid_amount > 0:
                        st.write(f"""
                        **Analysis Summary:**
                        - **Bid Amount**: ₹{bid_amount:,.0f}
                        - **Winning Month**: {winning_month}
                        - **Commission**: ₹{bid_amount * config_data['commission_rate'] / 100:,.0f} ({config_data['commission_rate']}%)
                        - **Net Received**: ₹{bid_amount - (bid_amount * config_data['commission_rate'] / 100):,.0f}
                        
                        **Risk Assessment:**
                        - Lower IRR indicates better return potential
                        - Consider market interest rates for comparison
                        - Factor in liquidity needs and risk tolerance
                        """)
                    else:
                        st.write("Enter a bid amount to see detailed analysis")
            
            with tab2:
                st.subheader("Scenario Analysis")
                
                # Scenario parameters
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    min_bid = st.number_input(
                        "Minimum Bid (₹)",
                        min_value=0,
                        max_value=int(config_data['chit_amount']),
                        value=int(config_data['chit_amount'] * 0.1),
                        step=1000
                    )
                
                with col2:
                    max_bid = st.number_input(
                        "Maximum Bid (₹)",
                        min_value=min_bid,
                        max_value=int(config_data['chit_amount']),
                        value=int(config_data['chit_amount'] * 0.5),
                        step=1000
                    )
                
                with col3:
                    target_month = st.number_input(
                        "Target Winning Month",
                        min_value=1,
                        max_value=config_data['total_months'],
                        value=min(10, config_data['total_months'])
                    )
                
                if st.button("🔍 Analyze Scenarios"):
                    # Create scenario analyzer
                    scenario_analyzer = ScenarioAnalyzer(chit_config)
                    
                    with st.spinner("Analyzing scenarios..."):
                        # Generate scenarios
                        bid_range = range(min_bid, max_bid + 1000, 5000)
                        scenarios = []
                        
                        for bid in bid_range:
                            irr_result = analyzer.calculate_irr_for_bid(bid, target_month)
                            if irr_result['success']:
                                net_amount = bid - (bid * config_data['commission_rate'] / 100)
                                scenarios.append({
                                    'Bid Amount': bid,
                                    'IRR (%)': irr_result['irr'] * 100,
                                    'Net Amount': net_amount,
                                    'Commission': bid * config_data['commission_rate'] / 100
                                })
                        
                        if scenarios:
                            # Create DataFrame
                            df_scenarios = pd.DataFrame(scenarios)
                            
                            # Plot IRR vs Bid Amount
                            fig = px.line(
                                df_scenarios,
                                x='Bid Amount',
                                y='IRR (%)',
                                title=f'IRR vs Bid Amount (Winning Month: {target_month})',
                                labels={'Bid Amount': 'Bid Amount (₹)', 'IRR (%)': 'IRR (%)'}
                            )
                            fig.add_hline(y=12, line_dash="dash", line_color="red", 
                                        annotation_text="Bank FD Rate (~12%)")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Data table
                            st.subheader("Detailed Scenario Data")
                            st.dataframe(df_scenarios, use_container_width=True)
                            
                            # Download option
                            csv = df_scenarios.to_csv(index=False)
                            st.download_button(
                                label="📊 Download Scenarios as CSV",
                                data=csv,
                                file_name=f"{selected_chit}_scenarios.csv",
                                mime="text/csv"
                            )
                        else:
                            st.error("Unable to generate scenarios. Please check your parameters.")
            
            with tab3:
                st.subheader("Cashflow Analysis")
                
                # Generate cashflow for current bid
                if bid_amount > 0:
                    cashflows = analyzer.calculate_cashflows(bid_amount, winning_month)
                    
                    if cashflows:
                        # Convert to DataFrame
                        df_cashflow = pd.DataFrame([
                            {'Month': i+1, 'Amount': cf} for i, cf in enumerate(cashflows)
                        ])
                        
                        # Plot
                        fig = px.bar(
                            df_cashflow,
                            x='Month',
                            y='Amount',
                            title=f'Monthly Cashflows (Bid: ₹{bid_amount:,.0f}, Winning Month: {winning_month})',
                            color='Amount',
                            color_continuous_scale=['red', 'blue']
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Summary
                        total_outflow = sum(cf for cf in cashflows if cf < 0)
                        total_inflow = sum(cf for cf in cashflows if cf > 0)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Outflow", f"₹{abs(total_outflow):,.0f}")
                        with col2:
                            st.metric("Total Inflow", f"₹{total_inflow:,.0f}")
                        with col3:
                            st.metric("Net Cashflow", f"₹{total_inflow + total_outflow:,.0f}")
                else:
                    st.info("Enter a bid amount in the 'Current Analysis' tab to see cashflow details")
            
            with tab4:
                st.subheader("Installment History")
                
                if installment_history:
                    # Convert to DataFrame
                    df_history = pd.DataFrame(installment_history)
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total_paid = df_history['amount_paid'].sum()
                    total_bids = df_history['bid_amount'].sum()
                    total_commission = df_history['commission'].sum()
                    avg_bid = df_history[df_history['bid_amount'] > 0]['bid_amount'].mean()
                    
                    with col1:
                        st.metric("Total Paid", f"₹{total_paid:,.0f}")
                    with col2:
                        st.metric("Total Bids", f"₹{total_bids:,.0f}")
                    with col3:
                        st.metric("Total Commission", f"₹{total_commission:,.0f}")
                    with col4:
                        if not pd.isna(avg_bid):
                            st.metric("Average Bid", f"₹{avg_bid:,.0f}")
                        else:
                            st.metric("Average Bid", "N/A")
                    
                    # History table
                    st.subheader("Detailed History")
                    
                    # Format the DataFrame for display
                    display_df = df_history.copy()
                    display_df['amount_paid'] = display_df['amount_paid'].apply(lambda x: f"₹{x:,.0f}")
                    display_df['bid_amount'] = display_df['bid_amount'].apply(lambda x: f"₹{x:,.0f}" if x > 0 else "-")
                    display_df['commission'] = display_df['commission'].apply(lambda x: f"₹{x:,.0f}" if x > 0 else "-")
                    display_df['net_amount'] = display_df['net_amount'].apply(lambda x: f"₹{x:,.0f}" if x > 0 else "-")
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Download option
                    csv = df_history.to_csv(index=False)
                    st.download_button(
                        label="📊 Download History as CSV",
                        data=csv,
                        file_name=f"{selected_chit}_history.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No installment history found for this chit fund.")
                    st.write("Add installment data by editing the configuration or updating the Google Sheet directly.")
        
        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")
            st.write("Please check your chit fund configuration and try again.")


def main():
    """Main app controller"""
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏦 Chit Fund Analyzer")
        st.write("---")
        
        # Navigation based on authentication state
        if st.session_state.authenticated:
            st.success("✅ Connected to Google Sheets")
            if st.session_state.spreadsheet_name:
                st.write(f"📊 **{st.session_state.spreadsheet_name}**")
            
            st.write("**Navigation:**")
            
            # Navigation buttons
            if st.button("📊 Configure New Chit", use_container_width=True):
                st.session_state.current_page = 'Configuration'
                st.rerun()
            
            if st.button("📈 Analyze Existing Chit", use_container_width=True):
                st.session_state.current_page = 'Analysis'
                st.rerun()
            
            st.write("---")
            
            # Quick stats if available
            try:
                chit_names = sheets_service.get_chit_names()
                st.write(f"**Available Chits:** {len(chit_names)}")
                
                if chit_names:
                    st.write("**Chit List:**")
                    for chit in chit_names[:5]:  # Show first 5
                        st.write(f"• {chit}")
                    if len(chit_names) > 5:
                        st.write(f"• ... and {len(chit_names) - 5} more")
            except:
                pass
            
            st.write("---")
            
            if st.button("🔄 Switch Account", type="secondary", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.current_page = 'Authentication'
                st.rerun()
        
        else:
            st.warning("🔐 Not Connected")
            st.write("Please authenticate with Google OAuth to continue.")
        
        # App info
        st.write("---")
        st.write("**About:**")
        st.write("Analyze chit fund investments with IRR calculations and scenario analysis.")
        st.write("🔐 **Auth:** Google OAuth")
        st.write("💡 **Version:** 2.1")
    
    # Main content area
    if not st.session_state.authenticated:
        show_authentication_page()
    elif st.session_state.current_page == 'Configuration':
        show_configuration_page()
    elif st.session_state.current_page == 'Analysis':
        show_analysis_page()
    else:
        # Default to analysis if authenticated
        st.session_state.current_page = 'Analysis'
        show_analysis_page()


if __name__ == "__main__":
    main()