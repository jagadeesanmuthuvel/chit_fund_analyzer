"""
Advanced Examples for Chit Fund Calculator

This script demonstrates advanced usage patterns and extension capabilities.
"""

from chit_fund_calculator import (
    ChitFundConfig,
    ChitFundCalculator,
    ScenarioAnalyzer,
    ReportGenerator,
    ChitFrequency
)
import pandas as pd


def example_1_basic_analysis():
    """Example 1: Basic single bid analysis."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Single Bid Analysis")
    print("="*80)
    
    config = ChitFundConfig(
        total_installments=14,
        current_installment_number=4,
        full_chit_value=700000,
        chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
        previous_installments=[42000, 40000, 40000, 43000],
        winner_installment_amount=50000
    )
    
    calculator = ChitFundCalculator()
    result = calculator.analyze_single_bid(config, bid_amount=100000)
    
    print(f"\nBid Amount: ₹{result.bid_amount:,.0f}")
    print(f"Prize Received: ₹{result.prize_amount:,.0f}")
    print(f"Annual IRR: {result.annual_irr * 100:.2f}%")
    print(f"Net Interest Cost: ₹{result.net_interest_cost:,.0f}")


def example_2_scenario_comparison():
    """Example 2: Compare multiple scenarios."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Scenario Comparison")
    print("="*80)
    
    config = ChitFundConfig(
        total_installments=14,
        current_installment_number=4,
        full_chit_value=700000,
        chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
        previous_installments=[42000, 40000, 40000, 43000],
        winner_installment_amount=50000
    )
    
    analyzer = ScenarioAnalyzer()
    
    # Analyze specific bid amounts
    custom_bids = [75000, 100000, 125000, 150000, 175000]
    results = analyzer.analyze_scenarios(config=config, bid_amounts=custom_bids)
    
    report = ReportGenerator()
    report.print_scenario_analysis(results, "Custom Bid Scenarios")


def example_3_find_optimal():
    """Example 3: Find optimal bid automatically."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Find Optimal Bid")
    print("="*80)
    
    config = ChitFundConfig(
        total_installments=14,
        current_installment_number=4,
        full_chit_value=700000,
        chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
        previous_installments=[42000, 40000, 40000, 43000],
        winner_installment_amount=50000
    )
    
    analyzer = ScenarioAnalyzer()
    optimal = analyzer.find_optimal_bid(
        config=config,
        bid_range=(50000, 200000),
        bid_step=5000  # Fine-grained search
    )
    
    report = ReportGenerator()
    report.print_optimal_strategy(optimal)


def example_4_different_frequencies():
    """Example 4: Compare different payment frequencies."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Different Payment Frequencies")
    print("="*80)
    
    frequencies = [
        (ChitFrequency.MONTHLY, "Monthly"),
        (ChitFrequency.QUARTERLY, "Quarterly"),
        (ChitFrequency.SEMI_ANNUAL, "Semi-Annual"),
        (ChitFrequency.ANNUAL, "Annual")
    ]
    
    calculator = ChitFundCalculator()
    results = []
    
    for freq, name in frequencies:
        # Adjust installments based on frequency
        total_inst = 24 if freq == ChitFrequency.MONTHLY else 12
        current_inst = 6 if freq == ChitFrequency.MONTHLY else 4
        prev_inst = [50000] * (current_inst - 1)
        
        config = ChitFundConfig(
            total_installments=total_inst,
            current_installment_number=current_inst,
            full_chit_value=700000,
            chit_frequency_per_year=freq.value,
            previous_installments=prev_inst,
            winner_installment_amount=50000
        )
        
        result = calculator.analyze_single_bid(config, 100000)
        results.append({
            'Frequency': name,
            'Total Installments': total_inst,
            'Annual IRR (%)': result.annual_irr * 100,
            'Prize Amount': result.prize_amount,
            'Net Interest': result.net_interest_cost
        })
    
    df = pd.DataFrame(results)
    print("\nFrequency Comparison:")
    print(df.to_string(index=False))


def example_5_export_results():
    """Example 5: Export results to CSV."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Export Results to CSV")
    print("="*80)
    
    config = ChitFundConfig(
        total_installments=14,
        current_installment_number=4,
        full_chit_value=700000,
        chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
        previous_installments=[42000, 40000, 40000, 43000],
        winner_installment_amount=50000
    )
    
    analyzer = ScenarioAnalyzer()
    results = analyzer.analyze_scenarios(
        config=config,
        bid_range=(50000, 200000),
        bid_step=10000
    )
    
    report = ReportGenerator()
    filename = "chit_fund_analysis_export.csv"
    report.export_to_csv(results, filename)
    print(f"\n✓ Results exported to {filename}")


def example_6_custom_extension():
    """Example 6: Extend with custom analysis."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Custom Extension - ROI Analysis")
    print("="*80)
    
    class ExtendedAnalyzer(ScenarioAnalyzer):
        """Extended analyzer with ROI calculation."""
        
        def calculate_roi_scenarios(
            self,
            config: ChitFundConfig,
            bid_range: tuple = (50000, 200000),
            bid_step: float = 10000
        ) -> pd.DataFrame:
            """Calculate ROI for different scenarios."""
            df = self.analyze_scenarios(config, bid_range=bid_range, bid_step=bid_step)
            
            # Add ROI calculation (simple return on investment)
            df['ROI (%)'] = ((df['Prize Received'] - df['Total Repayment']) / 
                             df['Total Repayment'] * 100)
            
            return df
    
    config = ChitFundConfig(
        total_installments=14,
        current_installment_number=4,
        full_chit_value=700000,
        chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
        previous_installments=[42000, 40000, 40000, 43000],
        winner_installment_amount=50000
    )
    
    extended_analyzer = ExtendedAnalyzer()
    results = extended_analyzer.calculate_roi_scenarios(
        config=config,
        bid_range=(50000, 150000),
        bid_step=25000
    )
    
    print("\nExtended Analysis with ROI:")
    pd.options.display.float_format = '{:,.2f}'.format
    print(results.to_string(index=False))


def example_7_sensitivity_analysis():
    """Example 7: Sensitivity analysis for winner installment amount."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Sensitivity Analysis")
    print("="*80)
    
    base_config_params = {
        'total_installments': 14,
        'current_installment_number': 4,
        'full_chit_value': 700000,
        'chit_frequency_per_year': ChitFrequency.SEMI_ANNUAL.value,
        'previous_installments': [42000, 40000, 40000, 43000],
    }
    
    winner_amounts = [45000, 50000, 55000, 60000]
    bid_amount = 100000
    calculator = ChitFundCalculator()
    
    results = []
    for winner_amt in winner_amounts:
        config = ChitFundConfig(
            **base_config_params,
            winner_installment_amount=winner_amt
        )
        
        result = calculator.analyze_single_bid(config, bid_amount)
        results.append({
            'Winner Installment': winner_amt,
            'Prize Amount': result.prize_amount,
            'Total Repayment': result.total_repayment,
            'Annual IRR (%)': result.annual_irr * 100,
            'Net Interest': result.net_interest_cost
        })
    
    df = pd.DataFrame(results)
    print(f"\nSensitivity Analysis (Bid Amount: ₹{bid_amount:,.0f}):")
    pd.options.display.float_format = '{:,.2f}'.format
    print(df.to_string(index=False))


def example_8_comparison_multiple_chits():
    """Example 8: Compare multiple chit funds."""
    print("\n" + "="*80)
    print("EXAMPLE 8: Compare Multiple Chit Funds")
    print("="*80)
    
    chit_configs = [
        {
            'name': 'Chit Fund A - Semi-Annual',
            'config': ChitFundConfig(
                total_installments=14,
                current_installment_number=4,
                full_chit_value=700000,
                chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
                previous_installments=[42000, 40000, 40000, 43000],
                winner_installment_amount=50000
            ),
            'bid': 100000
        },
        {
            'name': 'Chit Fund B - Quarterly',
            'config': ChitFundConfig(
                total_installments=12,
                current_installment_number=4,
                full_chit_value=600000,
                chit_frequency_per_year=ChitFrequency.QUARTERLY.value,
                previous_installments=[50000, 48000, 49000],
                winner_installment_amount=50000
            ),
            'bid': 100000
        },
        {
            'name': 'Chit Fund C - Monthly',
            'config': ChitFundConfig(
                total_installments=24,
                current_installment_number=6,
                full_chit_value=500000,
                chit_frequency_per_year=ChitFrequency.MONTHLY.value,
                previous_installments=[21000, 20000, 20000, 21000, 20000],
                winner_installment_amount=20000
            ),
            'bid': 80000
        }
    ]
    
    calculator = ChitFundCalculator()
    results = []
    
    for chit in chit_configs:
        result = calculator.analyze_single_bid(chit['config'], chit['bid'])
        results.append({
            'Chit Fund': chit['name'],
            'Bid Amount': result.bid_amount,
            'Prize Received': result.prize_amount,
            'Annual IRR (%)': result.annual_irr * 100,
            'Total Repayment': result.total_repayment,
            'Net Interest': result.net_interest_cost
        })
    
    df = pd.DataFrame(results)
    print("\nChit Fund Comparison:")
    pd.options.display.float_format = '{:,.2f}'.format
    print(df.to_string(index=False))
    
    # Find best option
    best_idx = df['Annual IRR (%)'].idxmin()
    print(f"\n✓ Best Option: {df.loc[best_idx, 'Chit Fund']}")
    print(f"  Annual IRR: {df.loc[best_idx, 'Annual IRR (%)']:.2f}%")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("CHIT FUND CALCULATOR - ADVANCED EXAMPLES")
    print("="*80)
    
    examples = [
        example_1_basic_analysis,
        example_2_scenario_comparison,
        example_3_find_optimal,
        example_4_different_frequencies,
        example_5_export_results,
        example_6_custom_extension,
        example_7_sensitivity_analysis,
        example_8_comparison_multiple_chits
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()
