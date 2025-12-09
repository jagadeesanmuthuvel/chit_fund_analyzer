from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import uuid
import gspread
from google.oauth2.credentials import Credentials
from .base import DataManager

class GoogleSheetsDataManager(DataManager):
    """
    Google Sheets implementation of DataManager.
    """
    
    SPREADSHEET_NAME = "ChitFundDB"
    
    def __init__(self, credentials: Credentials):
        """
        Initialize the Google Sheets connection.
        
        Args:
            credentials: Valid Google OAuth credentials
        """
        self.client = gspread.authorize(credentials)
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Create the spreadsheet and sheets if they don't exist."""
        try:
            self.spreadsheet = self.client.open(self.SPREADSHEET_NAME)
        except gspread.SpreadsheetNotFound:
            self.spreadsheet = self.client.create(self.SPREADSHEET_NAME)
            
        # Check/Create Chits sheet
        try:
            self.chits_sheet = self.spreadsheet.worksheet(self.CHITS_SHEET)
        except gspread.WorksheetNotFound:
            self.chits_sheet = self.spreadsheet.add_worksheet(
                title=self.CHITS_SHEET, 
                rows=100, 
                cols=len(self.CHITS_COLUMNS)
            )
            self.chits_sheet.append_row(self.CHITS_COLUMNS)

        # Check/Create Installments sheet
        try:
            self.installments_sheet = self.spreadsheet.worksheet(self.INSTALLMENTS_SHEET)
        except gspread.WorksheetNotFound:
            self.installments_sheet = self.spreadsheet.add_worksheet(
                title=self.INSTALLMENTS_SHEET, 
                rows=1000, 
                cols=len(self.INSTALLMENTS_COLUMNS)
            )
            self.installments_sheet.append_row(self.INSTALLMENTS_COLUMNS)
            
    def _get_df(self, sheet) -> pd.DataFrame:
        """Helper to get DataFrame from sheet."""
        data = sheet.get_all_records()
        return pd.DataFrame(data)

    def _save_df(self, sheet, df: pd.DataFrame) -> None:
        """Helper to save DataFrame to sheet (overwrite)."""
        # Clear existing content
        sheet.clear()
        # Write headers
        sheet.append_row(df.columns.tolist())
        # Write data
        # Handle dates and NaNs for JSON serialization
        df_to_save = df.fillna('').astype(str)
        # Replace 'nan' string with empty string if any remained
        df_to_save = df_to_save.replace('nan', '')
        
        data = df_to_save.values.tolist()
        if data:
            sheet.append_rows(data)

    def get_all_chits(self) -> List[Dict[str, Any]]:
        records = self.chits_sheet.get_all_records()
        
        # Convert date strings
        for chit in records:
            if chit.get('start_date'):
                try:
                    chit['start_date'] = datetime.fromisoformat(str(chit['start_date'])).date()
                except ValueError:
                    pass # Keep as string if parsing fails
        return records

    def get_chit_by_id(self, chit_id: str) -> Optional[Dict[str, Any]]:
        chits = self.get_all_chits()
        for chit in chits:
            if str(chit['chit_id']) == str(chit_id):
                return chit
        return None

    def create_chit(self, metadata: Dict[str, Any]) -> str:
        chit_id = metadata.get('chit_id', str(uuid.uuid4()))
        now = datetime.now().isoformat()
        
        chit_record = {
            'chit_id': chit_id,
            'name': metadata['name'],
            'description': metadata.get('description', ''),
            'total_installments': int(metadata['total_installments']),
            'full_chit_value': float(metadata['full_chit_value']),
            'chit_frequency_per_year': int(metadata['chit_frequency_per_year']),
            'start_date': str(metadata['start_date']),
            'created_at': now,
            'updated_at': now,
            'version': 1
        }
        
        # Append to chits sheet
        # Ensure order matches columns
        row = [chit_record.get(col, '') for col in self.CHITS_COLUMNS]
        self.chits_sheet.append_row(row)
        
        # Create installments
        start_date = pd.to_datetime(metadata['start_date'])
        
        if metadata['chit_frequency_per_year'] == 12:
            period_months = 1
        elif metadata['chit_frequency_per_year'] == 4:
            period_months = 3
        elif metadata['chit_frequency_per_year'] == 2:
            period_months = 6
        else:
            period_months = 12 // metadata['chit_frequency_per_year']
            
        installment_rows = []
        for i in range(int(metadata['total_installments'])):
            installment_date = start_date + pd.DateOffset(months=period_months * i)
            
            inst_record = {
                'chit_id': chit_id,
                'installment_number': i + 1,
                'date': installment_date.date().isoformat(),
                'amount_paid': '',
                'prize_amount': '',
                'discount': '',
                'annual_irr_winner': '',
                'winner_name': '',
                'is_winner': False,
                'notes': ''
            }
            row = [inst_record.get(col, '') for col in self.INSTALLMENTS_COLUMNS]
            installment_rows.append(row)
            
        self.installments_sheet.append_rows(installment_rows)
        
        return chit_id

    def update_chit_metadata(self, chit_id: str, metadata: Dict[str, Any]) -> None:
        df = self._get_df(self.chits_sheet)
        
        # Ensure chit_id is string for comparison
        df['chit_id'] = df['chit_id'].astype(str)
        
        mask = df['chit_id'] == str(chit_id)
        if not mask.any():
            raise ValueError(f"Chit with ID {chit_id} not found")
            
        allowed_fields = ['name', 'description']
        for field in allowed_fields:
            if field in metadata:
                df.loc[mask, field] = metadata[field]
                
        df.loc[mask, 'version'] = pd.to_numeric(df.loc[mask, 'version']) + 1
        df.loc[mask, 'updated_at'] = datetime.now().isoformat()
        
        self._save_df(self.chits_sheet, df)

    def get_installments(self, chit_id: str) -> List[Dict[str, Any]]:
        records = self.installments_sheet.get_all_records()
        
        # Filter
        installments = [r for r in records if str(r['chit_id']) == str(chit_id)]
        
        # Sort
        installments.sort(key=lambda x: x['installment_number'])
        
        # Convert dates
        for inst in installments:
            if inst.get('date'):
                try:
                    inst['date'] = datetime.fromisoformat(str(inst['date'])).date()
                except ValueError:
                    pass
                    
        return installments

    def update_installments(self, chit_id: str, updates: List[Dict[str, Any]]) -> None:
        # Read all installments
        df = self._get_df(self.installments_sheet)
        df['chit_id'] = df['chit_id'].astype(str)
        
        for update in updates:
            inst_num = update['installment_number']
            mask = (df['chit_id'] == str(chit_id)) & (df['installment_number'] == inst_num)
            
            if not mask.any():
                continue
                
            for field, value in update.items():
                if field != 'installment_number' and field in self.INSTALLMENTS_COLUMNS:
                    # Handle None/NaN
                    if value is None:
                        value = ''
                    df.loc[mask, field] = value
                    
        self._save_df(self.installments_sheet, df)
        
        # Update chit version
        chits_df = self._get_df(self.chits_sheet)
        chits_df['chit_id'] = chits_df['chit_id'].astype(str)
        chit_mask = chits_df['chit_id'] == str(chit_id)
        
        if chit_mask.any():
            chits_df.loc[chit_mask, 'version'] = pd.to_numeric(chits_df.loc[chit_mask, 'version']) + 1
            chits_df.loc[chit_mask, 'updated_at'] = datetime.now().isoformat()
            self._save_df(self.chits_sheet, chits_df)

    def delete_chit(self, chit_id: str) -> None:
        chits_df = self._get_df(self.chits_sheet)
        inst_df = self._get_df(self.installments_sheet)
        
        chits_df['chit_id'] = chits_df['chit_id'].astype(str)
        inst_df['chit_id'] = inst_df['chit_id'].astype(str)
        
        chits_df = chits_df[chits_df['chit_id'] != str(chit_id)]
        inst_df = inst_df[inst_df['chit_id'] != str(chit_id)]
        
        self._save_df(self.chits_sheet, chits_df)
        self._save_df(self.installments_sheet, inst_df)
