"""
Chit Fund Analyzer - A Python package for analyzing chit fund investments and calculating IRR.

This package provides tools for:
- Calculating chit fund investment returns
- Performing scenario analysis for different bid amounts
- Computing Internal Rate of Return (IRR) for chit fund investments

Main classes:
    ChitFundConfig: Configuration and validation for chit fund parameters
    ChitFundAnalyzer: Main analyzer class for calculations
    ScenarioAnalyzer: Tool for performing scenario analysis
"""

from .models import ChitFundConfig, BidScenario
from .analyzer import ChitFundAnalyzer
from .scenario import ScenarioAnalyzer

__version__ = "0.1.0"
__all__ = ["ChitFundConfig", "BidScenario", "ChitFundAnalyzer", "ScenarioAnalyzer"]