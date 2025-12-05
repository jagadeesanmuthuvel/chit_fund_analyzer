"""
Google Sheets service for Chit Fund Analyzer
Handles authentication and data operations with Google Sheets
"""

import gspread
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import streamlit as st
import json
import os
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime
import logging
import pickle
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Service class for Google Sheets operations"""
    
    # Required scopes for Google Sheets API
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.spreadsheet_url = None
        self.oauth_credentials = None
        
    def authenticate_with_oauth(self, client_config: Dict) -> Tuple[bool, Optional[str]]:
        """
        Authenticate using OAuth flow
        
        Args:
            client_config (Dict): OAuth client configuration
            
        Returns:
            Tuple[bool, Optional[str]]: (success, auth_url or None)
        """
        try:
            # Create flow from client config
            flow = Flow.from_client_config(
                client_config,
                scopes=self.SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # For manual auth flow
            )
            
            # Generate authorization URL
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            logger.info("OAuth flow initialized successfully")
            return True, auth_url
            
        except Exception as e:
            logger.error(f"OAuth flow initialization failed: {e}")
            return False, None
    
    def complete_oauth_flow(self, client_config: Dict, auth_code: str) -> bool:
        """
        Complete OAuth flow with authorization code
        
        Args:
            client_config (Dict): OAuth client configuration
            auth_code (str): Authorization code from user
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create flow from client config
            flow = Flow.from_client_config(
                client_config,
                scopes=self.SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            
            # Fetch token using authorization code
            flow.fetch_token(code=auth_code)
            
            # Store credentials
            self.oauth_credentials = flow.credentials
            
            # Initialize gspread client
            self.client = gspread.authorize(self.oauth_credentials)
            
            # Test the connection
            try:
                self.client.openall()
                logger.info("OAuth authentication successful")
                return True
            except Exception as test_error:
                logger.error(f"OAuth connection test failed: {test_error}")
                return False
                
        except Exception as e:
            logger.error(f"OAuth completion failed: {e}")
            return False
    
    def refresh_oauth_credentials(self) -> bool:
        """
        Refresh OAuth credentials if they're expired
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.oauth_credentials:
            return False
        
        try:
            if self.oauth_credentials.expired:
                request = Request()
                self.oauth_credentials.refresh(request)
                
                # Re-initialize client with refreshed credentials
                self.client = gspread.authorize(self.oauth_credentials)
                logger.info("OAuth credentials refreshed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"OAuth refresh failed: {e}")
            return False
    
    def create_or_get_spreadsheet(self, spreadsheet_name: str, try_create: bool = True) -> bool:
        """
        Create a new spreadsheet or get existing one
        
        Args:
            spreadsheet_name (str): Name of the spreadsheet
            try_create (bool): Whether to try creating if not found
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Not authenticated. Please authenticate first.")
            return False
        
        try:
            # Try to open existing spreadsheet first
            try:
                self.spreadsheet = self.client.open(spreadsheet_name)
                logger.info(f"Opened existing spreadsheet: {spreadsheet_name}")
            except gspread.SpreadsheetNotFound:
                if not try_create:
                    logger.error(f"Spreadsheet '{spreadsheet_name}' not found and creation disabled")
                    return False
                
                # Try to create new spreadsheet
                try:
                    self.spreadsheet = self.client.create(spreadsheet_name)
                    logger.info(f"Created new spreadsheet: {spreadsheet_name}")
                except Exception as create_error:
                    logger.error(f"Failed to create spreadsheet: {create_error}")
                    raise create_error
            
            # Get the spreadsheet URL
            self.spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}"
            
            # Initialize default worksheets
            self._initialize_worksheets()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create/get spreadsheet: {e}")
            return False
    
    def _initialize_worksheets(self):
        """Initialize required worksheets with proper headers"""
        try:
            # Check if worksheets exist, create if not
            worksheet_configs = {
                'Chit_Configurations': [
                    'Chit Name', 'Chit Amount', 'Total Months', 'Monthly Installment',
                    'Commission Rate', 'Chit Method', 'Created Date', 'Updated Date',
                    'Status', 'Description'
                ],
                'Installment_History': [
                    'Chit Name', 'Month', 'Installment Date', 'Amount Paid',
                    'Bid Amount', 'Winner', 'Commission', 'Net Amount',
                    'Payment Status', 'Notes'
                ],
                'User_Profiles': [
                    'User ID', 'User Name', 'Email', 'Phone',
                    'Address', 'Created Date', 'Status'
                ]
            }
            
            existing_worksheets = [ws.title for ws in self.spreadsheet.worksheets()]
            
            for ws_name, headers in worksheet_configs.items():
                if ws_name not in existing_worksheets:
                    # Create new worksheet
                    worksheet = self.spreadsheet.add_worksheet(
                        title=ws_name, rows=1000, cols=len(headers)
                    )
                    # Add headers
                    worksheet.append_row(headers)
                    logger.info(f"Created worksheet: {ws_name}")
                else:
                    logger.info(f"Worksheet already exists: {ws_name}")
            
            # Remove default 'Sheet1' if it exists and is empty
            if 'Sheet1' in existing_worksheets:
                try:
                    sheet1 = self.spreadsheet.worksheet('Sheet1')
                    if len(sheet1.get_all_values()) <= 1:  # Only header or empty
                        self.spreadsheet.del_worksheet(sheet1)
                        logger.info("Removed default Sheet1")
                except:
                    pass  # Ignore if can't remove
                    
        except Exception as e:
            logger.error(f"Failed to initialize worksheets: {e}")
    
    def save_chit_configuration(self, config_data: Dict) -> bool:
        """
        Save chit configuration to Google Sheets
        
        Args:
            config_data (Dict): Configuration data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.spreadsheet:
            logger.error("No spreadsheet available. Please create/open a spreadsheet first.")
            return False
        
        try:
            worksheet = self.spreadsheet.worksheet('Chit_Configurations')
            
            # Check if chit name already exists
            existing_data = worksheet.get_all_records()
            chit_exists = any(row['Chit Name'] == config_data['chit_name'] 
                            for row in existing_data)
            
            if chit_exists:
                # Update existing record
                for i, row in enumerate(existing_data):
                    if row['Chit Name'] == config_data['chit_name']:
                        row_num = i + 2  # +2 because of header and 0-indexing
                        worksheet.update_row(row_num, [
                            config_data['chit_name'],
                            config_data['chit_amount'],
                            config_data['total_months'],
                            config_data['monthly_installment'],
                            config_data['commission_rate'],
                            config_data['chit_method'],
                            row['Created Date'],  # Keep original creation date
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            config_data.get('status', 'Active'),
                            config_data.get('description', '')
                        ])
                        logger.info(f"Updated chit configuration: {config_data['chit_name']}")
                        break
            else:
                # Add new record
                new_row = [
                    config_data['chit_name'],
                    config_data['chit_amount'],
                    config_data['total_months'],
                    config_data['monthly_installment'],
                    config_data['commission_rate'],
                    config_data['chit_method'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    config_data.get('status', 'Active'),
                    config_data.get('description', '')
                ]
                worksheet.append_row(new_row)
                logger.info(f"Added new chit configuration: {config_data['chit_name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save chit configuration: {e}")
            return False
    
    def save_installment_data(self, installments: List[Dict]) -> bool:
        """
        Save installment history to Google Sheets
        
        Args:
            installments (List[Dict]): List of installment records
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.spreadsheet:
            logger.error("No spreadsheet available.")
            return False
        
        try:
            worksheet = self.spreadsheet.worksheet('Installment_History')
            
            # Clear existing data for this chit (optional - you might want to keep history)
            # existing_data = worksheet.get_all_records()
            # ... implement clearing logic if needed ...
            
            # Add installment records
            for installment in installments:
                new_row = [
                    installment['chit_name'],
                    installment['month'],
                    installment.get('installment_date', ''),
                    installment.get('amount_paid', 0),
                    installment.get('bid_amount', 0),
                    installment.get('winner', ''),
                    installment.get('commission', 0),
                    installment.get('net_amount', 0),
                    installment.get('payment_status', 'Paid'),
                    installment.get('notes', '')
                ]
                worksheet.append_row(new_row)
            
            logger.info(f"Saved {len(installments)} installment records")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save installment data: {e}")
            return False
    
    def get_chit_names(self) -> List[str]:
        """
        Get list of all chit names from the spreadsheet
        
        Returns:
            List[str]: List of chit names
        """
        if not self.spreadsheet:
            return []
        
        try:
            worksheet = self.spreadsheet.worksheet('Chit_Configurations')
            data = worksheet.get_all_records()
            return [row['Chit Name'] for row in data if row['Chit Name']]
            
        except Exception as e:
            logger.error(f"Failed to get chit names: {e}")
            return []
    
    def get_chit_configuration(self, chit_name: str) -> Optional[Dict]:
        """
        Get chit configuration by name
        
        Args:
            chit_name (str): Name of the chit
            
        Returns:
            Optional[Dict]: Configuration data or None if not found
        """
        if not self.spreadsheet:
            return None
        
        try:
            worksheet = self.spreadsheet.worksheet('Chit_Configurations')
            data = worksheet.get_all_records()
            
            for row in data:
                if row['Chit Name'] == chit_name:
                    return {
                        'chit_name': row['Chit Name'],
                        'chit_amount': float(row['Chit Amount']),
                        'total_months': int(row['Total Months']),
                        'monthly_installment': float(row['Monthly Installment']),
                        'commission_rate': float(row['Commission Rate']),
                        'chit_method': row['Chit Method'],
                        'status': row['Status'],
                        'description': row['Description']
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get chit configuration: {e}")
            return None
    
    def get_installment_history(self, chit_name: str) -> List[Dict]:
        """
        Get installment history for a specific chit
        
        Args:
            chit_name (str): Name of the chit
            
        Returns:
            List[Dict]: List of installment records
        """
        if not self.spreadsheet:
            return []
        
        try:
            worksheet = self.spreadsheet.worksheet('Installment_History')
            data = worksheet.get_all_records()
            
            installments = []
            for row in data:
                if row['Chit Name'] == chit_name:
                    installments.append({
                        'month': int(row['Month']),
                        'installment_date': row['Installment Date'],
                        'amount_paid': float(row['Amount Paid']) if row['Amount Paid'] else 0,
                        'bid_amount': float(row['Bid Amount']) if row['Bid Amount'] else 0,
                        'winner': row['Winner'],
                        'commission': float(row['Commission']) if row['Commission'] else 0,
                        'net_amount': float(row['Net Amount']) if row['Net Amount'] else 0,
                        'payment_status': row['Payment Status'],
                        'notes': row['Notes']
                    })
            
            # Sort by month
            return sorted(installments, key=lambda x: x['month'])
            
        except Exception as e:
            logger.error(f"Failed to get installment history: {e}")
            return []
    
    def is_authenticated(self) -> bool:
        """Check if the service is authenticated"""
        return self.client is not None
    
    def get_spreadsheet_url(self) -> Optional[str]:
        """Get the URL of the current spreadsheet"""
        return self.spreadsheet_url
    
    def list_existing_spreadsheets(self) -> List[Dict[str, str]]:
        """
        List all existing spreadsheets accessible to the service account
        
        Returns:
            List[Dict]: List of spreadsheet info with name and id
        """
        if not self.client:
            return []
        
        try:
            spreadsheets = self.client.openall()
            return [{"name": sheet.title, "id": sheet.id} for sheet in spreadsheets]
        except Exception as e:
            logger.error(f"Failed to list spreadsheets: {e}")
            return []


# Singleton instance
sheets_service = GoogleSheetsService()