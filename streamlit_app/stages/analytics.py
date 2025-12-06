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
    tab1, tab2 = st.tabs(["🎯 Scenario Analysis", "⚖️ 3-Way Comparative Analysis"])
    
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
    """Render 3-way comparative investment analysis tab."""
    
    st.subheader("⚖️ 3-Way Investment Comparison")
    
    st.markdown("""
    Compare three investment scenarios using IRR and absolute final values:
    1. **Win Early + Lump Sum** - Win at specific installment, invest prize as lump sum
    2. **Win Late** - Don't win until last installment with varying amounts
    3. **SIP Investment** - Regular SIP matching chit frequency and amounts
    """)
    
    # Configuration section
    st.markdown("---")
    st.subheader("🎯 Scenario Configuration")
    
    # Scenario 1: Early Win Configuration
    with st.expander("📍 **Scenario 1: Win Early + Lump Sum Investment**", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            win_installment = st.number_input(
                "Win at Installment #",
                min_value=current_installment,
                max_value=chit['total_installments'] - 1,
                value=current_installment,
                step=1,
                help="At which installment you win the chit"
            )
        
        with col2:
            win_bid_amount = st.number_input(
                "Bid Amount (₹)",
                min_value=1000.0,
                max_value=float(chit['full_chit_value']) * 0.9,
                value=50000.0,
                step=1000.0,
                help="Your bid amount when you win"
            )
        
        with col3:
            lumpsum_rate = st.number_input(
                "Lump Sum Investment Rate (% p.a.)",
                min_value=0.0,
                max_value=30.0,
                value=10.0,
                step=0.5,
                help="Expected annual return on lump sum investment"
            )
    
    # Scenario 2: Late Win Configuration
    with st.expander("📍 **Scenario 2: Win Late (Last Installment)**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            late_min_installment = st.number_input(
                "Minimum Installment Amount (₹)",
                min_value=1000.0,
                max_value=float(chit['full_chit_value']),
                value=float(chit['full_chit_value']) / chit['total_installments'] * 0.8,
                step=100.0,
                help="Minimum expected installment payment"
            )
        
        with col2:
            late_max_installment = st.number_input(
                "Maximum Installment Amount (₹)",
                min_value=late_min_installment,
                max_value=float(chit['full_chit_value']),
                value=float(chit['full_chit_value']) / chit['total_installments'] * 1.2,
                step=100.0,
                help="Maximum expected installment payment"
            )
    
    # Scenario 3: SIP Configuration
    with st.expander("📍 **Scenario 3: SIP Investment**", expanded=True):
        sip_rate = st.number_input(
            "SIP Expected Return (% p.a.)",
            min_value=0.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            help="Expected annual return from SIP investment"
        )
        st.caption("ℹ️ SIP will use same varying installment amounts as Scenario 2")
    
    # Analyze button
    st.markdown("---")
    if st.button("🚀 Run 3-Way Comparison", type="primary", use_container_width=True):
        run_three_way_comparison(
            chit=chit,
            current_installment=current_installment,
            previous_amounts=previous_amounts,
            win_installment=win_installment,
            win_bid_amount=win_bid_amount,
            lumpsum_rate=lumpsum_rate / 100,
            late_min_installment=late_min_installment,
            late_max_installment=late_max_installment,
            sip_rate=sip_rate / 100
        )
    
    # Display comparison results
    if 'three_way_comparison' in st.session_state and st.session_state['three_way_comparison']:
        display_three_way_comparison(st.session_state['three_way_comparison'])


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


def run_three_way_comparison(
    chit: Dict[str, Any],
    current_installment: int,
    previous_amounts: List[Decimal],
    win_installment: int,
    win_bid_amount: float,
    lumpsum_rate: float,
    late_min_installment: float,
    late_max_installment: float,
    sip_rate: float
) -> None:
    """Run the 3-way comparison analysis using ComparativeAnalyzer."""
    
    try:
        # Create comparative analyzer
        analyzer = ComparativeAnalyzer(chit_config={
            'total_installments': chit['total_installments'],
            'full_chit_value': chit['full_chit_value'],
            'chit_frequency_per_year': chit['chit_frequency_per_year'],
            'current_installment': current_installment,
            'name': chit['name']
        })
        
        # Run comparison analysis
        result = analyzer.compare_three_scenarios(
            previous_amounts=previous_amounts,
            win_installment=win_installment,
            win_bid_amount=win_bid_amount,
            lumpsum_rate=lumpsum_rate,
            late_min_installment=late_min_installment,
            late_max_installment=late_max_installment,
            sip_rate=sip_rate
        )
        
        # Store results in session state
        st.session_state['three_way_comparison'] = result
        
        show_success("✅ 3-way comparison completed successfully!")
        
    except Exception as e:
        show_error(f"Comparison error: {str(e)}")


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


def display_three_way_comparison(result) -> None:
    """Display the 3-way comparison results with visualizations."""
    
    st.markdown("---")
    st.header("📊 3-Way Comparison Results")
    
    scenario1 = result.scenario1
    scenario2 = result.scenario2
    scenario3 = result.scenario3
    
    # ===== SUMMARY CARDS =====
    st.subheader("💰 Final Values & IRR Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Scenario 1: Win Early")
        st.metric(
            "Final Value",
            format_currency(scenario1.final_absolute_value),
            delta=format_percentage(scenario1.annual_irr)
        )
        st.caption(f"Win at #{scenario1.details['win_installment']}, Bid: {format_currency(scenario1.details['bid_amount'])}")
    
    with col2:
        st.markdown("#### 📅 Scenario 2: Win Late")
        st.metric(
            "Final Value",
            format_currency(scenario2.final_absolute_value),
            delta=format_percentage(scenario2.annual_irr)
        )
        st.caption(f"Win at last, Avg: {format_currency(scenario2.details['avg_installment'])}")
    
    with col3:
        st.markdown("#### 📈 Scenario 3: SIP")
        st.metric(
            "Final Value",
            format_currency(scenario3.final_absolute_value),
            delta=format_percentage(scenario3.annual_irr)
        )
        st.caption(f"Rate: {format_percentage(scenario3.details['sip_rate'])}")
    
    # ===== WINNER ANNOUNCEMENT =====
    st.markdown("---")
    st.subheader("🏆 Best Strategy")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.success(f"✅ **{result.best_scenario_name}** is the best strategy!")
        st.markdown(f"**Advantage:** {format_currency(result.advantage_amount)} over next best option")
    
    with col2:
        emoji_map = {
            'Early Win + Lump Sum': "🎯",
            'Late Win (Last Installment)': "📅",
            'SIP Investment': "📈"
        }
        emoji = emoji_map.get(result.best_scenario_name, "🏆")
        
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background-color: #10b981; border-radius: 10px;'>
            <h1 style='font-size: 60px; margin: 0;'>{emoji}</h1>
            <p style='color: white; margin: 10px 0 0 0;'><strong>Winner!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== COMPARISON CHARTS =====
    st.markdown("---")
    st.subheader("📊 Visual Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Final values comparison
        fig_values = go.Figure(data=[
            go.Bar(
                x=['Win Early', 'Win Late', 'SIP'],
                y=[
                    float(scenario1.final_absolute_value),
                    float(scenario2.final_absolute_value),
                    float(scenario3.final_absolute_value)
                ],
                marker_color=['#3b82f6', '#10b981', '#f59e0b'],
                text=[
                    format_currency(scenario1.final_absolute_value),
                    format_currency(scenario2.final_absolute_value),
                    format_currency(scenario3.final_absolute_value)
                ],
                textposition='outside'
            )
        ])
        
        fig_values.update_layout(
            title="Final Absolute Values",
            yaxis_title="Final Value (₹)",
            height=350,
            template='plotly_white',
            showlegend=False
        )
        
        st.plotly_chart(fig_values, use_container_width=True)
    
    with col2:
        # IRR comparison
        fig_irr = go.Figure(data=[
            go.Bar(
                x=['Win Early', 'Win Late', 'SIP'],
                y=[
                    scenario1.annual_irr * 100,
                    scenario2.annual_irr * 100,
                    scenario3.annual_irr * 100
                ],
                marker_color=['#3b82f6', '#10b981', '#f59e0b'],
                text=[
                    f"{scenario1.annual_irr * 100:.2f}%",
                    f"{scenario2.annual_irr * 100:.2f}%",
                    f"{scenario3.annual_irr * 100:.2f}%"
                ],
                textposition='outside'
            )
        ])
        
        fig_irr.update_layout(
            title="Annual IRR (%)",
            yaxis_title="IRR (%)",
            height=350,
            template='plotly_white',
            showlegend=False
        )
        
        st.plotly_chart(fig_irr, use_container_width=True)
    
    # ===== DETAILED BREAKDOWN =====
    st.markdown("---")
    st.subheader("📋 Detailed Breakdown")
    
    tab1, tab2, tab3 = st.tabs([
        "🎯 Scenario 1: Win Early",
        "📅 Scenario 2: Win Late",
        "📈 Scenario 3: SIP"
    ])
    
    with tab1:
        st.markdown("##### Early Win + Lump Sum Investment Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Chit Details:**")
            st.write(f"• Win Installment: **#{scenario1.details['win_installment']}**")
            st.write(f"• Bid Amount: **{format_currency(scenario1.details['bid_amount'])}**")
            st.write(f"• Prize Received: **{format_currency(scenario1.details['prize_amount'])}**")
            st.write(f"• Total Invested: **{format_currency(scenario1.total_invested)}**")
        
        with col2:
            st.markdown("**Lump Sum Investment:**")
            st.write(f"• Investment: **{format_currency(scenario1.details['lumpsum_investment'])}**")
            st.write(f"• Rate: **{format_percentage(scenario1.details['lumpsum_rate'])}**")
            st.write(f"• Periods: **{scenario1.details['remaining_periods']}**")
            st.write(f"• Final Value: **{format_currency(scenario1.details['lumpsum_final_value'])}**")
        
        st.markdown("---")
        st.metric("Annual IRR", format_percentage(scenario1.annual_irr))
        st.metric("Net Gain", format_currency(scenario1.net_gain))
    
    with tab2:
        st.markdown("##### Late Win (Last Installment) Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Chit Details:**")
            st.write(f"• Win at: **Last Installment**")
            st.write(f"• Bid Amount: **{format_currency(scenario2.details['bid_amount'])}**")
            st.write(f"• Prize Received: **{format_currency(scenario2.details['prize_amount'])}**")
            st.write(f"• Total Invested: **{format_currency(scenario2.total_invested)}**")
        
        with col2:
            st.markdown("**Installment Range:**")
            st.write(f"• Min: **{format_currency(scenario2.details['min_installment'])}**")
            st.write(f"• Max: **{format_currency(scenario2.details['max_installment'])}**")
            st.write(f"• Average: **{format_currency(scenario2.details['avg_installment'])}**")
            st.write(f"• Installments Paid: **{scenario2.details['total_installments_paid']}**")
        
        st.markdown("---")
        st.metric("Annual IRR", format_percentage(scenario2.annual_irr))
        st.metric("Net Gain", format_currency(scenario2.net_gain))
    
    with tab3:
        st.markdown("##### SIP Investment Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**SIP Configuration:**")
            st.write(f"• Rate: **{format_percentage(scenario3.details['sip_rate'])}**")
            st.write(f"• Total SIPs: **{scenario3.details['total_sips']}**")
            st.write(f"• Total Invested: **{format_currency(scenario3.total_invested)}**")
        
        with col2:
            st.markdown("**Returns:**")
            st.write(f"• Maturity Value: **{format_currency(scenario3.details['sip_maturity'])}**")
            st.write(f"• Net Gain: **{format_currency(scenario3.net_gain)}**")
        
        st.markdown("---")
        st.metric("Annual IRR (CAGR)", format_percentage(scenario3.annual_irr))
        st.metric("Net Gain", format_currency(scenario3.net_gain))
    
    # ===== SUMMARY TABLE =====
    st.markdown("---")
    st.subheader("📊 Summary Table")
    
    summary_data = {
        'Strategy': [scenario1.scenario_name, scenario2.scenario_name, scenario3.scenario_name],
        'Total Invested': [
            format_currency(scenario1.total_invested),
            format_currency(scenario2.total_invested),
            format_currency(scenario3.total_invested)
        ],
        'Final Value': [
            format_currency(scenario1.final_absolute_value),
            format_currency(scenario2.final_absolute_value),
            format_currency(scenario3.final_absolute_value)
        ],
        'Net Gain': [
            format_currency(scenario1.net_gain),
            format_currency(scenario2.net_gain),
            format_currency(scenario3.net_gain)
        ],
        'Annual IRR': [
            format_percentage(scenario1.annual_irr),
            format_percentage(scenario2.annual_irr),
            format_percentage(scenario3.annual_irr)
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # ===== EXPORT BUTTON =====
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        excel_data = create_downloadable_df(summary_df, "three_way_comparison.xlsx")
        
        st.download_button(
            label="📥 Download Comparison Report",
            data=excel_data,
            file_name=f"chit_3way_comparison_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
