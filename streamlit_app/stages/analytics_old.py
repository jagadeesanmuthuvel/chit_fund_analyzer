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
import plotly.graph_objects as go

from chit_fund_analyzer.models import ChitFundConfig, BidScenario
from chit_fund_analyzer.analyzer import ChitFundAnalyzer
from chit_fund_analyzer.scenario import ScenarioAnalyzer
from chit_fund_analyzer.comparative import ComparativeAnalyzer
from chit_fund_analyzer.exceptions import ChitFundAnalysisError

from streamlit_app.db import ChitFundDB
from streamlit_app.utils import (
    show_success, show_error, show_warning,
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
    
    st.title(f"📊 Analytics: {chit['name']}")
    
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
    
    # Create tabs for different analysis types
    tab1, tab2 = st.tabs(["🎯 Scenario Analysis", "⚖️ Comparative Analysis"])
    
    with tab1:
        render_scenario_analysis(db, chit, current_installment, previous_amounts)
    
    with tab2:
        render_comparative_analysis(db, chit, current_installment, previous_amounts)
    
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


def render_scenario_analysis(
    db: ChitFundDB,
    chit: Dict[str, Any],
    current_installment: int,
    previous_amounts: List[Decimal]
) -> None:
    """Render the scenario analysis tab."""
    
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


def render_comparative_analysis(
    db: ChitFundDB,
    chit: Dict[str, Any],
    current_installment: int,
    previous_amounts: List[Decimal]
) -> None:
    """Render comparative investment analysis tab."""
    
    st.subheader("⚖️ Break-Even & Investment Comparison")
    
    st.markdown("""
    Compare the returns from winning a chit fund at a specific bid amount against 
    alternative investment options like Fixed Deposits, Mutual Funds, or other returns.
    """)
    
    # Configuration section
    st.markdown("---")
    st.subheader("🎯 Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bid_amount = st.number_input(
            "Chit Bid Amount (₹)",
            min_value=1000.0,
            max_value=float(chit['full_chit_value']) * 0.9,
            value=50000.0,
            step=1000.0,
            help="The bid amount at which you win the chit"
        )
        
        st.metric("Current Installment", current_installment)
        st.metric("Total Installments", chit['total_installments'])
    
    with col2:
        st.markdown("##### Alternative Investment Returns")
        
        fd_rate = st.number_input(
            "Fixed Deposit Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.25,
            help="Annual interest rate for FD"
        )
        
        mf_rate = st.number_input(
            "Mutual Fund Expected Return (%)",
            min_value=0.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            help="Expected annual return from mutual funds"
        )
        
        custom_rate = st.number_input(
            "Custom Investment Return (%)",
            min_value=0.0,
            max_value=50.0,
            value=10.0,
            step=0.5,
            help="Any other investment option annual return"
        )
    
    # Analyze button
    if st.button("🔍 Compare Investments", type="primary", use_container_width=True):
        compare_investments(
            chit=chit,
            current_installment=current_installment,
            previous_amounts=previous_amounts,
            bid_amount=bid_amount,
            fd_rate=fd_rate / 100,  # Convert to decimal
            mf_rate=mf_rate / 100,
            custom_rate=custom_rate / 100
        )
    
    # Display comparison results
    if 'comparison_results' in st.session_state and st.session_state['comparison_results']:
        display_comparison_results(st.session_state['comparison_results'])


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


def compare_investments(
    chit: Dict[str, Any],
    current_installment: int,
    previous_amounts: List[Decimal],
    bid_amount: float,
    fd_rate: float,
    mf_rate: float,
    custom_rate: float
) -> None:
    """Compare chit fund returns with alternative investments."""
    
    try:
        # Analyze chit fund
        config = ChitFundConfig(
            total_installments=chit['total_installments'],
            current_installment_number=current_installment,
            full_chit_value=Decimal(str(chit['full_chit_value'])),
            chit_frequency_per_year=chit['chit_frequency_per_year'],
            previous_installments=previous_amounts,
            bid_amount=Decimal(str(bid_amount))
        )
        
        analyzer = ChitFundAnalyzer(config)
        chit_result = analyzer.analyze()
        
        # Calculate prize amount and remaining installments
        prize_amount = float(chit_result.prize_amount)
        remaining_installments = chit['total_installments'] - current_installment
        installment_amount = (float(chit['full_chit_value']) - bid_amount) / remaining_installments if remaining_installments > 0 else 0
        
        # Calculate months per installment
        months_per_installment = 12 / chit['chit_frequency_per_year']
        total_months = remaining_installments * months_per_installment
        
        # Calculate alternative investment returns
        monthly_rate_fd = (1 + fd_rate) ** (1/12) - 1
        monthly_rate_mf = (1 + mf_rate) ** (1/12) - 1
        monthly_rate_custom = (1 + custom_rate) ** (1/12) - 1
        
        fd_final = prize_amount * ((1 + monthly_rate_fd) ** total_months)
        mf_final = prize_amount * ((1 + monthly_rate_mf) ** total_months)
        custom_final = prize_amount * ((1 + monthly_rate_custom) ** total_months)
        
        # Calculate break-even bid amount
        break_even_bid = calculate_break_even_bid(
            chit, current_installment, previous_amounts, fd_rate
        )
        
        # Store results
        st.session_state['comparison_results'] = {
            'chit': {
                'bid_amount': bid_amount,
                'prize_amount': prize_amount,
                'annual_irr': chit_result.annual_irr,
                'installment_amount': installment_amount,
                'remaining_installments': remaining_installments
            },
            'fd': {
                'rate': fd_rate,
                'final_amount': fd_final,
                'gain': fd_final - prize_amount,
            },
            'mf': {
                'rate': mf_rate,
                'final_amount': mf_final,
                'gain': mf_final - prize_amount,
            },
            'custom': {
                'rate': custom_rate,
                'final_amount': custom_final,
                'gain': custom_final - prize_amount,
            },
            'break_even_bid': break_even_bid,
        }
        
        show_success("✅ Comparison analysis completed!")
        
    except Exception as e:
        show_error(f"Comparison error: {str(e)}")


def calculate_break_even_bid(
    chit: Dict[str, Any],
    current_installment: int,
    previous_amounts: List[Decimal],
    target_rate: float
) -> float:
    """Calculate the bid amount that would give IRR equal to target rate."""
    
    try:
        # Binary search for break-even bid
        low = 1000.0
        high = float(chit['full_chit_value']) * 0.9
        tolerance = 100.0
        
        while high - low > tolerance:
            mid = (low + high) / 2
            
            config = ChitFundConfig(
                total_installments=chit['total_installments'],
                current_installment_number=current_installment,
                full_chit_value=Decimal(str(chit['full_chit_value'])),
                chit_frequency_per_year=chit['chit_frequency_per_year'],
                previous_installments=previous_amounts,
                bid_amount=Decimal(str(mid))
            )
            
            analyzer = ChitFundAnalyzer(config)
            result = analyzer.analyze()
            
            if result.annual_irr > target_rate:
                low = mid
            else:
                high = mid
        
        return (low + high) / 2
    except Exception:
        return 0.0


def display_comparison_results(results: Dict[str, Any]) -> None:
    """Display investment comparison results."""
    
    st.markdown("---")
    st.subheader("📊 Comparison Results")
    
    chit = results['chit']
    fd = results['fd']
    mf = results['mf']
    custom = results['custom']
    
    # Key metrics comparison
    st.markdown("### 💰 Returns Comparison")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Chit Fund",
            format_percentage(chit['annual_irr']),
            delta=f"Prize: {format_currency(chit['prize_amount'])}"
        )
    
    with col2:
        st.metric(
            "🏦 Fixed Deposit",
            format_percentage(fd['rate']),
            delta=f"Gain: {format_currency(fd['gain'])}"
        )
    
    with col3:
        st.metric(
            "📈 Mutual Fund",
            format_percentage(mf['rate']),
            delta=f"Gain: {format_currency(mf['gain'])}"
        )
    
    with col4:
        st.metric(
            "💼 Custom Investment",
            format_percentage(custom['rate']),
            delta=f"Gain: {format_currency(custom['gain'])}"
        )
    
    # Winner analysis
    st.markdown("### 🏆 Best Investment Option")
    
    options = {
        'Chit Fund': chit['annual_irr'],
        'Fixed Deposit': fd['rate'],
        'Mutual Fund': mf['rate'],
        'Custom Investment': custom['rate']
    }
    
    best_option = max(options, key=options.get)
    best_return = options[best_option]
    
    if best_option == 'Chit Fund':
        st.success(f"✅ **Chit Fund is the best option** with {format_percentage(best_return)} annual return!")
        advantage = best_return - max(fd['rate'], mf['rate'], custom['rate'])
        st.info(f"💡 Advantage over next best option: **{format_percentage(advantage)}** higher returns")
    else:
        st.warning(f"⚠️ **{best_option} is better** with {format_percentage(best_return)} annual return")
        disadvantage = best_return - chit['annual_irr']
        st.info(f"💡 Chit Fund returns are **{format_percentage(disadvantage)}** lower")
    
    # Break-even analysis
    st.markdown("### ⚖️ Break-Even Analysis")
    
    if results['break_even_bid'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Current Bid Amount",
                format_currency(chit['bid_amount'])
            )
        
        with col2:
            st.metric(
                f"Break-Even Bid (vs {format_percentage(fd['rate'])} FD)",
                format_currency(results['break_even_bid']),
                delta=format_currency(results['break_even_bid'] - chit['bid_amount'])
            )
        
        if chit['bid_amount'] < results['break_even_bid']:
            margin = results['break_even_bid'] - chit['bid_amount']
            st.success(f"✅ Your bid has a safety margin of {format_currency(margin)}. You can bid up to {format_currency(results['break_even_bid'])} and still beat FD returns!")
        else:
            excess = chit['bid_amount'] - results['break_even_bid']
            st.warning(f"⚠️ Your bid is {format_currency(excess)} higher than break-even. Consider bidding lower to improve returns.")
    
    # Detailed comparison chart
    st.markdown("### 📊 Visual Comparison")
    
    import plotly.graph_objects as go
    
    comparison_data = {
        'Investment': ['Chit Fund', 'Fixed Deposit', 'Mutual Fund', 'Custom'],
        'Annual Return (%)': [
            chit['annual_irr'] * 100,
            fd['rate'] * 100,
            mf['rate'] * 100,
            custom['rate'] * 100
        ],
        'Color': ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=comparison_data['Investment'],
            y=comparison_data['Annual Return (%)'],
            marker_color=comparison_data['Color'],
            text=[f"{val:.2f}%" for val in comparison_data['Annual Return (%)']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Annual Returns Comparison",
        xaxis_title="Investment Type",
        yaxis_title="Annual Return (%)",
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown table
    st.markdown("### 📋 Detailed Breakdown")
    
    breakdown_data = {
        'Investment Type': ['Chit Fund', 'Fixed Deposit', 'Mutual Fund', 'Custom Investment'],
        'Annual Return': [
            format_percentage(chit['annual_irr']),
            format_percentage(fd['rate']),
            format_percentage(mf['rate']),
            format_percentage(custom['rate'])
        ],
        'Final Amount': [
            format_currency(chit['prize_amount']),
            format_currency(fd['final_amount']),
            format_currency(mf['final_amount']),
            format_currency(custom['final_amount'])
        ],
        'Net Gain': [
            format_currency(0),  # Already received
            format_currency(fd['gain']),
            format_currency(mf['gain']),
            format_currency(custom['gain'])
        ]
    }
    
    breakdown_df = pd.DataFrame(breakdown_data)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

