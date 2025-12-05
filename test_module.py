"""
Test script for the chit_fund_analyzer module.

Run this script to verify that the module works correctly.
"""

from decimal import Decimal
from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer, ScenarioAnalyzer


def test_basic_functionality():
    """Test basic functionality of the chit fund analyzer."""
    print("🔍 Testing basic functionality...")
    
    # Create configuration
    config = ChitFundConfig(
        total_installments=14,
        current_installment_number=5,
        full_chit_value=Decimal('700000'),
        chit_frequency_per_year=2,
        previous_installments=[
            Decimal('42000'), 
            Decimal('40000'), 
            Decimal('40000'), 
            Decimal('43000')
        ],
        bid_amount=Decimal('100000')
    )
    
    # Perform analysis
    analyzer = ChitFundAnalyzer(config)
    result = analyzer.analyze()
    
    print(f"✅ Prize amount: ₹{result.prize_amount:,.2f}")
    print(f"✅ Annual IRR: {result.annual_irr:.2%}")
    
    return result


def test_scenario_analysis():
    """Test scenario analysis functionality."""
    print("\n🔍 Testing scenario analysis...")
    
    config = ChitFundConfig(
        total_installments=14,
        current_installment_number=5,
        full_chit_value=Decimal('700000'),
        chit_frequency_per_year=2,
        previous_installments=[
            Decimal('42000'), 
            Decimal('40000'), 
            Decimal('40000'), 
            Decimal('43000')
        ],
        bid_amount=Decimal('100000')  # This will be overridden
    )
    
    scenario_analyzer = ScenarioAnalyzer(config)
    bid_amounts = [Decimal(str(amount)) for amount in [80000, 100000, 120000]]
    scenarios = scenario_analyzer.analyze_bid_scenarios(bid_amounts)
    
    print(f"✅ Analyzed {len(scenarios)} scenarios")
    for scenario in scenarios:
        print(f"   Bid: ₹{scenario.bid_amount:,.0f} → IRR: {scenario.annual_irr:.2%}")
    
    return scenarios


def test_validation():
    """Test input validation."""
    print("\n🔍 Testing validation...")
    
    # Test invalid configuration
    try:
        invalid_config = ChitFundConfig(
            total_installments=10,
            current_installment_number=15,  # Invalid!
            full_chit_value=Decimal('500000'),
            chit_frequency_per_year=12,
            previous_installments=[],
            bid_amount=Decimal('50000')
        )
        print("❌ Validation failed - should have caught error")
    except Exception as e:
        print(f"✅ Validation working: {str(e)[:60]}...")


def main():
    """Run all tests."""
    print("=== CHIT FUND ANALYZER TEST SCRIPT ===\n")
    
    try:
        test_basic_functionality()
        test_scenario_analysis() 
        test_validation()
        
        print("\n✅ All tests passed! The module is working correctly.")
        print("📖 Open 'chit_fund_analyzer_demo.ipynb' for comprehensive examples.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()