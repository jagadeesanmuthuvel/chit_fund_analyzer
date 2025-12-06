"""
Chit Fund Analyzer - A Python package for analyzing chit fund investments and calculating IRR.

This package provides tools for:
- Calculating chit fund investment returns
- Performing scenario analysis for different bid amounts
- Computing Internal Rate of Return (IRR) for chit fund investments
- Comparative analysis across multiple investment strategies

Main classes:
    ChitFundConfig: Configuration and validation for chit fund parameters
    ChitFundAnalyzer: Main analyzer class for calculations
    ScenarioAnalyzer: Tool for performing scenario analysis
    ComparativeAnalyzer: Tool for 3-way comparative analysis
"""

from .models import (
    ChitFundConfig, 
    BidScenario, 
    ComparisonScenario, 
    ThreeWayComparisonResult
)
from .analyzer import ChitFundAnalyzer
from .scenario import ScenarioAnalyzer
from .comparative import ComparativeAnalyzer
from .utils import (
    calculate_varying_installments,
    calculate_sip_future_value,
    calculate_lump_sum_future_value
)

__version__ = "0.1.0"
__all__ = [
    "ChitFundConfig", 
    "BidScenario", 
    "ComparisonScenario",
    "ThreeWayComparisonResult",
    "ChitFundAnalyzer", 
    "ScenarioAnalyzer",
    "ComparativeAnalyzer",
    "calculate_varying_installments",
    "calculate_sip_future_value",
    "calculate_lump_sum_future_value"
]