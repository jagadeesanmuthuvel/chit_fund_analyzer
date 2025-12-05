"""
Utility functions for chit fund analysis.

This module provides helper functions and utilities that support
the main analysis functionality.
"""

from typing import List, Dict, Any, Union
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


def format_currency(amount: Union[Decimal, float], currency_symbol: str = "₹") -> str:
    """
    Format amount as currency with proper formatting.
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use
        
    Returns:
        Formatted currency string
    """
    return f"{currency_symbol}{float(amount):,.2f}"


def format_percentage(rate: float, decimal_places: int = 2) -> str:
    """
    Format rate as percentage.
    
    Args:
        rate: Rate as decimal (e.g., 0.15 for 15%)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{rate:.{decimal_places}%}"


def round_to_nearest(amount: Decimal, nearest: Decimal = Decimal('1')) -> Decimal:
    """
    Round amount to nearest specified value.
    
    Args:
        amount: Amount to round
        nearest: Value to round to (e.g., Decimal('1000') for nearest thousand)
        
    Returns:
        Rounded amount
    """
    return (amount / nearest).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * nearest


def validate_cashflow_signs(cashflows: List[Decimal]) -> bool:
    """
    Validate that cashflows have both positive and negative values for IRR calculation.
    
    Args:
        cashflows: List of cashflow values
        
    Returns:
        True if valid cashflow pattern exists
    """
    has_positive = any(cf > 0 for cf in cashflows)
    has_negative = any(cf < 0 for cf in cashflows)
    return has_positive and has_negative


def create_summary_stats(scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create summary statistics for a list of scenarios.
    
    Args:
        scenarios: List of scenario dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
    if not scenarios:
        return {}
    
    # Extract IRR values
    irr_values = [scenario.get('annual_irr', 0) for scenario in scenarios]
    bid_amounts = [scenario.get('bid_amount', 0) for scenario in scenarios]
    prize_amounts = [scenario.get('prize_amount', 0) for scenario in scenarios]
    
    return {
        'total_scenarios': len(scenarios),
        'irr_stats': {
            'min': min(irr_values),
            'max': max(irr_values),
            'mean': sum(irr_values) / len(irr_values),
            'median': sorted(irr_values)[len(irr_values) // 2]
        },
        'bid_range': {
            'min': min(bid_amounts),
            'max': max(bid_amounts)
        },
        'prize_range': {
            'min': min(prize_amounts),
            'max': max(prize_amounts)
        }
    }


def export_to_excel(
    dataframes: Dict[str, pd.DataFrame], 
    filename: str,
    include_charts: bool = False
) -> str:
    """
    Export multiple dataframes to Excel file with separate sheets.
    
    Args:
        dataframes: Dictionary mapping sheet names to DataFrames
        filename: Output filename
        include_charts: Whether to include basic charts
        
    Returns:
        Path to created file
    """
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    return filename


def generate_bid_range(
    min_bid: Union[Decimal, float],
    max_bid: Union[Decimal, float],
    num_scenarios: int = 10
) -> List[Decimal]:
    """
    Generate evenly spaced bid amounts for scenario analysis.
    
    Args:
        min_bid: Minimum bid amount
        max_bid: Maximum bid amount
        num_scenarios: Number of scenarios to generate
        
    Returns:
        List of bid amounts
    """
    min_bid = Decimal(str(min_bid))
    max_bid = Decimal(str(max_bid))
    
    if num_scenarios <= 1:
        return [min_bid]
    
    step = (max_bid - min_bid) / (num_scenarios - 1)
    return [min_bid + (step * i) for i in range(num_scenarios)]


class ChitFundFormatter:
    """
    Utility class for consistent formatting of chit fund data.
    """
    
    @staticmethod
    def format_analysis_summary(result) -> str:
        """
        Format analysis result as a readable summary.
        
        Args:
            result: ChitFundAnalysisResult instance
            
        Returns:
            Formatted summary string
        """
        lines = [
            "=== CHIT FUND ANALYSIS SUMMARY ===",
            f"Total Installments: {result.config.total_installments}",
            f"Current Installment: {result.config.current_installment_number}",
            f"Full Chit Value: {format_currency(result.config.full_chit_value)}",
            f"Bid Amount: {format_currency(result.config.bid_amount)}",
            f"Prize Amount: {format_currency(result.prize_amount)}",
            f"Winner Installment: {format_currency(result.config.get_winner_installment_amount())}",
            "",
            "=== RETURNS ===",
            f"Annual IRR: {format_percentage(result.annual_irr)}",
            f"Period IRR: {format_percentage(result.period_irr, 4)}",
            f"Payment Frequency: {result.config.chit_frequency_per_year} times per year",
            "===============================",
        ]
        return "\n".join(lines)
    
    @staticmethod
    def format_scenario_comparison(scenarios: List) -> str:
        """
        Format scenario comparison as a readable table.
        
        Args:
            scenarios: List of BidScenario instances
            
        Returns:
            Formatted comparison string
        """
        if not scenarios:
            return "No scenarios to display"
        
        lines = ["=== BID SCENARIO COMPARISON ==="]
        lines.append(f"{'Bid Amount':<15} {'Prize Amount':<15} {'Annual IRR':<12}")
        lines.append("-" * 45)
        
        for scenario in scenarios:
            lines.append(
                f"{format_currency(scenario.bid_amount):<15} "
                f"{format_currency(scenario.prize_amount):<15} "
                f"{format_percentage(scenario.annual_irr):<12}"
            )
        
        lines.append("=" * 45)
        return "\n".join(lines)