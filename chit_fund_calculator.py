"""
Chit Fund Calculator Module

This module provides classes and utilities for analyzing chit fund investments,
calculating IRR, and performing scenario analysis for different bid amounts.

Author: Jagadeesan Muthuvel
Date: December 4, 2025
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import numpy_financial as npf
import pandas as pd


class ChitFrequency(Enum):
    """Enum representing chit fund payment frequencies."""
    MONTHLY = 12
    QUARTERLY = 4
    SEMI_ANNUAL = 2
    ANNUAL = 1


@dataclass
class ChitFundConfig:
    """
    Configuration for a chit fund investment.
    
    Attributes:
        total_installments: Total number of installments in the chit fund
        current_installment_number: Current installment number (when winning)
        full_chit_value: Total value of the chit fund
        chit_frequency_per_year: Number of payments per year
        previous_installments: List of previous installment amounts paid
        winner_installment_amount: Fixed amount winner pays after winning
    """
    total_installments: int
    current_installment_number: int
    full_chit_value: float
    chit_frequency_per_year: int
    previous_installments: List[float]
    winner_installment_amount: float = 50000.0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate the configuration parameters."""
        if self.total_installments <= 0:
            raise ValueError("Total installments must be positive")
        
        if self.current_installment_number > self.total_installments:
            raise ValueError("Current installment cannot exceed total installments")
        
        if self.full_chit_value <= 0:
            raise ValueError("Chit value must be positive")
        
        if self.chit_frequency_per_year not in [freq.value for freq in ChitFrequency]:
            raise ValueError(f"Invalid frequency. Must be one of: {[f.value for f in ChitFrequency]}")
        
        if len(self.previous_installments) != self.current_installment_number - 1:
            raise ValueError(
                f"Expected {self.current_installment_number - 1} previous installments, "
                f"got {len(self.previous_installments)}"
            )


@dataclass
class ChitFundResult:
    """
    Result of a chit fund analysis.
    
    Attributes:
        bid_amount: Amount bid in the auction
        prize_amount: Amount received as prize
        total_repayment: Total amount to be repaid
        net_interest_cost: Total interest paid
        annual_irr: Annual Internal Rate of Return
        effective_interest_rate: Effective interest rate percentage
        cashflows: List of cashflows for the investment
    """
    bid_amount: float
    prize_amount: float
    total_repayment: float
    net_interest_cost: float
    annual_irr: float
    effective_interest_rate: float
    cashflows: List[float] = field(repr=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            'Bid Amount': self.bid_amount,
            'Prize Received': self.prize_amount,
            'Total Repayment': self.total_repayment,
            'Net Interest Cost': self.net_interest_cost,
            'Annual IRR (%)': self.annual_irr * 100,
            'Effective Interest (%)': self.effective_interest_rate * 100
        }


class ChitFundCalculator:
    """
    Calculator for chit fund financial analysis.
    
    This class provides methods to calculate prize amounts, cashflows,
    and Internal Rate of Return (IRR) for chit fund investments.
    """
    
    @staticmethod
    def calculate_prize_amount(full_chit_value: float, bid_amount: float) -> float:
        """
        Calculate the prize amount received by the winner.
        
        Args:
            full_chit_value: Total value of the chit fund
            bid_amount: Amount bid in the auction
            
        Returns:
            Prize amount (chit value minus bid amount)
        """
        if bid_amount < 0:
            raise ValueError("Bid amount cannot be negative")
        if bid_amount >= full_chit_value:
            raise ValueError("Bid amount must be less than chit value")
        
        return full_chit_value - bid_amount
    
    @staticmethod
    def create_cashflows(
        previous_installments: List[float],
        prize_amount: float,
        winner_installment_amount: float,
        current_installment_number: int,
        total_installments: int
    ) -> List[float]:
        """
        Create cashflow list for IRR calculation.
        
        Cashflow convention:
        - Negative values: Money paid out (installments)
        - Positive values: Money received (prize)
        
        Args:
            previous_installments: List of previous installment amounts
            prize_amount: Prize amount received
            winner_installment_amount: Fixed amount paid after winning
            current_installment_number: Current installment number
            total_installments: Total number of installments
            
        Returns:
            List of cashflows
        """
        remaining_installments = total_installments - current_installment_number
        future_winner_installments = [-winner_installment_amount] * remaining_installments
        
        cashflows = (
            [-amount for amount in previous_installments]
            + [prize_amount]
            + future_winner_installments
        )
        
        return cashflows
    
    @staticmethod
    def calculate_annual_irr(cashflows: List[float], frequency_per_year: int) -> float:
        """
        Calculate annual Internal Rate of Return (IRR).
        
        Args:
            cashflows: List of cashflows
            frequency_per_year: Number of payment periods per year
            
        Returns:
            Annual IRR as a decimal (e.g., 0.15 for 15%)
            
        Raises:
            ValueError: If IRR cannot be calculated
        """
        try:
            irr_per_period = npf.irr(cashflows)
            
            if irr_per_period is None or pd.isna(irr_per_period):
                raise ValueError("IRR calculation failed - no solution found")
            
            annual_irr = ((1 + irr_per_period) ** frequency_per_year) - 1
            return annual_irr
        
        except Exception as e:
            raise ValueError(f"Failed to calculate IRR: {str(e)}")
    
    def analyze_single_bid(
        self,
        config: ChitFundConfig,
        bid_amount: float
    ) -> ChitFundResult:
        """
        Analyze a single bid amount scenario.
        
        Args:
            config: Chit fund configuration
            bid_amount: Bid amount to analyze
            
        Returns:
            ChitFundResult object with analysis results
        """
        prize_amount = self.calculate_prize_amount(config.full_chit_value, bid_amount)
        
        cashflows = self.create_cashflows(
            config.previous_installments,
            prize_amount,
            config.winner_installment_amount,
            config.current_installment_number,
            config.total_installments
        )
        
        annual_irr = self.calculate_annual_irr(cashflows, config.chit_frequency_per_year)
        
        # Calculate financial metrics
        total_paid_before = sum(config.previous_installments)
        total_paid_after = config.winner_installment_amount * (
            config.total_installments - config.current_installment_number
        )
        total_repayment = total_paid_before + total_paid_after
        net_interest_cost = total_repayment - prize_amount
        effective_interest_rate = net_interest_cost / prize_amount
        
        return ChitFundResult(
            bid_amount=bid_amount,
            prize_amount=prize_amount,
            total_repayment=total_repayment,
            net_interest_cost=net_interest_cost,
            annual_irr=annual_irr,
            effective_interest_rate=effective_interest_rate,
            cashflows=cashflows
        )


class ScenarioAnalyzer:
    """
    Analyzer for comparing multiple bid scenarios.
    
    This class provides methods to analyze and compare different bid amounts
    to identify optimal bidding strategies.
    """
    
    def __init__(self, calculator: Optional[ChitFundCalculator] = None):
        """
        Initialize scenario analyzer.
        
        Args:
            calculator: ChitFundCalculator instance (creates new if None)
        """
        self.calculator = calculator or ChitFundCalculator()
    
    def analyze_scenarios(
        self,
        config: ChitFundConfig,
        bid_amounts: Optional[List[float]] = None,
        bid_range: Optional[tuple] = None,
        bid_step: float = 10000
    ) -> pd.DataFrame:
        """
        Analyze multiple bid amount scenarios.
        
        Args:
            config: Chit fund configuration
            bid_amounts: List of specific bid amounts to test
            bid_range: Tuple of (min_bid, max_bid) for range testing
            bid_step: Step size for bid range (default: 10000)
            
        Returns:
            DataFrame with scenario analysis results
        """
        # Determine bid amounts to test
        if bid_amounts is None:
            if bid_range is None:
                bid_range = (50000, 200000)
            bid_amounts = range(int(bid_range[0]), int(bid_range[1]) + 1, int(bid_step))
        
        results = []
        
        for bid_amount in bid_amounts:
            try:
                result = self.calculator.analyze_single_bid(config, bid_amount)
                results.append(result.to_dict())
            except Exception as e:
                # Add placeholder for failed calculations
                results.append({
                    'Bid Amount': bid_amount,
                    'Prize Received': None,
                    'Total Repayment': None,
                    'Net Interest Cost': None,
                    'Annual IRR (%)': None,
                    'Effective Interest (%)': None,
                    'Error': str(e)
                })
        
        df = pd.DataFrame(results)
        return df
    
    def find_optimal_bid(
        self,
        config: ChitFundConfig,
        bid_amounts: Optional[List[float]] = None,
        bid_range: Optional[tuple] = None,
        bid_step: float = 10000,
        optimization_metric: str = 'Annual IRR (%)'
    ) -> Dict[str, Any]:
        """
        Find the optimal bid amount based on specified metric.
        
        Args:
            config: Chit fund configuration
            bid_amounts: List of specific bid amounts to test
            bid_range: Tuple of (min_bid, max_bid) for range testing
            bid_step: Step size for bid range
            optimization_metric: Metric to optimize (default: 'Annual IRR (%)')
            
        Returns:
            Dictionary with optimal bid details
        """
        df = self.analyze_scenarios(config, bid_amounts, bid_range, bid_step)
        
        # Remove rows with errors
        df_valid = df[df[optimization_metric].notna()]
        
        if df_valid.empty:
            raise ValueError("No valid scenarios found")
        
        # Find optimal (minimum IRR is best)
        optimal_idx = df_valid[optimization_metric].idxmin()
        optimal_row = df_valid.loc[optimal_idx]
        
        return {
            'bid_amount': optimal_row['Bid Amount'],
            'prize_received': optimal_row['Prize Received'],
            'annual_irr': optimal_row['Annual IRR (%)'],
            'net_interest_cost': optimal_row['Net Interest Cost'],
            'total_repayment': optimal_row['Total Repayment'],
            'effective_interest': optimal_row['Effective Interest (%)']
        }


class ReportGenerator:
    """Generate formatted reports for chit fund analysis."""
    
    @staticmethod
    def print_scenario_analysis(
        df: pd.DataFrame,
        title: str = "BID AMOUNT SCENARIO ANALYSIS"
    ) -> None:
        """
        Print formatted scenario analysis table.
        
        Args:
            df: DataFrame with scenario results
            title: Report title
        """
        print("=" * 80)
        print(title.center(80))
        print("=" * 80)
        
        # Format display
        pd.options.display.float_format = '{:,.2f}'.format
        print(df.to_string(index=False))
    
    @staticmethod
    def print_optimal_strategy(
        optimal_result: Dict[str, Any],
        title: str = "OPTIMAL BID STRATEGY"
    ) -> None:
        """
        Print formatted optimal strategy report.
        
        Args:
            optimal_result: Dictionary with optimal bid details
            title: Report title
        """
        print("\n" + "=" * 80)
        print(title.center(80))
        print("=" * 80)
        print(f"Bid Amount: ₹{optimal_result['bid_amount']:,.0f}")
        print(f"Prize Received: ₹{optimal_result['prize_received']:,.0f}")
        print(f"Annual IRR: {optimal_result['annual_irr']:.2f}%")
        print(f"Net Interest Cost: ₹{optimal_result['net_interest_cost']:,.0f}")
        print(f"Total Repayment: ₹{optimal_result['total_repayment']:,.0f}")
        print(f"Effective Interest: {optimal_result['effective_interest']:.2f}%")
        print("=" * 80)
    
    @staticmethod
    def export_to_csv(
        df: pd.DataFrame,
        filename: str = "chit_fund_analysis.csv"
    ) -> None:
        """
        Export scenario analysis to CSV file.
        
        Args:
            df: DataFrame with scenario results
            filename: Output filename
        """
        df.to_csv(filename, index=False)
        print(f"\nAnalysis exported to {filename}")
