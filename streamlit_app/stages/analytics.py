"""
Stage 3: Analytics

Scenario analysis with visualizations and exports.
"""

from typing import List, Dict, Any
from decimal import Decimal
from datetime import date
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from chit_fund_analyzer.models import ChitFundConfig, BidScenario
from chit_fund_analyzer.analyzer import ChitFundAnalyzer
from chit_fund_analyzer.scenario import ScenarioAnalyzer
from chit_fund_analyzer.exceptions import ChitFundAnalysisError

from streamlit_app.db import ChitFundDB
from streamlit_app.utils import (
    show_success, show_error, show_warning, show_info,
    format_currency, format_percentage, create_downloadable_df
)


def render(db: ChitFundDB) -> None:
    """
    Render the analytics stage.
    
    Args:
        db: Database instance
    """
    # Check if a chit is selected
    if 'selected_chit' not in st.session_state or st.session_state['selected_chit'] is None:
        show_warning("No chit fund selected. Please go back to the dashboard.")
        if st.button("⬅️ Back to Dashboard"):
            st.session_state['current_stage'] = 1
            st.rerun()
        return
    
    chit = st.session_state['selected_chit']
    
    st.title(f"📊 Scenario Analysis: {chit['name']}")
    
    # Get installments to determine current state
    installments = db.get_installments(chit['chit_id'])
    
    # Find the first installment with data (or use 1 as default)
    current_installment = 1
    previous_amounts = []
    
    for inst in installments:
        if inst.get('amount_paid') and inst['amount_paid'] > 0:
            previous_amounts.append(Decimal(str(inst['amount_paid'])))
            current_installment = inst['installment_number'] + 1
    
    # If we're past the last installment, analyze the last one
    if current_installment > chit['total_installments']:
        current_installment = chit['total_installments']
    
    # Scenario configuration
    st.subheader("🎯 Scenario Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Current Installment", current_installment)
        st.metric("Total Installments", chit['total_installments'])
    
    with col2:
        st.metric("Full Chit Value", format_currency(chit['full_chit_value']))
        st.metric("Frequency/Year", chit['chit_frequency_per_year'])
    
    st.markdown("---")
    
    # Bid range configuration
    st.subheader("💡 Configure Bid Scenarios")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_bid = st.number_input(
            "Minimum Bid Amount (₹)",
            min_value=1000.0,
            max_value=float(chit['full_chit_value']) * 0.8,
            value=10000.0,
            step=1000.0,
            help="Lowest bid amount to analyze"
        )
    
    with col2:
        max_bid = st.number_input(
            "Maximum Bid Amount (₹)",
            min_value=min_bid + 1000,
            max_value=float(chit['full_chit_value']) * 0.95,
            value=min(50000.0, float(chit['full_chit_value']) * 0.5),
            step=1000.0,
            help="Highest bid amount to analyze"
        )
    
    with col3:
        num_scenarios = st.number_input(
            "Number of Scenarios",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            help="Number of bid scenarios to analyze"
        )
    
    # Analyze button
    if st.button("🚀 Run Scenario Analysis", type="primary", use_container_width=True):
        run_scenario_analysis(
            chit=chit,
            current_installment=current_installment,
            previous_amounts=previous_amounts,
            min_bid=min_bid,
            max_bid=max_bid,
            num_scenarios=int(num_scenarios)
        )
    
    # Display results if available
    if 'scenario_results' in st.session_state and st.session_state['scenario_results']:
        display_scenario_results(st.session_state['scenario_results'])
    
    # Navigation
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Installments", use_container_width=True):
            st.session_state['current_stage'] = 2
            st.rerun()
    
    with col2:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.session_state['current_stage'] = 1
            st.rerun()


def run_scenario_analysis(
    chit: Dict[str, Any],
    current_installment: int,
    previous_amounts: List[Decimal],
    min_bid: float,
    max_bid: float,
    num_scenarios: int
) -> None:
    """Run the scenario analysis."""
    
    try:
        # Generate bid amounts
        bid_amounts = [
            Decimal(str(bid))
            for bid in np.linspace(min_bid, max_bid, num_scenarios)
        ]
        
        # Create base config
        base_config = ChitFundConfig(
            total_installments=chit['total_installments'],
            current_installment_number=current_installment,
            full_chit_value=Decimal(str(chit['full_chit_value'])),
            chit_frequency_per_year=chit['chit_frequency_per_year'],
            previous_installments=previous_amounts if previous_amounts else [],
            bid_amount=Decimal(str(min_bid))  # Placeholder
        )
        
        # Run scenario analysis
        scenario_analyzer = ScenarioAnalyzer(base_config)
        scenarios = scenario_analyzer.analyze_bid_scenarios(bid_amounts)
        
        # Store results
        st.session_state['scenario_results'] = {
            'scenarios': scenarios,
            'config': base_config
        }
        
        show_success(f"✅ Analyzed {len(scenarios)} scenarios successfully!")
        
    except ChitFundAnalysisError as e:
        show_error(f"Analysis error: {str(e)}")
    except Exception as e:
        show_error(f"Unexpected error: {str(e)}")


def display_scenario_results(results: Dict[str, Any]) -> None:
    """Display the scenario analysis results."""
    
    scenarios: List[BidScenario] = results['scenarios']
    
    st.markdown("---")
    st.subheader("📈 Analysis Results")
    
    # Create DataFrame
    df_data = []
    for scenario in scenarios:
        df_data.append({
            'Bid Amount': float(scenario.bid_amount),
            'Prize Amount': float(scenario.prize_amount),
            'Annual IRR': scenario.annual_irr,
            'Annual IRR (%)': format_percentage(scenario.annual_irr)
        })
    
    df = pd.DataFrame(df_data)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_irr_scenario = max(scenarios, key=lambda s: s.annual_irr)
        st.metric(
            "🏆 Best IRR",
            format_percentage(best_irr_scenario.annual_irr),
            delta=f"Bid: {format_currency(best_irr_scenario.bid_amount)}"
        )
    
    with col2:
        avg_irr = sum(s.annual_irr for s in scenarios) / len(scenarios)
        st.metric(
            "📊 Average IRR",
            format_percentage(avg_irr)
        )
    
    with col3:
        highest_prize = max(scenarios, key=lambda s: s.prize_amount)
        st.metric(
            "💰 Max Prize Amount",
            format_currency(highest_prize.prize_amount),
            delta=f"Bid: {format_currency(highest_prize.bid_amount)}"
        )
    
    # Visualization
    st.markdown("### 📉 Bid Amount vs Annual IRR")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Bid Amount'],
        y=df['Annual IRR'] * 100,  # Convert to percentage
        mode='lines+markers',
        name='Annual IRR',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#3b82f6'),
        hovertemplate=(
            '<b>Bid Amount:</b> ₹%{x:,.2f}<br>'
            '<b>Annual IRR:</b> %{y:.2f}%<br>'
            '<extra></extra>'
        )
    ))
    
    fig.update_layout(
        xaxis_title='Bid Amount (₹)',
        yaxis_title='Annual IRR (%)',
        hovermode='closest',
        height=500,
        template='plotly_white',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(tickformat=',.0f', gridcolor='#e5e7eb')
    fig.update_yaxes(tickformat='.2f', gridcolor='#e5e7eb')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.markdown("### 📋 Detailed Scenario Breakdown")
    
    # Format the DataFrame for display
    display_df = df.copy()
    display_df['Bid Amount'] = display_df['Bid Amount'].apply(lambda x: format_currency(x))
    display_df['Prize Amount'] = display_df['Prize Amount'].apply(lambda x: format_currency(x))
    
    st.dataframe(
        display_df[['Bid Amount', 'Prize Amount', 'Annual IRR (%)']],
        use_container_width=True,
        hide_index=True
    )
    
    # Cashflow breakdown for best scenario
    st.markdown("### 💵 Cashflow Analysis (Best IRR Scenario)")
    
    best_scenario_config = ChitFundConfig(
        total_installments=results['config'].total_installments,
        current_installment_number=results['config'].current_installment_number,
        full_chit_value=results['config'].full_chit_value,
        chit_frequency_per_year=results['config'].chit_frequency_per_year,
        previous_installments=results['config'].previous_installments,
        bid_amount=best_irr_scenario.bid_amount
    )
    
    analyzer = ChitFundAnalyzer(best_scenario_config)
    result = analyzer.analyze()
    
    # Create cashflow DataFrame
    cashflow_data = []
    for i, cf in enumerate(result.cashflows):
        period_type = "Past" if i < len(results['config'].previous_installments) else \
                     "Prize" if i == len(results['config'].previous_installments) else \
                     "Future"
        
        cashflow_data.append({
            'Period': i + 1,
            'Type': period_type,
            'Cashflow': float(cf),
            'Cashflow (Formatted)': format_currency(abs(cf)) if cf < 0 else f"+{format_currency(cf)}"
        })
    
    cashflow_df = pd.DataFrame(cashflow_data)
    
    st.dataframe(
        cashflow_df[['Period', 'Type', 'Cashflow (Formatted)']],
        use_container_width=True,
        hide_index=True
    )
    
    # Export button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        # Prepare export data
        export_df = df.copy()
        
        excel_data = create_downloadable_df(export_df, "scenario_analysis.xlsx")
        
        st.download_button(
            label="📥 Download Report (Excel)",
            data=excel_data,
            file_name=f"chit_scenario_analysis_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
