"""
Scenario analysis functionality for chit fund investments.

This module provides tools for analyzing multiple bid scenarios
and comparing their returns and outcomes.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
import pandas as pd

from .models import ChitFundConfig, BidScenario
from .analyzer import ChitFundAnalyzer
from .exceptions import ChitFundAnalysisError


class ScenarioAnalyzer:
    """
    Analyzer for comparing multiple bid scenarios.
    
    This class helps evaluate different bid amounts and their impact
    on returns, allowing for informed decision-making in chit fund bidding.
    """

    def __init__(self, base_config: ChitFundConfig):
        """
        Initialize scenario analyzer with base configuration.
        
        Args:
            base_config: Base ChitFundConfig (bid_amount will be overridden for scenarios)
        """
        self.base_config = base_config

    def analyze_bid_scenarios(
        self, 
        bid_amounts: List[Decimal],
        winner_installment_amount: Optional[Decimal] = None
    ) -> List[BidScenario]:
        """
        Analyze multiple bid scenarios and return results.
        
        Args:
            bid_amounts: List of bid amounts to analyze
            winner_installment_amount: Optional override for winner installment
            
        Returns:
            List of BidScenario results
            
        Raises:
            ChitFundAnalysisError: If scenario analysis fails
        """
        scenarios = []
        
        for bid_amount in bid_amounts:
            try:
                # Create config for this scenario
                scenario_config = self._create_scenario_config(
                    bid_amount, winner_installment_amount
                )
                
                # Analyze this scenario
                analyzer = ChitFundAnalyzer(scenario_config)
                result = analyzer.analyze()
                
                # Create scenario result
                scenario = BidScenario(
                    bid_amount=bid_amount,
                    prize_amount=result.prize_amount,
                    annual_irr=result.annual_irr,
                    monthly_irr=result.period_irr if self.base_config.chit_frequency_per_year == 12 else None
                )
                
                scenarios.append(scenario)
                
            except Exception as e:
                raise ChitFundAnalysisError(
                    f"Scenario analysis failed for bid amount {bid_amount}: {str(e)}"
                )
        
        return scenarios

    def _create_scenario_config(
        self, 
        bid_amount: Decimal, 
        winner_installment_amount: Optional[Decimal]
    ) -> ChitFundConfig:
        """
        Create a configuration for a specific scenario.
        
        Args:
            bid_amount: Bid amount for this scenario
            winner_installment_amount: Optional winner installment override
            
        Returns:
            ChitFundConfig for the scenario
        """
        config_dict = self.base_config.dict()
        config_dict['bid_amount'] = bid_amount
        
        if winner_installment_amount is not None:
            config_dict['winner_installment_amount'] = winner_installment_amount
        
        return ChitFundConfig(**config_dict)

    def create_scenario_dataframe(
        self, 
        scenarios: List[BidScenario],
        format_currency: bool = True
    ) -> pd.DataFrame:
        """
        Create a pandas DataFrame from scenario results.
        
        Args:
            scenarios: List of BidScenario results
            format_currency: Whether to format currency columns
            
        Returns:
            DataFrame with scenario analysis results
        """
        data = []
        
        for scenario in scenarios:
            row = {
                'Bid Amount': scenario.bid_amount,
                'Prize Amount': scenario.prize_amount,
                'Annual IRR': scenario.annual_irr,
                'Annual IRR (%)': f"{scenario.annual_irr:.2%}"
            }
            
            if scenario.monthly_irr is not None:
                row['Monthly IRR'] = scenario.monthly_irr
                row['Monthly IRR (%)'] = f"{scenario.monthly_irr:.4%}"
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        if format_currency and not df.empty:
            # Format currency columns
            for col in ['Bid Amount', 'Prize Amount']:
                if col in df.columns:
                    df[f'{col} (Formatted)'] = df[col].apply(lambda x: f"₹{x:,.2f}")
        
        return df

    def find_optimal_bid(
        self, 
        bid_range: tuple,
        target_irr: Optional[float] = None,
        step_size: Decimal = Decimal('1000'),
        winner_installment_amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Find optimal bid amount based on criteria.
        
        Args:
            bid_range: Tuple of (min_bid, max_bid)
            target_irr: Target annual IRR to achieve
            step_size: Step size for bid amount increments
            winner_installment_amount: Optional winner installment override
            
        Returns:
            Dictionary with optimal bid analysis results
        """
        min_bid, max_bid = bid_range
        current_bid = Decimal(str(min_bid))
        bid_amounts = []
        
        # Generate bid amounts
        while current_bid <= max_bid:
            bid_amounts.append(current_bid)
            current_bid += step_size
        
        # Analyze scenarios
        scenarios = self.analyze_bid_scenarios(bid_amounts, winner_installment_amount)
        
        # Find optimal based on criteria
        if target_irr is not None:
            # Find bid closest to target IRR
            best_scenario = min(
                scenarios, 
                key=lambda s: abs(s.annual_irr - target_irr)
            )
            optimization_criterion = f"Closest to target IRR of {target_irr:.2%}"
        else:
            # Find highest IRR
            best_scenario = max(scenarios, key=lambda s: s.annual_irr)
            optimization_criterion = "Highest Annual IRR"
        
        return {
            'optimization_criterion': optimization_criterion,
            'optimal_bid_amount': best_scenario.bid_amount,
            'optimal_prize_amount': best_scenario.prize_amount,
            'optimal_annual_irr': best_scenario.annual_irr,
            'optimal_annual_irr_formatted': f"{best_scenario.annual_irr:.2%}",
            'total_scenarios_analyzed': len(scenarios),
            'bid_range_analyzed': f"₹{min_bid:,.0f} - ₹{max_bid:,.0f}",
            'all_scenarios': scenarios
        }

    def compare_frequencies(
        self, 
        bid_amount: Decimal,
        frequencies: List[int],
        winner_installment_amount: Optional[Decimal] = None
    ) -> pd.DataFrame:
        """
        Compare the same bid across different payment frequencies.
        
        Args:
            bid_amount: Fixed bid amount to analyze
            frequencies: List of payment frequencies per year to compare
            winner_installment_amount: Optional winner installment override
            
        Returns:
            DataFrame comparing different frequencies
        """
        comparison_data = []
        
        for freq in frequencies:
            # Create config with different frequency
            config_dict = self.base_config.dict()
            config_dict['bid_amount'] = bid_amount
            config_dict['chit_frequency_per_year'] = freq
            
            if winner_installment_amount is not None:
                config_dict['winner_installment_amount'] = winner_installment_amount
            
            scenario_config = ChitFundConfig(**config_dict)
            
            # Analyze
            analyzer = ChitFundAnalyzer(scenario_config)
            result = analyzer.analyze()
            
            comparison_data.append({
                'Frequency per Year': freq,
                'Period Type': 'Monthly' if freq == 12 else 'Quarterly' if freq == 4 else 'Half-Yearly' if freq == 2 else 'Custom',
                'Bid Amount': bid_amount,
                'Prize Amount': result.prize_amount,
                'Annual IRR': result.annual_irr,
                'Annual IRR (%)': f"{result.annual_irr:.2%}",
                'Period IRR': result.period_irr,
                'Period IRR (%)': f"{result.period_irr:.4%}"
            })
        
        return pd.DataFrame(comparison_data)