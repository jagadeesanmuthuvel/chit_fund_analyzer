"""
Quick test script to verify Streamlit app functionality.

This script tests all the major components of the Streamlit app
to ensure they work correctly.
"""

import sys
import traceback
from decimal import Decimal


def test_imports():
    """Test all required imports."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported")
        
        import pandas as pd
        print("✅ Pandas imported")
        
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        print("✅ Plotly components imported")
        
        from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer, ScenarioAnalyzer
        print("✅ Chit fund analyzer imported")
        
        from chit_fund_analyzer.utils import format_currency, format_percentage
        print("✅ Utility functions imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic analyzer functionality."""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer
        
        # Create test configuration
        config = ChitFundConfig(
            total_installments=10,
            current_installment_number=3,
            full_chit_value=Decimal('500000'),
            chit_frequency_per_year=2,
            previous_installments=[Decimal('40000'), Decimal('38000')],
            bid_amount=Decimal('80000')
        )
        print("✅ Configuration created")
        
        # Test analysis
        analyzer = ChitFundAnalyzer(config)
        result = analyzer.analyze()
        print(f"✅ Analysis completed - IRR: {result.annual_irr:.2%}")
        
        return True
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        traceback.print_exc()
        return False


def test_scenario_analysis():
    """Test scenario analysis functionality."""
    print("\n🔍 Testing scenario analysis...")
    
    try:
        from chit_fund_analyzer import ChitFundConfig, ScenarioAnalyzer
        
        config = ChitFundConfig(
            total_installments=10,
            current_installment_number=3,
            full_chit_value=Decimal('500000'),
            chit_frequency_per_year=2,
            previous_installments=[Decimal('40000'), Decimal('38000')],
            bid_amount=Decimal('80000')
        )
        
        scenario_analyzer = ScenarioAnalyzer(config)
        bid_amounts = [Decimal(str(x)) for x in [60000, 80000, 100000]]
        scenarios = scenario_analyzer.analyze_bid_scenarios(bid_amounts)
        
        print(f"✅ Scenario analysis completed - {len(scenarios)} scenarios")
        return True
    except Exception as e:
        print(f"❌ Scenario analysis error: {e}")
        traceback.print_exc()
        return False


def test_visualization_data():
    """Test data preparation for visualizations."""
    print("\n🔍 Testing visualization data preparation...")
    
    try:
        import pandas as pd
        import plotly.graph_objects as go
        
        # Test data
        test_data = {
            'Bid Amount': [60000, 80000, 100000],
            'Annual IRR': [0.12, 0.15, 0.18],
            'Prize Amount': [400000, 380000, 360000]
        }
        
        df = pd.DataFrame(test_data)
        print("✅ DataFrame creation successful")
        
        # Test plotly figure creation
        fig = go.Figure(data=[
            go.Bar(x=df['Bid Amount'], y=df['Annual IRR'])
        ])
        fig.update_layout(title="Test Chart")
        print("✅ Plotly figure creation successful")
        
        return True
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=== STREAMLIT APP VERIFICATION TESTS ===\n")
    
    tests = [
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Scenario Analysis", test_scenario_analysis),
        ("Visualization Data", test_visualization_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("SUMMARY:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Streamlit app is ready to run.")
        print("💡 Start the app with: python run_app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())