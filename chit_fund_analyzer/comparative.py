"""
Comparative analysis functionality for chit fund investments.

This module provides tools for comparing three investment scenarios:
1. Early win with lump sum investment
2. Late win with varying installment amounts
3. SIP (Systematic Investment Plan) alternative

Each scenario is analyzed with proper IRR calculations and absolute final values.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
import numpy as np
import numpy_financial as npf

from .models import (
    ChitFundConfig, 
    ComparisonScenario, 
    ThreeWayComparisonResult
)
from .analyzer import ChitFundAnalyzer
from .utils import (
    calculate_varying_installments,
    calculate_sip_future_value,
    calculate_lump_sum_future_value
)
from .exceptions import ChitFundAnalysisError


class ComparativeAnalyzer:
    """
    Analyzer for comparing three distinct investment scenarios.
    
    This class provides comprehensive comparison between:
    - Winning chit early and investing prize as lump sum
    - Winning chit late with varying installment amounts
    - Pure SIP investment alternative
    """

    def __init__(self, chit_config: Dict[str, Any]):
        """
        Initialize comparative analyzer.
        
        Args:
            chit_config: Dictionary containing chit fund configuration
                Required keys: total_installments, full_chit_value, 
                              chit_frequency_per_year, current_installment
        """
        self.total_installments = chit_config['total_installments']
        self.full_chit_value = Decimal(str(chit_config['full_chit_value']))
        self.frequency_per_year = chit_config['chit_frequency_per_year']
        self.current_installment = chit_config.get('current_installment', 1)
        self.chit_name = chit_config.get('name', 'Chit Fund')
        
        # Calculate period parameters
        self.months_per_period = 12 / self.frequency_per_year
        self.base_installment = self.full_chit_value / self.total_installments

    def compare_three_scenarios(
        self,
        previous_amounts: List[Decimal],
        # Scenario 1 params
        win_installment: int,
        win_bid_amount: float,
        lumpsum_rate: float,
        # Scenario 2 params
        late_min_installment: float,
        late_max_installment: float,
        # Scenario 3 params
        sip_rate: float
    ) -> ThreeWayComparisonResult:
        """
        Run comprehensive 3-way comparison analysis.
        
        Args:
            previous_amounts: List of amounts paid in previous installments
            win_installment: Installment number to win at (Scenario 1)
            win_bid_amount: Bid amount when winning (Scenario 1)
            lumpsum_rate: Annual return rate for lump sum investment (Scenario 1)
            late_min_installment: Minimum installment amount (Scenario 2)
            late_max_installment: Maximum installment amount (Scenario 2)
            sip_rate: Annual return rate for SIP investment (Scenario 3)
            
        Returns:
            ThreeWayComparisonResult with all three scenarios analyzed
            
        Raises:
            ChitFundAnalysisError: If comparison analysis fails
        """
        try:
            # Analyze each scenario
            scenario1 = self.analyze_early_win_scenario(
                previous_amounts=previous_amounts,
                win_installment=win_installment,
                bid_amount=win_bid_amount,
                lumpsum_rate=lumpsum_rate
            )
            
            scenario2 = self.analyze_late_win_scenario(
                previous_amounts=previous_amounts,
                min_installment=late_min_installment,
                max_installment=late_max_installment
            )
            
            scenario3 = self.analyze_sip_scenario(
                previous_amounts=previous_amounts,
                min_installment=late_min_installment,
                max_installment=late_max_installment,
                sip_rate=sip_rate
            )
            
            # Determine best scenario
            scenarios_dict = {
                'Early Win + Lump Sum': scenario1.final_absolute_value,
                'Late Win': scenario2.final_absolute_value,
                'SIP Investment': scenario3.final_absolute_value
            }
            
            best_scenario_name = max(scenarios_dict, key=scenarios_dict.get)
            sorted_values = sorted(scenarios_dict.values(), reverse=True)
            advantage_amount = sorted_values[0] - sorted_values[1] if len(sorted_values) > 1 else Decimal('0')
            
            return ThreeWayComparisonResult(
                scenario1=scenario1,
                scenario2=scenario2,
                scenario3=scenario3,
                chit_name=self.chit_name,
                total_installments=self.total_installments,
                chit_value=self.full_chit_value,
                frequency_per_year=self.frequency_per_year,
                best_scenario_name=best_scenario_name,
                advantage_amount=advantage_amount
            )
            
        except Exception as e:
            raise ChitFundAnalysisError(f"Comparative analysis failed: {str(e)}")

    def analyze_early_win_scenario(
        self,
        previous_amounts: List[Decimal],
        win_installment: int,
        bid_amount: float,
        lumpsum_rate: float
    ) -> ComparisonScenario:
        """
        Analyze Scenario 1: Win early and invest prize as lump sum.
        
        Strategy:
        - Win at specified installment with given bid
        - Receive prize = full_chit_value - bid - base_installment
        - Invest (prize - base_installment) as lump sum
        - Pay base_installment for remaining periods
        - Final value = lump sum maturity value
        
        Args:
            previous_amounts: Amounts paid before analysis
            win_installment: Installment number to win at
            bid_amount: Bid amount when winning
            lumpsum_rate: Annual return rate for lump sum investment
            
        Returns:
            ComparisonScenario with analysis results
        """
        # Build previous installments up to win point
        win_previous = []
        for i in range(win_installment - 1):
            if i < len(previous_amounts):
                win_previous.append(previous_amounts[i])
            else:
                # Estimate future installments as base amount
                win_previous.append(self.base_installment)
        
        # Analyze chit fund to get prize amount
        config = ChitFundConfig(
            total_installments=self.total_installments,
            current_installment_number=win_installment,
            full_chit_value=self.full_chit_value,
            chit_frequency_per_year=self.frequency_per_year,
            previous_installments=win_previous,
            bid_amount=Decimal(str(bid_amount))
        )
        
        analyzer = ChitFundAnalyzer(config)
        result = analyzer.analyze()
        
        prize_amount = result.prize_amount
        winner_installment = config.get_winner_installment_amount()
        
        # Calculate lump sum investment
        remaining_periods = self.total_installments - win_installment
        lumpsum_investment = prize_amount  # Invest full prize
        
        lumpsum_final_value = calculate_lump_sum_future_value(
            principal=lumpsum_investment,
            annual_rate=lumpsum_rate,
            periods=remaining_periods,
            frequency_per_year=self.frequency_per_year
        )
        
        # Build cashflows for IRR calculation
        # Past payments + Prize inflow + Lump sum outflow + Future installments + Final lump sum inflow
        cashflows = []
        
        # Past installments (outflows)
        for amt in win_previous:
            cashflows.append(-amt)
        
        # At win period: receive prize, invest lump sum, pay winner installment
        # Net cashflow = +prize - lumpsum_investment - winner_installment
        net_at_win = prize_amount - lumpsum_investment - winner_installment
        cashflows.append(net_at_win)
        
        # Future installments (outflows) - pay base installment, not winner installment
        for _ in range(remaining_periods):
            cashflows.append(-self.base_installment)
        
        # Final inflow: lump sum maturity
        cashflows[-1] = cashflows[-1] + lumpsum_final_value
        
        # Calculate IRR
        annual_irr = self._calculate_annual_irr(cashflows)
        
        # Calculate totals
        total_spent = sum(float(amt) for amt in win_previous)
        total_spent += float(winner_installment)  # Winner installment at win period
        total_spent += float(self.base_installment) * remaining_periods  # Base installments after winning
        
        return ComparisonScenario(
            scenario_name="Early Win + Lump Sum",
            cashflows=[Decimal(str(cf)) for cf in cashflows],
            annual_irr=annual_irr,
            final_absolute_value=lumpsum_final_value,
            total_invested=Decimal(str(total_spent)),
            net_gain=lumpsum_final_value - Decimal(str(total_spent)),
            details={
                'win_installment': win_installment,
                'bid_amount': float(bid_amount),
                'prize_amount': float(prize_amount),
                'winner_installment': float(winner_installment),
                'lumpsum_investment': float(lumpsum_investment),
                'lumpsum_rate': lumpsum_rate,
                'lumpsum_final_value': float(lumpsum_final_value),
                'remaining_periods': remaining_periods
            }
        )

    def analyze_late_win_scenario(
        self,
        previous_amounts: List[Decimal],
        min_installment: float,
        max_installment: float
    ) -> ComparisonScenario:
        """
        Analyze Scenario 2: Don't win until last installment with varying amounts.
        
        Strategy:
        - Don't win until last installment
        - Pay varying amounts between min and max (simulating bid variations)
        - Win at last installment with minimal bid (₹1000)
        - Receive prize = full_chit_value - base_installment
        - Final value = prize amount
        
        Args:
            previous_amounts: Amounts paid before analysis
            min_installment: Minimum expected installment amount
            max_installment: Maximum expected installment amount
            
        Returns:
            ComparisonScenario with analysis results
        """
        # Generate varying installment amounts
        varying_installments = calculate_varying_installments(
            full_chit_value=self.full_chit_value,
            total_installments=self.total_installments,
            min_installment=Decimal(str(min_installment)),
            max_installment=Decimal(str(max_installment))
        )
        
        # Build all installments (N-1 varying amounts)
        all_installments = []
        for i in range(self.total_installments - 1):
            if i < len(previous_amounts):
                all_installments.append(previous_amounts[i])
            else:
                idx = i - len(previous_amounts)
                if idx < len(varying_installments):
                    all_installments.append(varying_installments[idx])
                else:
                    # Fallback to average
                    avg = (Decimal(str(min_installment)) + Decimal(str(max_installment))) / 2
                    all_installments.append(avg)
        
        # Win at last installment with minimal bid
        minimal_bid = Decimal('1000')
        
        config = ChitFundConfig(
            total_installments=self.total_installments,
            current_installment_number=self.total_installments,
            full_chit_value=self.full_chit_value,
            chit_frequency_per_year=self.frequency_per_year,
            previous_installments=all_installments,
            bid_amount=minimal_bid
        )
        
        analyzer = ChitFundAnalyzer(config)
        result = analyzer.analyze()
        
        prize_amount = result.prize_amount
        
        # Build cashflows: all installments as outflows, final prize as inflow
        cashflows = [-amt for amt in all_installments]
        cashflows.append(prize_amount)
        
        # Calculate IRR
        annual_irr = self._calculate_annual_irr(cashflows)
        
        total_spent = sum(float(amt) for amt in all_installments)
        
        return ComparisonScenario(
            scenario_name="Late Win (Last Installment)",
            cashflows=[Decimal(str(cf)) for cf in cashflows],
            annual_irr=annual_irr,
            final_absolute_value=prize_amount,
            total_invested=Decimal(str(total_spent)),
            net_gain=prize_amount - Decimal(str(total_spent)),
            details={
                'min_installment': min_installment,
                'max_installment': max_installment,
                'avg_installment': float((Decimal(str(min_installment)) + Decimal(str(max_installment))) / 2),
                'total_installments_paid': len(all_installments),
                'bid_amount': float(minimal_bid),
                'prize_amount': float(prize_amount)
            }
        )

    def analyze_sip_scenario(
        self,
        previous_amounts: List[Decimal],
        min_installment: float,
        max_installment: float,
        sip_rate: float
    ) -> ComparisonScenario:
        """
        Analyze Scenario 3: SIP investment with same frequency and amounts.
        
        Strategy:
        - Invest in SIP with same frequency as chit
        - Use same varying amounts as Scenario 2
        - Each installment compounds independently
        - Final value = total SIP maturity value
        
        Args:
            previous_amounts: Amounts paid before analysis (for consistency)
            min_installment: Minimum SIP installment amount
            max_installment: Maximum SIP installment amount
            sip_rate: Annual return rate for SIP
            
        Returns:
            ComparisonScenario with analysis results
        """
        # Generate varying installment amounts (same as Scenario 2)
        varying_installments = calculate_varying_installments(
            full_chit_value=self.full_chit_value,
            total_installments=self.total_installments,
            min_installment=Decimal(str(min_installment)),
            max_installment=Decimal(str(max_installment))
        )
        
        # Build all SIP installments
        all_sip_installments = []
        for i in range(self.total_installments):
            if i < len(previous_amounts):
                # Use actual amounts if available (for past periods)
                all_sip_installments.append(previous_amounts[i])
            else:
                idx = i - len(previous_amounts)
                if idx < len(varying_installments):
                    all_sip_installments.append(varying_installments[idx])
                else:
                    avg = (Decimal(str(min_installment)) + Decimal(str(max_installment))) / 2
                    all_sip_installments.append(avg)
        
        # Calculate SIP maturity value
        sip_maturity = calculate_sip_future_value(
            installments=all_sip_installments,
            annual_rate=sip_rate,
            frequency_per_year=self.frequency_per_year
        )
        
        # Build cashflows: all installments as outflows, final maturity as inflow
        cashflows = [-amt for amt in all_sip_installments]
        cashflows.append(sip_maturity)
        
        # Calculate IRR
        annual_irr = self._calculate_annual_irr(cashflows)
        
        total_invested = sum(float(amt) for amt in all_sip_installments)
        
        return ComparisonScenario(
            scenario_name="SIP Investment",
            cashflows=[Decimal(str(cf)) for cf in cashflows],
            annual_irr=annual_irr,
            final_absolute_value=sip_maturity,
            total_invested=Decimal(str(total_invested)),
            net_gain=sip_maturity - Decimal(str(total_invested)),
            details={
                'sip_min_amount': min_installment,
                'sip_max_amount': max_installment,
                'sip_rate': sip_rate,
                'total_sips': len(all_sip_installments),
                'sip_maturity': float(sip_maturity)
            }
        )

    def _calculate_annual_irr(self, cashflows: List[Any]) -> float:
        """
        Calculate annual IRR from cashflows.
        
        Args:
            cashflows: List of cashflows (Decimal or float)
            
        Returns:
            Annual IRR as float
        """
        try:
            cf_array = np.array([float(cf) for cf in cashflows])
            period_irr = npf.irr(cf_array)
            
            if period_irr is None or np.isnan(period_irr):
                return 0.0
            
            # Convert period IRR to annual IRR
            annual_irr = ((1 + period_irr) ** self.frequency_per_year) - 1
            return float(annual_irr)
            
        except Exception:
            return 0.0
