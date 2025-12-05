"""
Core chit fund analysis functionality.

This module contains the main ChitFundAnalyzer class that performs
chit fund calculations including prize amounts, cashflow generation,
and IRR calculations.
"""

from typing import List, Tuple
from decimal import Decimal
import numpy_financial as npf
import numpy as np

from .models import ChitFundConfig, ChitFundAnalysisResult
from .exceptions import ChitFundAnalysisError


class ChitFundAnalyzer:
    """
    Main analyzer class for chit fund calculations.
    
    This class provides methods to calculate prize amounts, generate cashflows,
    and compute Internal Rate of Return (IRR) for chit fund investments.
    """

    def __init__(self, config: ChitFundConfig):
        """
        Initialize the analyzer with chit fund configuration.
        
        Args:
            config: Validated ChitFundConfig instance
            
        Raises:
            ChitFundAnalysisError: If configuration is invalid
        """
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """Additional validation for the configuration."""
        if not self.config.previous_installments:
            if self.config.current_installment_number > 1:
                raise ChitFundAnalysisError(
                    "Previous installments required for current installment > 1"
                )

    def calculate_prize_amount(self) -> Decimal:
        """
        Calculate the prize amount for the chit fund winner.
        
        Prize amount = Full chit value - Bid amount - Winner installment amount
        
        Returns:
            Calculated prize amount
            
        Raises:
            ChitFundAnalysisError: If calculation results in negative prize
        """
        winner_installment = self.config.get_winner_installment_amount()
        prize_amount = (
            self.config.full_chit_value 
            - self.config.bid_amount 
            - winner_installment
        )
        
        if prize_amount <= 0:
            raise ChitFundAnalysisError(
                f"Prize amount ({prize_amount}) must be positive. "
                f"Check bid amount and winner installment values."
            )
        
        return prize_amount

    def generate_cashflows(self, prize_amount: Decimal) -> List[Decimal]:
        """
        Generate cashflow array for IRR calculation.
        
        Cashflows include:
        - Negative values for previous installments (outflows)
        - Positive value for prize amount (inflow)
        - Negative values for future winner installments (outflows)
        
        Args:
            prize_amount: The calculated prize amount
            
        Returns:
            List of cashflow values
        """
        winner_installment = self.config.get_winner_installment_amount()
        
        # Previous installments as negative cashflows (money paid out)
        previous_cashflows = [-amount for amount in self.config.previous_installments]
        
        # Prize amount as positive cashflow (money received)
        prize_cashflow = [prize_amount]
        
        # Future installments as negative cashflows (money to be paid)
        remaining_installments = (
            self.config.total_installments - self.config.current_installment_number
        )
        future_cashflows = [-winner_installment] * remaining_installments
        
        # Combine all cashflows
        cashflows = previous_cashflows + prize_cashflow + future_cashflows
        
        return [Decimal(str(cf)) for cf in cashflows]

    def calculate_irr(self, cashflows: List[Decimal]) -> Tuple[float, float]:
        """
        Calculate Internal Rate of Return (IRR) for the cashflows.
        
        Args:
            cashflows: List of cashflow values
            
        Returns:
            Tuple of (period_irr, annual_irr)
            
        Raises:
            ChitFundAnalysisError: If IRR calculation fails
        """
        try:
            # Convert to float array for numpy-financial
            cf_array = np.array([float(cf) for cf in cashflows])
            
            # Calculate IRR per period
            period_irr = npf.irr(cf_array)
            
            if period_irr is None or np.isnan(period_irr):
                raise ChitFundAnalysisError(
                    "IRR calculation failed. Check cashflow values."
                )
            
            # Convert to annual IRR
            annual_irr = ((1 + period_irr) ** self.config.chit_frequency_per_year) - 1
            
            return period_irr, annual_irr
            
        except Exception as e:
            raise ChitFundAnalysisError(f"IRR calculation error: {str(e)}")

    def analyze(self) -> ChitFundAnalysisResult:
        """
        Perform complete chit fund analysis.
        
        Returns:
            ChitFundAnalysisResult with all calculated values
            
        Raises:
            ChitFundAnalysisError: If analysis fails at any step
        """
        try:
            # Calculate prize amount
            prize_amount = self.calculate_prize_amount()
            
            # Generate cashflows
            cashflows = self.generate_cashflows(prize_amount)
            
            # Calculate IRR
            period_irr, annual_irr = self.calculate_irr(cashflows)
            
            return ChitFundAnalysisResult(
                config=self.config,
                prize_amount=prize_amount,
                cashflows=cashflows,
                annual_irr=annual_irr,
                period_irr=period_irr
            )
            
        except Exception as e:
            if isinstance(e, ChitFundAnalysisError):
                raise
            else:
                raise ChitFundAnalysisError(f"Analysis failed: {str(e)}")

    def format_results(self, result: ChitFundAnalysisResult) -> dict:
        """
        Format analysis results for display.
        
        Args:
            result: ChitFundAnalysisResult instance
            
        Returns:
            Dictionary with formatted results
        """
        return {
            "Total Installments": result.config.total_installments,
            "Current Installment": result.config.current_installment_number,
            "Full Chit Value": f"₹{result.config.full_chit_value:,.2f}",
            "Bid Amount": f"₹{result.config.bid_amount:,.2f}",
            "Prize Amount": f"₹{result.prize_amount:,.2f}",
            "Annual IRR": f"{result.annual_irr:.2%}",
            "Period IRR": f"{result.period_irr:.4%}",
            "Frequency per Year": result.config.chit_frequency_per_year,
            "Winner Installment": f"₹{result.config.get_winner_installment_amount():,.2f}"
        }