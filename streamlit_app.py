"""
Chit Fund Analyzer - Streamlit Web Application

A comprehensive web interface for analyzing chit fund investments with real-time
calculations, scenario analysis, and interactive visualizations.

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from decimal import Decimal
import numpy as np
from typing import List, Dict, Any

# Import our chit fund analyzer
from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer, ScenarioAnalyzer
from chit_fund_analyzer.utils import format_currency, format_percentage, ChitFundFormatter
from chit_fund_analyzer.exceptions import ChitFundAnalysisError


def set_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Chit Fund Analyzer",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def add_custom_css():
    """Add custom CSS for better styling."""
    st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #007bff;
            margin: 0.5rem 0;
        }
        .success-card {
            background: #d4edda;
            border-left: 4px solid #28a745;
        }
        .warning-card {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }
        .error-card {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }
        .stButton > button {
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)


def create_header():
    """Create the app header."""
    st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0; text-align: center;">
                💰 Chit Fund Analyzer
            </h1>
            <p style="color: #e9ecef; margin: 0; text-align: center;">
                Analyze chit fund investments with precision and confidence
            </p>
        </div>
    """, unsafe_allow_html=True)


def get_user_inputs():
    """Get user inputs from the sidebar."""
    st.sidebar.header("🔧 Configuration")
    
    with st.sidebar.expander("📊 Basic Parameters", expanded=True):
        total_installments = st.number_input(
            "Total Installments",
            min_value=1,
            max_value=100,
            value=14,
            help="Total number of installments in the chit fund"
        )
        
        current_installment = st.number_input(
            "Current Installment Number",
            min_value=1,
            max_value=total_installments,
            value=min(5, total_installments),
            help="The current installment number (1-based)"
        )
        
        full_chit_value = st.number_input(
            "Full Chit Value (₹)",
            min_value=1000,
            max_value=10000000,
            value=700000,
            step=1000,
            help="Total value of the chit fund"
        )
        
        chit_frequency = st.selectbox(
            "Payment Frequency",
            options=[1, 2, 4, 6, 12],
            index=1,  # Default to bi-annual
            format_func=lambda x: {
                1: "Annual", 2: "Bi-annual", 4: "Quarterly", 
                6: "Bi-monthly", 12: "Monthly"
            }[x],
            help="Number of installments per year"
        )
        
        bid_amount = st.number_input(
            "Your Bid Amount (₹)",
            min_value=1000,
            max_value=full_chit_value - 1000,
            value=min(100000, full_chit_value // 2),
            step=1000,
            help="Amount you're bidding to win the chit"
        )
    
    with st.sidebar.expander("💸 Previous Installments"):
        st.info(f"Enter {current_installment - 1} previous installment amounts")
        
        previous_installments = []
        default_installment = full_chit_value / total_installments
        
        for i in range(current_installment - 1):
            amount = st.number_input(
                f"Installment {i + 1} (₹)",
                min_value=0,
                max_value=full_chit_value,
                value=int(default_installment),
                step=1000,
                key=f"prev_installment_{i}"
            )
            previous_installments.append(amount)
    
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
                max_value=full_chit_value,
                value=int(full_chit_value / total_installments),
                step=1000,
                help="Custom installment amount for the winner"
            )
    
    return {
        'total_installments': total_installments,
        'current_installment_number': current_installment,
        'full_chit_value': Decimal(str(full_chit_value)),
        'chit_frequency_per_year': chit_frequency,
        'previous_installments': [Decimal(str(amount)) for amount in previous_installments],
        'bid_amount': Decimal(str(bid_amount)),
        'winner_installment_amount': Decimal(str(custom_installment)) if custom_installment else None
    }


def create_config_and_analyze(inputs: Dict) -> tuple:
    """Create configuration and perform analysis."""
    try:
        config = ChitFundConfig(**inputs)
        analyzer = ChitFundAnalyzer(config)
        result = analyzer.analyze()
        return config, result, None
    except Exception as e:
        return None, None, str(e)


def display_basic_results(config: ChitFundConfig, result):
    """Display basic analysis results."""
    st.header("📈 Analysis Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card success-card">
                <h4>Prize Amount</h4>
                <h2>{format_currency(result.prize_amount)}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h4>Annual IRR</h4>
                <h2 style="color: {'green' if result.annual_irr > 0.1 else 'orange' if result.annual_irr > 0.05 else 'red'}">
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
        net_return = result.prize_amount - sum(result.cashflows[:-len(result.cashflows) + config.current_installment_number])
        st.markdown(f"""
            <div class="metric-card">
                <h4>Net Benefit</h4>
                <h2 style="color: {'green' if net_return > 0 else 'red'}">
                    {format_currency(abs(net_return))}
                </h2>
            </div>
        """, unsafe_allow_html=True)


def create_cashflow_chart(result):
    """Create cashflow visualization."""
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


def get_scenario_inputs():
    """Get scenario analysis inputs."""
    st.header("🔍 Scenario Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_bid = st.number_input(
            "Minimum Bid Amount (₹)",
            min_value=1000,
            value=80000,
            step=1000,
            key="min_bid"
        )
    
    with col2:
        max_bid = st.number_input(
            "Maximum Bid Amount (₹)",
            min_value=min_bid + 1000,
            value=150000,
            step=1000,
            key="max_bid"
        )
    
    with col3:
        num_scenarios = st.number_input(
            "Number of Scenarios",
            min_value=3,
            max_value=50,
            value=10,
            help="Number of bid amounts to analyze between min and max"
        )
    
    return min_bid, max_bid, num_scenarios


def perform_scenario_analysis(config: ChitFundConfig, min_bid: int, max_bid: int, num_scenarios: int):
    """Perform scenario analysis."""
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


def create_scenario_visualizations(scenarios: List):
    """Create scenario analysis visualizations."""
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
    
    # Update x-axis and y-axis labels
    fig.update_xaxes(title_text="Bid Amount (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Annual IRR (%)", row=1, col=1)
    
    fig.update_xaxes(title_text="Bid Amount (₹)", row=1, col=2)
    fig.update_yaxes(title_text="Prize Amount (₹)", row=1, col=2)
    
    fig.update_xaxes(title_text="Annual IRR (%)", row=2, col=1)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    
    fig.update_xaxes(title_text="Bid Amount (₹)", row=2, col=2)
    fig.update_yaxes(title_text="Prize Amount (₹)", row=2, col=2)
    
    return fig


def create_scenario_table(scenarios: List):
    """Create a detailed scenario analysis table."""
    data = []
    for i, scenario in enumerate(scenarios, 1):
        data.append({
            'Scenario': f'#{i}',
            'Bid Amount': format_currency(scenario.bid_amount),
            'Prize Amount': format_currency(scenario.prize_amount),
            'Annual IRR': format_percentage(scenario.annual_irr),
            'IRR Score': '🟢 Excellent' if scenario.annual_irr > 0.15 
                        else '🟡 Good' if scenario.annual_irr > 0.10 
                        else '🟠 Average' if scenario.annual_irr > 0.05 
                        else '🔴 Poor'
        })
    
    return pd.DataFrame(data)


def display_summary_insights(config: ChitFundConfig, result, scenarios: List = None):
    """Display insights and recommendations."""
    st.header("💡 Insights & Recommendations")
    
    insights = []
    
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


def export_analysis(config: ChitFundConfig, result, scenarios: List = None):
    """Provide export functionality."""
    st.header("📄 Export Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Basic Analysis"):
            analysis_data = {
                'Configuration': pd.DataFrame([{
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
            }
            
            st.download_button(
                label="Download CSV",
                data=analysis_data['Configuration'].to_csv(index=False),
                file_name="chit_fund_analysis.csv",
                mime="text/csv"
            )
    
    with col2:
        if scenarios and st.button("📈 Download Scenario Analysis"):
            scenario_df = create_scenario_table(scenarios)
            st.download_button(
                label="Download Scenarios CSV",
                data=scenario_df.to_csv(index=False),
                file_name="chit_fund_scenarios.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Generate Report"):
            report = f"""
# Chit Fund Analysis Report

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

## Generated by Chit Fund Analyzer
"""
            
            st.download_button(
                label="Download Report",
                data=report,
                file_name="chit_fund_report.md",
                mime="text/markdown"
            )


def main():
    """Main application function."""
    set_page_config()
    add_custom_css()
    create_header()
    
    # Get user inputs
    inputs = get_user_inputs()
    
    # Analyze button
    if st.sidebar.button("🚀 Analyze Chit Fund", type="primary"):
        with st.spinner("Analyzing your chit fund..."):
            config, result, error = create_config_and_analyze(inputs)
            
            if error:
                st.error(f"⚠️ Configuration Error: {error}")
                st.info("Please check your inputs and try again.")
                return
            
            # Store results in session state
            st.session_state['config'] = config
            st.session_state['result'] = result
    
    # Display results if available
    if 'config' in st.session_state and 'result' in st.session_state:
        config = st.session_state['config']
        result = st.session_state['result']
        
        # Basic Results
        display_basic_results(config, result)
        
        # Cashflow Chart
        st.subheader("💰 Cashflow Visualization")
        cashflow_fig = create_cashflow_chart(result)
        st.plotly_chart(cashflow_fig, width='stretch')
        
        # Scenario Analysis Section
        st.markdown("---")
        min_bid, max_bid, num_scenarios = get_scenario_inputs()
        
        if st.button("🔍 Run Scenario Analysis", type="secondary"):
            with st.spinner("Running scenario analysis..."):
                scenarios, scenario_error = perform_scenario_analysis(
                    config, min_bid, max_bid, num_scenarios
                )
                
                if scenario_error:
                    st.error(f"⚠️ Scenario Analysis Error: {scenario_error}")
                else:
                    st.session_state['scenarios'] = scenarios
        
        # Display scenario results if available
        if 'scenarios' in st.session_state:
            scenarios = st.session_state['scenarios']
            
            # Scenario Visualizations
            st.subheader("📊 Scenario Analysis Results")
            scenario_fig = create_scenario_visualizations(scenarios)
            st.plotly_chart(scenario_fig, width='stretch')
            
            # Scenario Table
            st.subheader("📋 Detailed Scenario Breakdown")
            scenario_table = create_scenario_table(scenarios)
            st.dataframe(scenario_table, width='stretch', hide_index=True)
            
            # Insights
            st.markdown("---")
            display_summary_insights(config, result, scenarios)
            
            # Export
            st.markdown("---")
            export_analysis(config, result, scenarios)
        else:
            # Show insights without scenario data
            st.markdown("---")
            display_summary_insights(config, result)
            
            # Export basic analysis
            st.markdown("---")
            export_analysis(config, result)
    
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to the Chit Fund Analyzer! 👋
        
        This application helps you analyze chit fund investments with precision and confidence.
        
        ### Getting Started:
        1. **Configure your chit fund parameters** in the sidebar
        2. **Enter your previous installments** (if any)
        3. **Click "Analyze Chit Fund"** to see detailed results
        4. **Run scenario analysis** to compare different bid amounts
        
        ### Features:
        - 📊 **Real-time IRR calculations**
        - 📈 **Interactive visualizations**
        - 🔍 **Comprehensive scenario analysis**
        - 🎯 **Optimal bid recommendations**
        - 💡 **Intelligent insights**
        - 📄 **Export capabilities**
        
        Start by entering your chit fund details in the sidebar!
        """)
        
        # Sample configuration for demo
        st.markdown("---")
        st.subheader("💡 Sample Configuration")
        st.info("""
        **Demo Setup**: Try these sample values to see the analyzer in action:
        - Total Installments: 14
        - Current Installment: 5
        - Full Chit Value: ₹7,00,000
        - Bid Amount: ₹1,00,000
        - Previous Installments: ₹42,000, ₹40,000, ₹40,000, ₹43,000
        """)


if __name__ == "__main__":
    main()