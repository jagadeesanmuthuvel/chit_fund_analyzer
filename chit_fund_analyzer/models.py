"""                                                                                                                                                                  
Data models and validation schemas for chit fund analysis.

This module contains Pydantic models for validating and structuring
chit fund data with proper type hints and constraints.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator
class ChitFundConfig(BaseModel):
    """
    Configuration model for chit fund parameters with validation.
    
    Attributes:
        total_installments: Total number of installments in the chit fund
        current_installment_number: Current installment number (1-based)
        full_chit_value: Total value of the chit fund
        chit_frequency_per_year: Number of installments per year
        previous_installments: List of previously paid installment amounts
        bid_amount: Amount bid for winning the chit
        winner_installment_amount: Optional custom installment amount for winner
    """
    
    total_installments: int = Field(..., gt=0, description="Total number of installments")
    current_installment_number: int = Field(..., gt=0, description="Current installment number")
    full_chit_value: Decimal = Field(..., gt=0, description="Total chit fund value")
    chit_frequency_per_year: int = Field(..., gt=0, le=12, description="Installments per year")
    previous_installments: List[Decimal] = Field(
        ..., 
        min_items=0,
        description="List of previously paid installments"
    )
    bid_amount: Decimal = Field(..., gt=0, description="Bid amount for winning")
    winner_installment_amount: Optional[Decimal] = Field(
        None, 
        gt=0,
        description="Custom installment amount for winner (defaults to chit_value/total_installments)"
    )

    class Config:
        """Pydantic config for the model."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        json_schema_extra = {
            "example": {
                "total_installments": 14,
                "current_installment_number": 5,
                "full_chit_value": 700000,
                "chit_frequency_per_year": 2,
                "previous_installments": [42000, 40000, 40000, 43000],
                "bid_amount": 100000
            }
        }

    @field_validator('current_installment_number')
    @classmethod
    def validate_current_installment(cls, v, info):
        """Validate that current installment is not greater than total installments."""
        data = info.data if info else {}
        total = data.get('total_installments')
        if total and v > total:
            raise ValueError(f"Current installment ({v}) cannot exceed total installments ({total})")
        return v

    @field_validator('previous_installments')
    @classmethod
    def validate_previous_installments_count(cls, v, info):
        """Validate that previous installments count matches current installment number."""
        data = info.data if info else {}
        current = data.get('current_installment_number')
        if current and len(v) != current - 1:
            raise ValueError(
                f"Number of previous installments ({len(v)}) should be {current - 1} "
                f"for current installment number {current}"
            )
        return v

    @field_validator('bid_amount')
    @classmethod
    def validate_bid_amount(cls, v, info):
        """Validate that bid amount is reasonable compared to chit value."""
        data = info.data if info else {}
        chit_value = data.get('full_chit_value')
        if chit_value and v >= chit_value:
            raise ValueError(f"Bid amount ({v}) cannot be >= full chit value ({chit_value})")
        return v

    @field_validator('winner_installment_amount')
    @classmethod
    def validate_winner_installment_amount(cls, v, info):
        """Validate winner installment amount if provided."""
        if v is not None:
            data = info.data if info else {}
            chit_value = data.get('full_chit_value')
            total_installments = data.get('total_installments')
            if chit_value and total_installments:
                expected_amount = chit_value / total_installments
                if v > expected_amount * 2:  # Allow some flexibility
                    raise ValueError(
                        f"Winner installment amount ({v}) seems too high. "
                        f"Expected around {expected_amount}"
                    )
        return v

    def get_winner_installment_amount(self) -> Decimal:
        """Get the winner installment amount, calculating default if not provided."""
        if self.winner_installment_amount is not None:
            return self.winner_installment_amount
        return self.full_chit_value / self.total_installments


class BidScenario(BaseModel):
    """
    Model for individual bid scenario results.
    
    Attributes:
        bid_amount: The bid amount for this scenario
        prize_amount: Calculated prize amount
        annual_irr: Annual Internal Rate of Return
        monthly_irr: Monthly Internal Rate of Return (if applicable)
    """
    
    bid_amount: Decimal = Field(..., gt=0, description="Bid amount")
    prize_amount: Decimal = Field(..., description="Prize amount received")
    annual_irr: float = Field(..., description="Annual Internal Rate of Return")
    monthly_irr: Optional[float] = Field(None, description="Monthly Internal Rate of Return")

    class Config:
        """Pydantic config for the model."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ChitFundAnalysisResult(BaseModel):
    """
    Complete analysis result for a chit fund configuration.
    
    Attributes:
        config: The original chit fund configuration
        prize_amount: Calculated prize amount
        cashflows: Generated cashflow array
        annual_irr: Annual Internal Rate of Return
        period_irr: IRR per payment period
    """
    
    config: ChitFundConfig
    prize_amount: Decimal
    cashflows: List[Decimal]
    annual_irr: float
    period_irr: float

    class Config:
        """Pydantic config for the model."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ComparisonScenario(BaseModel):
    """
    Model for individual comparison scenario results.
    
    Attributes:
        scenario_name: Name of the scenario
        cashflows: Complete cashflow array for the scenario
        annual_irr: Annual Internal Rate of Return
        final_absolute_value: Absolute final value at end of tenure
        total_invested: Total amount invested/paid
        net_gain: Net gain (final_value - total_invested)
        details: Additional scenario-specific details
    """
    
    scenario_name: str = Field(..., description="Scenario name")
    cashflows: List[Decimal] = Field(..., description="Cashflow array")
    annual_irr: float = Field(..., description="Annual Internal Rate of Return")
    final_absolute_value: Decimal = Field(..., description="Final absolute value at tenure end")
    total_invested: Decimal = Field(..., description="Total amount invested")
    net_gain: Decimal = Field(..., description="Net gain (final - invested)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Scenario-specific details")

    class Config:
        """Pydantic config for the model."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ThreeWayComparisonResult(BaseModel):
    """
    Complete result for 3-way comparative analysis.
    
    Attributes:
        scenario1: Early win + lump sum scenario
        scenario2: Late win scenario
        scenario3: SIP investment scenario
        chit_name: Name of the chit fund
        total_installments: Total number of installments
        chit_value: Full chit fund value
        frequency_per_year: Payment frequency per year
        best_scenario_name: Name of the best performing scenario
        advantage_amount: Advantage amount over second best scenario
    """
    
    scenario1: ComparisonScenario
    scenario2: ComparisonScenario
    scenario3: ComparisonScenario
    chit_name: str
    total_installments: int
    chit_value: Decimal
    frequency_per_year: int
    best_scenario_name: str
    advantage_amount: Decimal

    class Config:
        """Pydantic config for the model."""
        json_encoders = {
            Decimal: lambda v: float(v)
        }