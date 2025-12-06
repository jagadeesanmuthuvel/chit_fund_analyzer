"""
Data Access Layer for Chit Fund Manager.

This module provides Excel-based database operations with an interface
designed to be easily portable to Google Sheets in future versions.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date
import pandas as pd
import uuid


class ChitFundDB:
    """
    Excel-based database manager for chit fund data.
    
    This class abstracts file I/O operations and provides a clean interface
    that can be easily migrated to Google Sheets in Version 2.
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
    
    def __init__(self, file_path: str = "data/chit_fund_db.xlsx"):
        """
        Initialize the database connection.
        
        Args:
            file_path: Path to the Excel database file
        """
        self.file_path = Path(file_path)
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Create the database file with proper schema if it doesn't exist."""
        if not self.file_path.exists():
            # Create directory if needed
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create empty DataFrames with correct schema
            chits_df = pd.DataFrame(columns=self.CHITS_COLUMNS)
            installments_df = pd.DataFrame(columns=self.INSTALLMENTS_COLUMNS)
            
            # Write to Excel
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                chits_df.to_excel(writer, sheet_name=self.CHITS_SHEET, index=False)
                installments_df.to_excel(writer, sheet_name=self.INSTALLMENTS_SHEET, index=False)
    
    def _read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """
        Read a sheet from the Excel file.
        
        Args:
            sheet_name: Name of the sheet to read
            
        Returns:
            DataFrame containing the sheet data
        """
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            return df
        except Exception as e:
            raise Exception(f"Error reading sheet '{sheet_name}': {str(e)}")
    
    def _write_sheets(self, sheets: Dict[str, pd.DataFrame]) -> None:
        """
        Write multiple sheets to the Excel file.
        
        Args:
            sheets: Dictionary mapping sheet names to DataFrames
        """
        try:
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                for sheet_name, df in sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            raise Exception(f"Error writing to database: {str(e)}")
    
    def get_all_chits(self) -> List[Dict[str, Any]]:
        """
        Retrieve all chits from the database.
        
        Returns:
            List of chit dictionaries
        """
        df = self._read_sheet(self.CHITS_SHEET)
        
        if df.empty:
            return []
        
        # Convert DataFrame to list of dicts
        chits = df.to_dict('records')
        
        # Convert date strings back to date objects
        for chit in chits:
            if pd.notna(chit.get('start_date')):
                if isinstance(chit['start_date'], str):
                    chit['start_date'] = datetime.fromisoformat(chit['start_date']).date()
                elif isinstance(chit['start_date'], datetime):
                    chit['start_date'] = chit['start_date'].date()
        
        return chits
    
    def get_chit_by_id(self, chit_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific chit by ID.
        
        Args:
            chit_id: The chit ID to retrieve
            
        Returns:
            Chit dictionary or None if not found
        """
        chits = self.get_all_chits()
        for chit in chits:
            if str(chit['chit_id']) == str(chit_id):
                return chit
        return None
    
    def create_chit(self, metadata: Dict[str, Any]) -> str:
        """
        Create a new chit with initial installments.
        
        Args:
            metadata: Dictionary containing chit configuration
                Required keys: name, total_installments, full_chit_value,
                              chit_frequency_per_year, start_date
                Optional keys: description
        
        Returns:
            The created chit_id
        """
        # Generate unique ID
        chit_id = str(uuid.uuid4())
        
        # Read existing data
        chits_df = self._read_sheet(self.CHITS_SHEET)
        installments_df = self._read_sheet(self.INSTALLMENTS_SHEET)
        
        # Create chit record
        now = datetime.now()
        chit_record = {
            'chit_id': chit_id,
            'name': metadata['name'],
            'description': metadata.get('description', ''),
            'total_installments': int(metadata['total_installments']),
            'full_chit_value': float(metadata['full_chit_value']),
            'chit_frequency_per_year': int(metadata['chit_frequency_per_year']),
            'start_date': metadata['start_date'],
            'created_at': now,
            'updated_at': now,
            'version': 1
        }
        
        # Add to chits DataFrame
        chits_df = pd.concat([chits_df, pd.DataFrame([chit_record])], ignore_index=True)
        
        # Create installment records
        installment_records = []
        start_date = pd.to_datetime(metadata['start_date'])
        
        # Calculate period delta based on frequency
        if metadata['chit_frequency_per_year'] == 12:
            period_months = 1
        elif metadata['chit_frequency_per_year'] == 4:
            period_months = 3
        elif metadata['chit_frequency_per_year'] == 2:
            period_months = 6
        else:
            period_months = 12 // metadata['chit_frequency_per_year']
        
        for i in range(int(metadata['total_installments'])):
            installment_date = start_date + pd.DateOffset(months=period_months * i)
            
            installment_record = {
                'chit_id': chit_id,
                'installment_number': i + 1,
                'date': installment_date,
                'amount_paid': None,
                'prize_amount': None,
                'discount': None,
                'annual_irr_winner': None,
                'winner_name': None,
                'is_winner': False,
                'notes': ''
            }
            installment_records.append(installment_record)
        
        # Add to installments DataFrame
        installments_df = pd.concat(
            [installments_df, pd.DataFrame(installment_records)], 
            ignore_index=True
        )
        
        # Write to database
        self._write_sheets({
            self.CHITS_SHEET: chits_df,
            self.INSTALLMENTS_SHEET: installments_df
        })
        
        return chit_id
    
    def update_chit_metadata(self, chit_id: str, metadata: Dict[str, Any]) -> None:
        """
        Update chit metadata (name, description, etc.).
        
        Args:
            chit_id: The chit ID to update
            metadata: Dictionary containing fields to update
        """
        chits_df = self._read_sheet(self.CHITS_SHEET)
        
        # Find the chit
        mask = chits_df['chit_id'] == chit_id
        if not mask.any():
            raise ValueError(f"Chit with ID {chit_id} not found")
        
        # Update allowed fields
        allowed_fields = ['name', 'description']
        for field in allowed_fields:
            if field in metadata:
                chits_df.loc[mask, field] = metadata[field]
        
        # Update version and timestamp
        chits_df.loc[mask, 'version'] = chits_df.loc[mask, 'version'] + 1
        chits_df.loc[mask, 'updated_at'] = datetime.now()
        
        # Read installments to preserve them
        installments_df = self._read_sheet(self.INSTALLMENTS_SHEET)
        
        # Write back
        self._write_sheets({
            self.CHITS_SHEET: chits_df,
            self.INSTALLMENTS_SHEET: installments_df
        })
    
    def get_installments(self, chit_id: str) -> List[Dict[str, Any]]:
        """
        Get all installments for a specific chit.
        
        Args:
            chit_id: The chit ID
            
        Returns:
            List of installment dictionaries
        """
        installments_df = self._read_sheet(self.INSTALLMENTS_SHEET)
        
        # Filter by chit_id
        filtered_df = installments_df[installments_df['chit_id'] == chit_id]
        
        if filtered_df.empty:
            return []
        
        # Sort by installment number
        filtered_df = filtered_df.sort_values('installment_number')
        
        # Convert to list of dicts
        installments = filtered_df.to_dict('records')
        
        # Convert date strings back to date objects
        for inst in installments:
            if pd.notna(inst.get('date')):
                if isinstance(inst['date'], str):
                    inst['date'] = datetime.fromisoformat(inst['date']).date()
                elif isinstance(inst['date'], datetime):
                    inst['date'] = inst['date'].date()
        
        return installments
    
    def update_installments(
        self, 
        chit_id: str, 
        updates: List[Dict[str, Any]]
    ) -> None:
        """
        Update multiple installments.
        
        Args:
            chit_id: The chit ID
            updates: List of update dictionaries, each containing:
                     - installment_number: The installment to update
                     - Other fields to update (amount_paid, bid_amount, etc.)
        """
        # Read both sheets
        chits_df = self._read_sheet(self.CHITS_SHEET)
        installments_df = self._read_sheet(self.INSTALLMENTS_SHEET)
        
        # Apply updates
        for update in updates:
            installment_number = update['installment_number']
            
            # Find the row
            mask = (
                (installments_df['chit_id'] == chit_id) & 
                (installments_df['installment_number'] == installment_number)
            )
            
            if not mask.any():
                continue
            
            # Update fields
            for field, value in update.items():
                if field != 'installment_number' and field in self.INSTALLMENTS_COLUMNS:
                    installments_df.loc[mask, field] = value
        
        # Update chit version
        chit_mask = chits_df['chit_id'] == chit_id
        if chit_mask.any():
            chits_df.loc[chit_mask, 'version'] = chits_df.loc[chit_mask, 'version'] + 1
            chits_df.loc[chit_mask, 'updated_at'] = datetime.now()
        
        # Write back
        self._write_sheets({
            self.CHITS_SHEET: chits_df,
            self.INSTALLMENTS_SHEET: installments_df
        })
    
    def delete_chit(self, chit_id: str) -> None:
        """
        Delete a chit and all its installments.
        
        Args:
            chit_id: The chit ID to delete
        """
        chits_df = self._read_sheet(self.CHITS_SHEET)
        installments_df = self._read_sheet(self.INSTALLMENTS_SHEET)
        
        # Remove from both sheets
        chits_df = chits_df[chits_df['chit_id'] != chit_id]
        installments_df = installments_df[installments_df['chit_id'] != chit_id]
        
        # Write back
        self._write_sheets({
            self.CHITS_SHEET: chits_df,
            self.INSTALLMENTS_SHEET: installments_df
        })
