from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd

class DataManager(ABC):
    """
    Abstract base class for data management operations.
    """
    
    CHITS_SHEET = "chits"
    INSTALLMENTS_SHEET = "installments"
    
    CHITS_COLUMNS = [
        "chit_id", "name", "description", "total_installments", 
        "full_chit_value", "chit_frequency_per_year", "start_date",
        "created_at", "updated_at", "version"
    ]
    
    INSTALLMENTS_COLUMNS = [
        "chit_id", "installment_number", "date", "amount_paid",
        "prize_amount", "discount", "annual_irr_winner", "winner_name",
        "is_winner", "notes"
    ]

    @abstractmethod
    def get_all_chits(self) -> List[Dict[str, Any]]:
        """Retrieve all chits from the database."""
        pass

    @abstractmethod
    def get_chit_by_id(self, chit_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific chit by ID."""
        pass

    @abstractmethod
    def create_chit(self, metadata: Dict[str, Any]) -> str:
        """Create a new chit with initial installments."""
        pass

    @abstractmethod
    def update_chit_metadata(self, chit_id: str, metadata: Dict[str, Any]) -> None:
        """Update chit metadata (name, description, etc.)."""
        pass

    @abstractmethod
    def get_installments(self, chit_id: str) -> List[Dict[str, Any]]:
        """Get all installments for a specific chit."""
        pass

    @abstractmethod
    def update_installments(self, chit_id: str, updates: List[Dict[str, Any]]) -> None:
        """Update multiple installments."""
        pass
    
    @abstractmethod
    def delete_chit(self, chit_id: str) -> None:
        """Delete a chit and its installments."""
        pass
