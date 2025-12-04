"""
Unit tests for Chit Fund Calculator module.

Run with: pytest test_chit_fund_calculator.py
"""

import pytest
import pandas as pd
from chit_fund_calculator import (
    ChitFundConfig,
    ChitFundCalculator,
    ChitFundResult,
    ScenarioAnalyzer,
    ReportGenerator,
    ChitFrequency
)


class TestChitFundConfig:
    """Test ChitFundConfig validation and initialization."""
    
    def test_valid_config(self):
        """Test creating valid configuration."""
        config = ChitFundConfig(
            total_installments=14,
            current_installment_number=4,
            full_chit_value=700000,
            chit_frequency_per_year=2,
            previous_installments=[42000, 40000, 43000],
            winner_installment_amount=50000
        )
        assert config.total_installments == 14
        assert config.full_chit_value == 700000
    
    def test_invalid_total_installments(self):
        """Test validation of negative installments."""
        with pytest.raises(ValueError, match="Total installments must be positive"):
            ChitFundConfig(
                total_installments=-5,
                current_installment_number=1,
                full_chit_value=700000,
                chit_frequency_per_year=2,
                previous_installments=[],
                winner_installment_amount=50000
            )
    
    def test_invalid_current_installment(self):
        """Test validation of current installment number."""
        with pytest.raises(ValueError, match="Current installment cannot exceed"):
            ChitFundConfig(
                total_installments=10,
                current_installment_number=15,
                full_chit_value=700000,
                chit_frequency_per_year=2,
                previous_installments=[50000] * 14,
                winner_installment_amount=50000
            )
    
    def test_invalid_chit_value(self):
        """Test validation of chit value."""
        with pytest.raises(ValueError, match="Chit value must be positive"):
            ChitFundConfig(
                total_installments=10,
                current_installment_number=4,
                full_chit_value=-100000,
                chit_frequency_per_year=2,
                previous_installments=[50000, 50000, 50000],
                winner_installment_amount=50000
            )
    
    def test_invalid_frequency(self):
        """Test validation of frequency."""
        with pytest.raises(ValueError, match="Invalid frequency"):
            ChitFundConfig(
                total_installments=10,
                current_installment_number=4,
                full_chit_value=700000,
                chit_frequency_per_year=5,  # Invalid
                previous_installments=[50000, 50000, 50000],
                winner_installment_amount=50000
            )
    
    def test_invalid_previous_installments_count(self):
        """Test validation of previous installments count."""
        with pytest.raises(ValueError, match="Expected .* previous installments"):
            ChitFundConfig(
                total_installments=10,
                current_installment_number=4,
                full_chit_value=700000,
                chit_frequency_per_year=2,
                previous_installments=[50000, 50000],  # Should be 3
                winner_installment_amount=50000
            )


class TestChitFundCalculator:
    """Test ChitFundCalculator methods."""
    
    @pytest.fixture
    def calculator(self):
        """Fixture providing calculator instance."""
        return ChitFundCalculator()
    
    @pytest.fixture
    def sample_config(self):
        """Fixture providing sample configuration."""
        return ChitFundConfig(
            total_installments=14,
            current_installment_number=4,
            full_chit_value=700000,
            chit_frequency_per_year=2,
            previous_installments=[42000, 40000, 43000],
            winner_installment_amount=50000
        )
    
    def test_calculate_prize_amount(self, calculator):
        """Test prize amount calculation."""
        prize = calculator.calculate_prize_amount(700000, 100000)
        assert prize == 600000
    
    def test_calculate_prize_amount_negative_bid(self, calculator):
        """Test negative bid amount."""
        with pytest.raises(ValueError, match="Bid amount cannot be negative"):
            calculator.calculate_prize_amount(700000, -50000)
    
    def test_calculate_prize_amount_bid_too_high(self, calculator):
        """Test bid amount exceeding chit value."""
        with pytest.raises(ValueError, match="Bid amount must be less than"):
            calculator.calculate_prize_amount(700000, 750000)
    
    def test_create_cashflows(self, calculator):
        """Test cashflow creation."""
        cashflows = calculator.create_cashflows(
            previous_installments=[42000, 40000, 43000],
            prize_amount=600000,
            winner_installment_amount=50000,
            current_installment_number=4,
            total_installments=14
        )
        
        # Check structure
        assert len(cashflows) == 3 + 1 + (14 - 4)  # previous + prize + future
        assert cashflows[0] == -42000  # First previous (negative)
        assert cashflows[3] == 600000  # Prize (positive)
        assert cashflows[4] == -50000  # First future (negative)
    
    def test_analyze_single_bid(self, calculator, sample_config):
        """Test single bid analysis."""
        result = calculator.analyze_single_bid(sample_config, 100000)
        
        assert isinstance(result, ChitFundResult)
        assert result.bid_amount == 100000
        assert result.prize_amount == 600000
        assert result.total_repayment > 0
        assert result.annual_irr is not None


class TestScenarioAnalyzer:
    """Test ScenarioAnalyzer methods."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture providing analyzer instance."""
        return ScenarioAnalyzer()
    
    @pytest.fixture
    def sample_config(self):
        """Fixture providing sample configuration."""
        return ChitFundConfig(
            total_installments=14,
            current_installment_number=4,
            full_chit_value=700000,
            chit_frequency_per_year=2,
            previous_installments=[42000, 40000, 43000],
            winner_installment_amount=50000
        )
    
    def test_analyze_scenarios_with_range(self, analyzer, sample_config):
        """Test scenario analysis with bid range."""
        df = analyzer.analyze_scenarios(
            config=sample_config,
            bid_range=(50000, 100000),
            bid_step=10000
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6  # 50k to 100k in 10k steps
        assert 'Bid Amount' in df.columns
        assert 'Annual IRR (%)' in df.columns
    
    def test_analyze_scenarios_with_list(self, analyzer, sample_config):
        """Test scenario analysis with specific bid list."""
        bid_amounts = [50000, 75000, 100000]
        df = analyzer.analyze_scenarios(
            config=sample_config,
            bid_amounts=bid_amounts
        )
        
        assert len(df) == 3
        assert df['Bid Amount'].tolist() == bid_amounts
    
    def test_find_optimal_bid(self, analyzer, sample_config):
        """Test finding optimal bid."""
        optimal = analyzer.find_optimal_bid(
            config=sample_config,
            bid_range=(50000, 150000),
            bid_step=10000
        )
        
        assert isinstance(optimal, dict)
        assert 'bid_amount' in optimal
        assert 'annual_irr' in optimal
        assert 'prize_received' in optimal
        assert optimal['bid_amount'] >= 50000
        assert optimal['bid_amount'] <= 150000


class TestReportGenerator:
    """Test ReportGenerator methods."""
    
    @pytest.fixture
    def sample_dataframe(self):
        """Fixture providing sample DataFrame."""
        return pd.DataFrame({
            'Bid Amount': [50000, 100000, 150000],
            'Prize Received': [650000, 600000, 550000],
            'Annual IRR (%)': [15.5, 12.3, 10.1],
            'Net Interest Cost': [50000, 45000, 40000]
        })
    
    @pytest.fixture
    def sample_optimal(self):
        """Fixture providing sample optimal result."""
        return {
            'bid_amount': 100000,
            'prize_received': 600000,
            'annual_irr': 12.3,
            'net_interest_cost': 45000,
            'total_repayment': 645000,
            'effective_interest': 7.5
        }
    
    def test_print_scenario_analysis(self, sample_dataframe, capsys):
        """Test scenario analysis printing."""
        ReportGenerator.print_scenario_analysis(sample_dataframe)
        captured = capsys.readouterr()
        assert "BID AMOUNT SCENARIO ANALYSIS" in captured.out
        assert "50000" in captured.out
    
    def test_print_optimal_strategy(self, sample_optimal, capsys):
        """Test optimal strategy printing."""
        ReportGenerator.print_optimal_strategy(sample_optimal)
        captured = capsys.readouterr()
        assert "OPTIMAL BID STRATEGY" in captured.out
        assert "100000" in captured.out
        assert "12.3" in captured.out
    
    def test_export_to_csv(self, sample_dataframe, tmp_path):
        """Test CSV export."""
        csv_file = tmp_path / "test_export.csv"
        ReportGenerator.export_to_csv(sample_dataframe, str(csv_file))
        
        assert csv_file.exists()
        
        # Read back and verify
        df_read = pd.read_csv(csv_file)
        assert len(df_read) == 3
        assert 'Bid Amount' in df_read.columns


class TestChitFundResult:
    """Test ChitFundResult dataclass."""
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ChitFundResult(
            bid_amount=100000,
            prize_amount=600000,
            total_repayment=645000,
            net_interest_cost=45000,
            annual_irr=0.123,
            effective_interest_rate=0.075,
            cashflows=[-50000, -50000, 600000, -50000]
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['Bid Amount'] == 100000
        assert result_dict['Prize Received'] == 600000
        assert result_dict['Annual IRR (%)'] == 12.3
        assert result_dict['Effective Interest (%)'] == 7.5


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow."""
        # 1. Create configuration
        config = ChitFundConfig(
            total_installments=14,
            current_installment_number=4,
            full_chit_value=700000,
            chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
            previous_installments=[42000, 40000, 43000],
            winner_installment_amount=50000
        )
        
        # 2. Analyze scenarios
        analyzer = ScenarioAnalyzer()
        scenarios = analyzer.analyze_scenarios(
            config=config,
            bid_range=(50000, 150000),
            bid_step=25000
        )
        
        # 3. Find optimal
        optimal = analyzer.find_optimal_bid(
            config=config,
            bid_range=(50000, 150000),
            bid_step=25000
        )
        
        # Verify results
        assert len(scenarios) == 5  # 50k, 75k, 100k, 125k, 150k
        assert optimal['bid_amount'] in [50000, 75000, 100000, 125000, 150000]
        assert optimal['annual_irr'] > 0
    
    def test_different_frequencies(self):
        """Test with different payment frequencies."""
        frequencies = [
            ChitFrequency.MONTHLY,
            ChitFrequency.QUARTERLY,
            ChitFrequency.SEMI_ANNUAL,
            ChitFrequency.ANNUAL
        ]
        
        calculator = ChitFundCalculator()
        
        for freq in frequencies:
            config = ChitFundConfig(
                total_installments=12,
                current_installment_number=4,
                full_chit_value=600000,
                chit_frequency_per_year=freq.value,
                previous_installments=[50000, 50000, 50000],
                winner_installment_amount=50000
            )
            
            result = calculator.analyze_single_bid(config, 100000)
            assert result.annual_irr is not None
            assert result.prize_amount == 500000
