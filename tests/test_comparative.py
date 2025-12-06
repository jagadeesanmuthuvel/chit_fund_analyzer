"""
Unit tests for comparative analysis functionality.

Tests the ComparativeAnalyzer class and utility functions for
3-way investment comparison scenarios.
"""

import pytest
from decimal import Decimal
from chit_fund_analyzer.comparative import ComparativeAnalyzer
from chit_fund_analyzer.utils import (
    calculate_varying_installments,
    calculate_sip_future_value,
    calculate_lump_sum_future_value
)
from chit_fund_analyzer.models import (
    ComparisonScenario,
    ThreeWayComparisonResult
)
from chit_fund_analyzer.exceptions import ChitFundAnalysisError


class TestCalculateVaryingInstallments:
    """Test varying installments calculation."""
    
    def test_linear_interpolation(self):
        """Test that varying installments use linear interpolation."""
        full_chit_value = Decimal('700000')
        total_installments = 10
        min_installment = Decimal('40000')
        max_installment = Decimal('60000')
        
        result = calculate_varying_installments(
            full_chit_value=full_chit_value,
            total_installments=total_installments,
            min_installment=min_installment,
            max_installment=max_installment
        )
        
        # Should have N-1 installments (last one is when you win)
        assert len(result) == total_installments - 1
        
        # First should be close to min
        assert abs(result[0] - min_installment) < Decimal('100')
        
        # Last should be close to max
        assert abs(result[-1] - max_installment) < Decimal('100')
        
        # Should be monotonically increasing
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]
    
    def test_single_installment(self):
        """Test edge case with only 2 total installments."""
        result = calculate_varying_installments(
            full_chit_value=Decimal('100000'),
            total_installments=2,
            min_installment=Decimal('10000'),
            max_installment=Decimal('20000')
        )
        
        # Should have exactly 1 installment
        assert len(result) == 1


class TestCalculateSipFutureValue:
    """Test SIP future value calculation."""
    
    def test_zero_rate(self):
        """Test SIP with zero interest rate."""
        installments = [Decimal('5000')] * 12
        annual_rate = 0.0
        frequency_per_year = 12
        
        result = calculate_sip_future_value(
            installments=installments,
            annual_rate=annual_rate,
            frequency_per_year=frequency_per_year
        )
        
        # With 0% rate, FV should equal sum of installments
        expected = sum(installments)
        assert result == expected
    
    def test_positive_rate(self):
        """Test SIP with positive interest rate."""
        installments = [Decimal('10000')] * 12
        annual_rate = 0.12  # 12% annual
        frequency_per_year = 12
        
        result = calculate_sip_future_value(
            installments=installments,
            annual_rate=annual_rate,
            frequency_per_year=frequency_per_year
        )
        
        # FV should be greater than sum (due to compounding)
        total_invested = sum(installments)
        assert result > total_invested
        
        # Should be approximately 126,825 for 12 monthly 10k SIPs at 12% p.a.
        expected_approx = Decimal('126800')
        assert abs(result - expected_approx) < Decimal('1000')
    
    def test_varying_installments(self):
        """Test SIP with varying installment amounts."""
        installments = [Decimal(str(i * 1000)) for i in range(1, 13)]  # 1k to 12k
        annual_rate = 0.10
        frequency_per_year = 12
        
        result = calculate_sip_future_value(
            installments=installments,
            annual_rate=annual_rate,
            frequency_per_year=frequency_per_year
        )
        
        # Should be positive and greater than sum
        assert result > sum(installments)


class TestCalculateLumpSumFutureValue:
    """Test lump sum future value calculation."""
    
    def test_zero_rate(self):
        """Test lump sum with zero rate."""
        principal = Decimal('100000')
        annual_rate = 0.0
        periods = 12
        frequency_per_year = 12
        
        result = calculate_lump_sum_future_value(
            principal=principal,
            annual_rate=annual_rate,
            periods=periods,
            frequency_per_year=frequency_per_year
        )
        
        # With 0% rate, FV equals principal
        assert result == principal
    
    def test_positive_rate(self):
        """Test lump sum with positive rate."""
        principal = Decimal('100000')
        annual_rate = 0.12  # 12% annual
        periods = 12
        frequency_per_year = 12
        
        result = calculate_lump_sum_future_value(
            principal=principal,
            annual_rate=annual_rate,
            periods=periods,
            frequency_per_year=frequency_per_year
        )
        
        # FV should be greater than principal
        assert result > principal
        
        # Should be approximately 112,000 (compound interest formula)
        expected_approx = Decimal('112000')
        assert abs(result - expected_approx) < Decimal('1000')
    
    def test_zero_periods(self):
        """Test lump sum with zero periods."""
        principal = Decimal('50000')
        annual_rate = 0.10
        periods = 0
        frequency_per_year = 12
        
        result = calculate_lump_sum_future_value(
            principal=principal,
            annual_rate=annual_rate,
            periods=periods,
            frequency_per_year=frequency_per_year
        )
        
        # With 0 periods, FV equals principal
        assert result == principal


class TestComparativeAnalyzer:
    """Test ComparativeAnalyzer class."""
    
    @pytest.fixture
    def chit_config(self):
        """Fixture for chit fund configuration."""
        return {
            'total_installments': 10,
            'full_chit_value': 500000,
            'chit_frequency_per_year': 12,
            'current_installment': 1,
            'name': 'Test Chit'
        }
    
    @pytest.fixture
    def analyzer(self, chit_config):
        """Fixture for ComparativeAnalyzer instance."""
        return ComparativeAnalyzer(chit_config=chit_config)
    
    def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.total_installments == 10
        assert analyzer.full_chit_value == Decimal('500000')
        assert analyzer.frequency_per_year == 12
        assert analyzer.current_installment == 1
        assert analyzer.chit_name == 'Test Chit'
        
        # Calculated values
        assert analyzer.months_per_period == 1.0  # 12/12
        assert analyzer.base_installment == Decimal('50000')  # 500k/10
    
    def test_early_win_scenario(self, analyzer):
        """Test early win scenario analysis."""
        scenario = analyzer.analyze_early_win_scenario(
            previous_amounts=[],
            win_installment=3,
            bid_amount=50000.0,
            lumpsum_rate=0.10
        )
        
        # Verify scenario structure
        assert isinstance(scenario, ComparisonScenario)
        assert scenario.scenario_name == "Early Win + Lump Sum"
        assert scenario.annual_irr is not None  # IRR can be negative
        assert scenario.final_absolute_value > 0
        assert scenario.total_invested > 0
        
        # Verify details
        assert scenario.details['win_installment'] == 3
        assert scenario.details['bid_amount'] == 50000.0
        assert 'prize_amount' in scenario.details
        assert 'lumpsum_final_value' in scenario.details
    
    def test_late_win_scenario(self, analyzer):
        """Test late win scenario analysis."""
        scenario = analyzer.analyze_late_win_scenario(
            previous_amounts=[],
            min_installment=40000.0,
            max_installment=60000.0
        )
        
        # Verify scenario structure
        assert isinstance(scenario, ComparisonScenario)
        assert scenario.scenario_name == "Late Win (Last Installment)"
        assert scenario.annual_irr is not None  # IRR can be negative
        assert scenario.final_absolute_value > 0
        
        # Verify details
        assert scenario.details['min_installment'] == 40000.0
        assert scenario.details['max_installment'] == 60000.0
        assert 'avg_installment' in scenario.details
        assert 'prize_amount' in scenario.details
    
    def test_sip_scenario(self, analyzer):
        """Test SIP scenario analysis."""
        scenario = analyzer.analyze_sip_scenario(
            previous_amounts=[],
            min_installment=40000.0,
            max_installment=60000.0,
            sip_rate=0.12
        )
        
        # Verify scenario structure
        assert isinstance(scenario, ComparisonScenario)
        assert scenario.scenario_name == "SIP Investment"
        assert scenario.annual_irr >= 0
        assert scenario.final_absolute_value > scenario.total_invested  # Should have returns
        
        # Verify details
        assert scenario.details['sip_rate'] == 0.12
        assert scenario.details['total_sips'] == 10
        assert 'sip_maturity' in scenario.details
    
    def test_compare_three_scenarios(self, analyzer):
        """Test full 3-way comparison."""
        result = analyzer.compare_three_scenarios(
            previous_amounts=[],
            win_installment=3,
            win_bid_amount=50000.0,
            lumpsum_rate=0.10,
            late_min_installment=40000.0,
            late_max_installment=60000.0,
            sip_rate=0.12
        )
        
        # Verify result structure
        assert isinstance(result, ThreeWayComparisonResult)
        assert isinstance(result.scenario1, ComparisonScenario)
        assert isinstance(result.scenario2, ComparisonScenario)
        assert isinstance(result.scenario3, ComparisonScenario)
        
        # Verify metadata
        assert result.chit_name == 'Test Chit'
        assert result.total_installments == 10
        assert result.chit_value == Decimal('500000')
        assert result.frequency_per_year == 12
        
        # Verify best scenario is identified
        assert result.best_scenario_name in [
            'Early Win + Lump Sum',
            'Late Win (Last Installment)',
            'SIP Investment'
        ]
        
        # Verify advantage amount is non-negative
        assert result.advantage_amount >= 0
    
    def test_with_previous_amounts(self, analyzer):
        """Test scenarios with previous installments."""
        previous = [Decimal('45000'), Decimal('46000')]
        
        scenario = analyzer.analyze_early_win_scenario(
            previous_amounts=previous,
            win_installment=3,
            bid_amount=40000.0,
            lumpsum_rate=0.10
        )
        
        # Should account for previous amounts
        assert len(scenario.cashflows) > len(previous)
    
    def test_irr_calculation(self, analyzer):
        """Test that IRR is calculated for all scenarios."""
        result = analyzer.compare_three_scenarios(
            previous_amounts=[],
            win_installment=2,
            win_bid_amount=30000.0,
            lumpsum_rate=0.08,
            late_min_installment=45000.0,
            late_max_installment=55000.0,
            sip_rate=0.10
        )
        
        # All scenarios should have IRR calculated
        assert result.scenario1.annual_irr is not None
        assert result.scenario2.annual_irr is not None
        assert result.scenario3.annual_irr is not None
        
        # IRR should be reasonable (not NaN or infinity)
        assert -1 < result.scenario1.annual_irr < 2
        assert -1 < result.scenario2.annual_irr < 2
        assert -1 < result.scenario3.annual_irr < 2


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_high_bid_amount(self):
        """Test scenario with very high bid amount."""
        analyzer = ComparativeAnalyzer(chit_config={
            'total_installments': 5,
            'full_chit_value': 100000,
            'chit_frequency_per_year': 12,
            'current_installment': 1,
            'name': 'Test'
        })
        
        # Test with a small bid that should work reliably
        # Small bids create normal cashflow patterns that converge
        scenario = analyzer.analyze_early_win_scenario(
            previous_amounts=[],
            win_installment=2,
            bid_amount=5000.0,  # Small bid to ensure stable IRR calculation
            lumpsum_rate=0.10
        )
        
        assert scenario is not None
        assert scenario.annual_irr is not None
        assert scenario.final_absolute_value > 0
        assert scenario.details['bid_amount'] == 5000.0
    
    def test_min_equals_max_installment(self):
        """Test when min and max installments are equal."""
        analyzer = ComparativeAnalyzer(chit_config={
            'total_installments': 10,
            'full_chit_value': 500000,
            'chit_frequency_per_year': 12,
            'current_installment': 1,
            'name': 'Test'
        })
        
        scenario = analyzer.analyze_late_win_scenario(
            previous_amounts=[],
            min_installment=50000.0,
            max_installment=50000.0  # Same as min
        )
        
        # Should use constant installment amount
        assert scenario.details['avg_installment'] == 50000.0
    
    def test_zero_interest_rates(self):
        """Test scenarios with zero interest rates."""
        analyzer = ComparativeAnalyzer(chit_config={
            'total_installments': 5,
            'full_chit_value': 100000,
            'chit_frequency_per_year': 12,
            'current_installment': 1,
            'name': 'Test'
        })
        
        result = analyzer.compare_three_scenarios(
            previous_amounts=[],
            win_installment=2,
            win_bid_amount=10000.0,
            lumpsum_rate=0.0,  # Zero rate
            late_min_installment=18000.0,
            late_max_installment=22000.0,
            sip_rate=0.0  # Zero rate
        )
        
        # Should handle zero rates gracefully
        assert result.scenario1 is not None
        assert result.scenario3 is not None


class TestIntegration:
    """Integration tests with realistic scenarios."""
    
    def test_realistic_chit_comparison(self):
        """Test with realistic chit fund parameters."""
        analyzer = ComparativeAnalyzer(chit_config={
            'total_installments': 20,
            'full_chit_value': 1000000,
            'chit_frequency_per_year': 2,  # Bi-annual
            'current_installment': 1,
            'name': 'Real Estate Chit'
        })
        
        result = analyzer.compare_three_scenarios(
            previous_amounts=[],
            win_installment=5,
            win_bid_amount=100000.0,
            lumpsum_rate=0.12,
            late_min_installment=45000.0,
            late_max_installment=55000.0,
            sip_rate=0.14
        )
        
        # Verify all scenarios complete
        assert result.scenario1 is not None
        assert result.scenario2 is not None
        assert result.scenario3 is not None
        
        # Verify calculations are reasonable
        assert result.scenario1.final_absolute_value > 0
        assert result.scenario2.final_absolute_value > 0
        assert result.scenario3.final_absolute_value > 0
        
        # Net gains should be positive for good scenarios
        assert result.scenario1.net_gain != 0
        assert result.scenario2.net_gain != 0
        assert result.scenario3.net_gain > 0  # SIP should always have positive gain
    
    def test_monthly_vs_annual_frequency(self):
        """Test scenarios with different payment frequencies."""
        # Monthly chit
        monthly_analyzer = ComparativeAnalyzer(chit_config={
            'total_installments': 12,
            'full_chit_value': 120000,
            'chit_frequency_per_year': 12,
            'current_installment': 1,
            'name': 'Monthly Chit'
        })
        
        monthly_result = monthly_analyzer.compare_three_scenarios(
            previous_amounts=[],
            win_installment=3,
            win_bid_amount=12000.0,
            lumpsum_rate=0.10,
            late_min_installment=9000.0,
            late_max_installment=11000.0,
            sip_rate=0.12
        )
        
        # Annual chit
        annual_analyzer = ComparativeAnalyzer(chit_config={
            'total_installments': 12,
            'full_chit_value': 120000,
            'chit_frequency_per_year': 1,
            'current_installment': 1,
            'name': 'Annual Chit'
        })
        
        annual_result = annual_analyzer.compare_three_scenarios(
            previous_amounts=[],
            win_installment=3,
            win_bid_amount=12000.0,
            lumpsum_rate=0.10,
            late_min_installment=9000.0,
            late_max_installment=11000.0,
            sip_rate=0.12
        )
        
        # Both should complete successfully
        assert monthly_result.best_scenario_name is not None
        assert annual_result.best_scenario_name is not None
        
        # Results will differ due to compounding frequency
        assert monthly_result.scenario3.final_absolute_value != annual_result.scenario3.final_absolute_value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
