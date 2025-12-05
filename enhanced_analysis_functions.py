# Enhanced analysis functions matching streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from decimal import Decimal
from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer, ScenarioAnalyzer


def get_enhanced_analysis_inputs(config):
    """Get enhanced analysis inputs similar to streamlit_app.py"""
    st.sidebar.header("🔧 Enhanced Analysis Configuration")
    
    with st.sidebar.expander("📊 Analysis Parameters", expanded=True):
        # Get current installment data
        from google_sheets_service_auto import GoogleSheetsService
        google_sheets_service = GoogleSheetsService()
        installments = google_sheets_service.get_installments(config.get('chit_name', ''))
        
        current_installment = st.number_input(
            "Current Installment Number",
            min_value=1,
            max_value=config.get('total_installments', 12),
            value=len(installments) + 1 if installments else 1,
            help="The current installment number (1-based)"
        )
        
        bid_amount = st.number_input(
            "Your Bid Amount (₹)",
            min_value=1000,
            max_value=config.get('full_chit_value', 1000000) - 1000,
            value=min(100000, config.get('full_chit_value', 1000000) // 2),
            step=1000,
            help="Amount you're bidding to win the chit"
        )
    
    with st.sidebar.expander("⚙️ Advanced Options"):
        use_custom_installment = st.checkbox(
            "Custom Winner Installment Amount",
            help="Override the default winner installment calculation"
        )
        
        custom_installment = None
        if use_custom_installment:
            custom_installment = st.number_input(
                "Winner Installment Amount (₹)",
                min_value=1000,
                max_value=config.get('full_chit_value', 1000000),
                value=int(config.get('full_chit_value', 1000000) / config.get('total_installments', 12)),
                step=1000,
                help="Custom installment amount for the winner"
            )
    
    return {
        'current_installment_number': current_installment,
        'bid_amount': bid_amount,
        'winner_installment_amount': Decimal(str(custom_installment)) if custom_installment else None
    }


def create_enhanced_config_and_analyze(config, analysis_inputs):
    """Create enhanced configuration and perform analysis"""
    try:
        # Get installments data
        from google_sheets_service_auto import GoogleSheetsService
        google_sheets_service = GoogleSheetsService()
        installments = google_sheets_service.get_installments(config.get('chit_name', ''))
        
        # Prepare previous installments
        previous_installments = []
        if installments:
            for inst in installments:
                try:
                    payment = inst.get('Net Payment', 0)
                    if payment:
                        previous_installments.append(Decimal(str(payment)))
                except (ValueError, TypeError):
                    continue
        
        # Create enhanced config
        enhanced_config = ChitFundConfig(
            total_installments=config.get('total_installments', 12),
            current_installment_number=analysis_inputs['current_installment_number'],
            full_chit_value=Decimal(str(config.get('full_chit_value', 0))),
            chit_frequency_per_year=config.get('chit_frequency_per_year', 12),
            previous_installments=previous_installments,
            bid_amount=Decimal(str(analysis_inputs['bid_amount'])),
            winner_installment_amount=analysis_inputs['winner_installment_amount']
        )
        
        # Analyze
        analyzer = ChitFundAnalyzer(enhanced_config)
        result = analyzer.analyze()
        
        return enhanced_config, result, None
    except Exception as e:
        return None, None, str(e)


def display_enhanced_basic_results(config, result):
    """Display enhanced basic analysis results similar to streamlit_app.py"""
    st.header("📈 Analysis Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Formatting functions
    def format_currency(amount):
        return f"₹{float(amount):,.2f}"
    
    def format_percentage(rate):
        return f"{float(rate)*100:.2f}%"
    
    with col1:
        st.markdown(f"""
            <div class="metric-card success-card">
                <h4>Prize Amount</h4>
                <h2>{format_currency(result.prize_amount)}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        irr_color = "green" if result.annual_irr > 0.1 else "orange" if result.annual_irr > 0.05 else "red"
        st.markdown(f"""
            <div class="metric-card">
                <h4>Annual IRR</h4>
                <h2 style="color: {irr_color}">
                    {format_percentage(result.annual_irr)}
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h4>Winner Installment</h4>
                <h2>{format_currency(config.get_winner_installment_amount())}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_payments = sum(float(cf) for cf in result.cashflows if float(cf) < 0)
        net_benefit = float(result.prize_amount) + total_payments
        benefit_color = "green" if net_benefit > 0 else "red"
        st.markdown(f"""
            <div class="metric-card">
                <h4>Net Benefit</h4>
                <h2 style="color: {benefit_color}">
                    {format_currency(abs(net_benefit))}
                </h2>
            </div>
        """, unsafe_allow_html=True)


def create_enhanced_cashflow_chart(result):
    """Create enhanced cashflow visualization"""
    def format_currency(amount):
        return f"₹{float(amount):,.2f}"
    
    cashflows = [float(cf) for cf in result.cashflows]
    periods = list(range(1, len(cashflows) + 1))
    
    # Identify inflow and outflow
    colors = ['red' if cf < 0 else 'green' for cf in cashflows]
    
    fig = go.Figure(data=[
        go.Bar(
            x=periods,
            y=cashflows,
            marker_color=colors,
            text=[format_currency(abs(cf)) for cf in cashflows],
            textposition='outside',
            hovertemplate='<b>Period %{x}</b><br>' +
                         'Cashflow: %{text}<br>' +
                         'Type: %{customdata}<extra></extra>',
            customdata=['OUTFLOW' if cf < 0 else 'INFLOW' for cf in cashflows]
        )
    ])
    
    fig.update_layout(
        title="Cashflow Breakdown by Period",
        xaxis_title="Period",
        yaxis_title="Amount (₹)",
        showlegend=False,
        height=500
    )
    
    return fig


def get_enhanced_scenario_inputs(config):
    """Get enhanced scenario analysis inputs"""
    st.header("🔍 Comprehensive Scenario Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_bid = st.number_input(
            "Minimum Bid Amount (₹)",
            min_value=1000,
            value=max(1000, int(float(config.bid_amount) * 0.8)),
            step=1000,
            key="enh_min_bid",
            help="Lowest bid amount to analyze"
        )
    
    with col2:
        max_bid = st.number_input(
            "Maximum Bid Amount (₹)",
            min_value=min_bid + 1000,
            value=min(int(float(config.bid_amount) * 1.5), int(float(config.full_chit_value) * 0.8)),
            step=1000,
            key="enh_max_bid",
            help="Highest bid amount to analyze"
        )
    
    with col3:
        num_scenarios = st.number_input(
            "Number of Scenarios",
            min_value=3,
            max_value=20,
            value=10,
            help="Number of bid amounts to analyze between min and max"
        )
    
    return {
        'min_bid': min_bid,
        'max_bid': max_bid,
        'num_scenarios': num_scenarios
    }


def perform_enhanced_scenario_analysis(config, min_bid, max_bid, num_scenarios):
    """Perform enhanced scenario analysis"""
    try:
        scenario_analyzer = ScenarioAnalyzer(config)
        
        # Generate bid amounts
        bid_step = (max_bid - min_bid) / (num_scenarios - 1)
        bid_amounts = [Decimal(str(min_bid + i * bid_step)) for i in range(num_scenarios)]
        
        # Analyze scenarios
        scenarios = scenario_analyzer.analyze_bid_scenarios(bid_amounts)
        
        return scenarios, None
    except Exception as e:
        return None, str(e)


def create_enhanced_scenario_visualizations(scenarios):
    """Create enhanced scenario analysis visualizations"""
    # Prepare data
    bid_amounts = [float(s.bid_amount) for s in scenarios]
    prize_amounts = [float(s.prize_amount) for s in scenarios]
    annual_irrs = [s.annual_irr * 100 for s in scenarios]  # Convert to percentage
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('IRR vs Bid Amount', 'Prize Amount vs Bid Amount', 
                       'IRR Distribution', 'Bid vs Prize Relationship'),
        specs=[[{'secondary_y': False}, {'secondary_y': False}],
               [{'secondary_y': False}, {'secondary_y': False}]]
    )
    
    # IRR vs Bid Amount (Line Chart)
    fig.add_trace(
        go.Scatter(x=bid_amounts, y=annual_irrs, 
                  mode='lines+markers',
                  name='Annual IRR (%)',
                  line=dict(color='blue', width=3),
                  marker=dict(size=8)),
        row=1, col=1
    )
    
    # Prize Amount vs Bid Amount (Bar Chart)
    fig.add_trace(
        go.Bar(x=bid_amounts, y=prize_amounts,
               name='Prize Amount',
               marker_color='lightgreen'),
        row=1, col=2
    )
    
    # IRR Distribution (Histogram)
    fig.add_trace(
        go.Histogram(x=annual_irrs,
                    nbinsx=10,
                    name='IRR Distribution',
                    marker_color='orange'),
        row=2, col=1
    )
    
    # Bid vs Prize Relationship (Scatter)
    fig.add_trace(
        go.Scatter(x=bid_amounts, y=prize_amounts,
                  mode='markers+text',
                  text=[f'{irr:.1f}%' for irr in annual_irrs],
                  textposition='top center',
                  name='Bid vs Prize (with IRR)',
                  marker=dict(size=10, color=annual_irrs, 
                            colorscale='viridis', showscale=True)),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Comprehensive Scenario Analysis"
    )
    
    # Update axis labels
    fig.update_xaxes(title_text="Bid Amount (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Annual IRR (%)", row=1, col=1)
    fig.update_xaxes(title_text="Bid Amount (₹)", row=1, col=2)
    fig.update_yaxes(title_text="Prize Amount (₹)", row=1, col=2)
    fig.update_xaxes(title_text="Annual IRR (%)", row=2, col=1)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    fig.update_xaxes(title_text="Bid Amount (₹)", row=2, col=2)
    fig.update_yaxes(title_text="Prize Amount (₹)", row=2, col=2)
    
    return fig


def create_enhanced_scenario_table(scenarios):
    """Create enhanced detailed scenario analysis table"""
    def format_currency(amount):
        return f"₹{float(amount):,.2f}"
    def format_percentage(rate):
        return f"{float(rate)*100:.2f}%"
    
    data = []
    for i, scenario in enumerate(scenarios, 1):
        data.append({
            'Scenario': f'#{i}',
            'Bid Amount': format_currency(scenario.bid_amount),
            'Prize Amount': format_currency(scenario.prize_amount),
            'Annual IRR': format_percentage(scenario.annual_irr),
            'IRR Score': '🟢 Excellent' if scenario.annual_irr > 0.15 \
                        else '🟡 Good' if scenario.annual_irr > 0.10 \
                        else '🟠 Average' if scenario.annual_irr > 0.05 \
                        else '🔴 Poor'
        })
    
    return pd.DataFrame(data)


def display_enhanced_summary_insights(config, result, scenarios=None):
    """Display enhanced insights and recommendations"""
    def format_currency(amount):
        return f"₹{float(amount):,.2f}"
    def format_percentage(rate):
        return f"{float(rate)*100:.2f}%"
    
    st.header("💡 Enhanced Insights & Recommendations")
    
    insights = []
    
    # Check if result is valid
    if not result:
        st.error("⚠️ No analysis results available. Please run the analysis first.")
        return
    
    # IRR Analysis
    if result.annual_irr > 0.15:
        insights.append("🟢 **Excellent Returns**: Your investment offers outstanding returns (>15% annually)")
    elif result.annual_irr > 0.10:
        insights.append("🟡 **Good Returns**: Your investment offers good returns (10-15% annually)")
    elif result.annual_irr > 0.05:
        insights.append("🟠 **Average Returns**: Your investment offers average returns (5-10% annually)")
    else:
        insights.append("🔴 **Poor Returns**: Consider higher bid amounts or different timing")
    
    # Bid Analysis
    bid_ratio = float(config.bid_amount) / float(config.full_chit_value)
    if bid_ratio < 0.1:
        insights.append("🔷 **Conservative Bidding**: Your bid is conservative, consider increasing for better returns")
    elif bid_ratio > 0.3:
        insights.append("🔶 **Aggressive Bidding**: High bid amount reduces immediate prize but may improve long-term returns")
    
    # Timing Analysis
    timing_ratio = config.current_installment_number / config.total_installments
    if timing_ratio < 0.3:
        insights.append("⏰ **Early Winner**: Winning early provides good liquidity but lower returns")
    elif timing_ratio > 0.7:
        insights.append("⌛ **Late Winner**: Winning late typically offers higher returns due to time value")
    
    # Frequency Analysis
    if config.chit_frequency_per_year >= 12:
        insights.append("📅 **High Frequency**: Monthly payments provide good cash flow management")
    elif config.chit_frequency_per_year <= 2:
        insights.append("📆 **Low Frequency**: Longer payment cycles may offer compounding benefits")
    
    # Display insights
    for insight in insights:
        st.markdown(insight)
    
    # Scenario-based insights
    if scenarios and len(scenarios) > 2:
        best_scenario = max(scenarios, key=lambda s: s.annual_irr)
        worst_scenario = min(scenarios, key=lambda s: s.annual_irr)
        
        st.subheader("🔍 Scenario Insights")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                **🏆 Best Case Scenario:**
                - Bid: {format_currency(best_scenario.bid_amount)}
                - IRR: {format_percentage(best_scenario.annual_irr)}
                - Prize: {format_currency(best_scenario.prize_amount)}
            """)
        
        with col2:
            st.markdown(f"""
                **📉 Worst Case Scenario:**
                - Bid: {format_currency(worst_scenario.bid_amount)}
                - IRR: {format_percentage(worst_scenario.annual_irr)}
                - Prize: {format_currency(worst_scenario.prize_amount)}
            """)
        
        irr_range = best_scenario.annual_irr - worst_scenario.annual_irr
        st.info(f"💡 **Range Impact**: Bid amount variations can change your returns by {format_percentage(irr_range)}")


def export_enhanced_analysis(config, result, scenarios=None):
    """Provide enhanced export functionality"""
    def format_currency(amount):
        return f"₹{float(amount):,.2f}"
    def format_percentage(rate):
        return f"{float(rate)*100:.2f}%"
    
    st.header("📄 Export Enhanced Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Basic Analysis"):
            analysis_data = pd.DataFrame([{
                'Parameter': 'Total Installments',
                'Value': config.total_installments
            }, {
                'Parameter': 'Current Installment',
                'Value': config.current_installment_number
            }, {
                'Parameter': 'Full Chit Value',
                'Value': format_currency(config.full_chit_value)
            }, {
                'Parameter': 'Bid Amount',
                'Value': format_currency(config.bid_amount)
            }, {
                'Parameter': 'Annual IRR',
                'Value': format_percentage(result.annual_irr)
            }, {
                'Parameter': 'Prize Amount',
                'Value': format_currency(result.prize_amount)
            }])
            
            st.download_button(
                label="Download CSV",
                data=analysis_data.to_csv(index=False),
                file_name="enhanced_chit_fund_analysis.csv",
                mime="text/csv"
            )
    
    with col2:
        if scenarios and st.button("📈 Download Scenario Analysis"):
            scenario_df = create_enhanced_scenario_table(scenarios)
            st.download_button(
                label="Download Scenarios CSV",
                data=scenario_df.to_csv(index=False),
                file_name="enhanced_chit_fund_scenarios.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Generate Comprehensive Report"):
            report = f"""
# Enhanced Chit Fund Analysis Report

## Configuration
- **Total Installments:** {config.total_installments}
- **Current Installment:** {config.current_installment_number}
- **Full Chit Value:** {format_currency(config.full_chit_value)}
- **Bid Amount:** {format_currency(config.bid_amount)}
- **Payment Frequency:** {config.chit_frequency_per_year} times per year

## Results
- **Prize Amount:** {format_currency(result.prize_amount)}
- **Annual IRR:** {format_percentage(result.annual_irr)}
- **Winner Installment:** {format_currency(config.get_winner_installment_amount())}

## Generated by Enhanced Chit Fund Analyzer
"""
            
            st.download_button(
                label="Download Report",
                data=report,
                file_name="enhanced_chit_fund_report.md",
                mime="text/markdown"
            )


def export_current_configuration(config, chit_name):
    """Export current configuration data"""
    config_data = pd.DataFrame([{
        'Chit Name': chit_name,
        'Total Installments': config.get('total_installments', 'N/A'),
        'Full Chit Value': f"₹{config.get('full_chit_value', 0):,}",
        'Payment Frequency': config.get('payment_frequency', 'N/A'),
        'Chit Method': config.get('chit_method', 'N/A'),
        'Start Date': config.get('start_date', 'N/A'),
        'Created': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }])
    
    st.download_button(
        label="Download Configuration",
        data=config_data.to_csv(index=False),
        file_name=f"chit_config_{chit_name.replace(' ', '_')}.csv",
        mime="text/csv"
    )