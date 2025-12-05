"""
Google Sheets service for Chit Fund Analyzer with Automatic OAuth
Handles authentication and data operations with Google Sheets
"""

import gspread
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
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
import threading
import webbrowser
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Service class for Google Sheets operations with automatic OAuth"""
    
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
        self.credentials_file = 'oauth_credentials.json'
        self.token_file = 'token.pickle'
        
    def authenticate_automatically(self) -> bool:
        """
        Perform complete OAuth authentication automatically
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check for existing valid credentials
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                
                # Check if credentials are valid
                if creds and creds.valid:
                    self.oauth_credentials = creds
                    self.client = gspread.authorize(self.oauth_credentials)
                    logger.info("Using existing valid credentials")
                    return True
                
                # Refresh if expired but refreshable
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        with open(self.token_file, 'wb') as token:
                            pickle.dump(creds, token)
                        self.oauth_credentials = creds
                        self.client = gspread.authorize(self.oauth_credentials)
                        logger.info("Refreshed expired credentials")
                        return True
                    except Exception as refresh_error:
                        logger.warning(f"Failed to refresh credentials: {refresh_error}")
                        # Continue to new auth flow
            
            # Check if credentials file exists
            if not os.path.exists(self.credentials_file):
                logger.error(f"Credentials file not found: {self.credentials_file}")
                return False
            
            # Load client configuration
            with open(self.credentials_file, 'r') as f:
                client_config = json.load(f)
            
            # Create flow for installed app
            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes=self.SCOPES
            )
            
            # Run local server and get credentials automatically
            # This opens browser and handles the complete flow
            logger.info("Starting automatic OAuth flow...")
            creds = flow.run_local_server(
                port=0,  # Use any available port
                open_browser=True,
                success_message='Authentication successful! You can close this tab and return to the app.',
                timeout_seconds=300  # 5 minute timeout
            )
            
            # Save credentials for next time
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            
            self.oauth_credentials = creds
            self.client = gspread.authorize(self.oauth_credentials)
            
            # Test the connection
            try:
                self.client.openall()
                logger.info("OAuth authentication completed successfully")
                return True
            except Exception as test_error:
                logger.error(f"OAuth connection test failed: {test_error}")
                return False
                
        except Exception as e:
            logger.error(f"Automatic OAuth authentication failed: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self.client is not None and self.oauth_credentials is not None
    
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
            # First, try to find existing spreadsheet
            try:
                spreadsheets = self.client.openall()
                for sheet in spreadsheets:
                    if sheet.title == spreadsheet_name:
                        self.spreadsheet = sheet
                        self.spreadsheet_url = sheet.url
                        logger.info(f"Found existing spreadsheet: {spreadsheet_name}")
                        return True
            except Exception as e:
                logger.warning(f"Error searching for existing spreadsheets: {e}")
            
            # If not found and try_create is True, create new one
            if try_create:
                logger.info(f"Creating new spreadsheet: {spreadsheet_name}")
                self.spreadsheet = self.client.create(spreadsheet_name)
                self.spreadsheet_url = self.spreadsheet.url
                
                # Make the spreadsheet accessible
                self.spreadsheet.share('', perm_type='anyone', role='reader')
                
                # Create default worksheets
                self._setup_default_worksheets()
                
                logger.info(f"Created new spreadsheet: {spreadsheet_name}")
                logger.info(f"Spreadsheet URL: {self.spreadsheet_url}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating/getting spreadsheet: {e}")
            return False
    
    def _setup_default_worksheets(self):
        """Setup default worksheets in the spreadsheet"""
        try:
            # Get the default sheet
            default_sheet = self.spreadsheet.sheet1
            
            # Rename it to 'Chit Configurations'
            default_sheet.update_title('Chit Configurations')
            
            # Setup headers for chit configurations
            config_headers = [
                'Chit Name', 'Total Installments', 'Full Chit Value', 'Payment Frequency', 
                'Chit Frequency Per Year', 'Chit Method', 'Interest Rate (%)', 
                'Start Date', 'Installment Amount', 'Duration (Months)', 'Created Date'
            ]
            default_sheet.update('A1:K1', [config_headers])
            
            # Create Installments worksheet
            installments_sheet = self.spreadsheet.add_worksheet(
                title='Installments', 
                rows=1000, 
                cols=10
            )
            
            # Setup headers for installments
            installment_headers = [
                'Chit Name', 'Month', 'Date', 'Installment Amount',
                'Auction Amount', 'Dividend', 'Net Payment', 'Member Name', 'Notes'
            ]
            installments_sheet.update('A1:I1', [installment_headers])
            
            logger.info("Default worksheets setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up default worksheets: {e}")
    
    def save_chit_configuration(self, config: Dict) -> bool:
        """
        Save chit fund configuration to Google Sheets
        
        Args:
            config (Dict): Configuration data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.spreadsheet:
            logger.error("No spreadsheet available. Please create/get spreadsheet first.")
            return False
        
        try:
            # Get the configurations worksheet
            try:
                config_sheet = self.spreadsheet.worksheet('Chit Configurations')
            except Exception as worksheet_error:
                if "not found" in str(worksheet_error).lower() or "worksheet" in str(worksheet_error).lower():
                    logger.warning("'Chit Configurations' worksheet not found. Creating it...")
                    self._setup_default_worksheets()
                    config_sheet = self.spreadsheet.worksheet('Chit Configurations')
                else:
                    raise worksheet_error
            
            # Prepare data row
            row_data = [
                config.get('chit_name', ''),
                config.get('total_installments', 0),
                config.get('full_chit_value', 0),
                config.get('payment_frequency', 'Monthly'),
                config.get('chit_frequency_per_year', 12),
                config.get('chit_method', 'Auction'),
                config.get('interest_rate', 0),
                config.get('start_date', ''),
                config.get('installment_amount', 0),
                config.get('duration_months', 0),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            # Append the row
            config_sheet.append_row(row_data)
            
            logger.info(f"Saved configuration for chit: {config.get('chit_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving chit configuration: {e}")
            return False
    
    def get_chit_configurations(self) -> List[Dict]:
        """
        Get all chit fund configurations from Google Sheets
        
        Returns:
            List[Dict]: List of configuration dictionaries
        """
        if not self.spreadsheet:
            logger.error("No spreadsheet available. Please create/get spreadsheet first.")
            return []
        
        try:
            # Get the configurations worksheet
            try:
                config_sheet = self.spreadsheet.worksheet('Chit Configurations')
            except Exception as worksheet_error:
                if "not found" in str(worksheet_error).lower() or "worksheet" in str(worksheet_error).lower():
                    logger.warning("'Chit Configurations' worksheet not found. Creating it...")
                    self._setup_default_worksheets()
                    config_sheet = self.spreadsheet.worksheet('Chit Configurations')
                else:
                    raise worksheet_error
            
            # Get all records
            records = config_sheet.get_all_records()
            
            logger.info(f"Retrieved {len(records)} chit configurations")
            return records
            
        except Exception as e:
            logger.error(f"Error getting chit configurations: {e}")
            return []
    
    def save_installment(self, installment: Dict) -> bool:
        """
        Save installment data to Google Sheets
        
        Args:
            installment (Dict): Installment data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.spreadsheet:
            logger.error("No spreadsheet available. Please create/get spreadsheet first.")
            return False
        
        try:
            # Get the installments worksheet
            try:
                installments_sheet = self.spreadsheet.worksheet('Installments')
            except Exception as worksheet_error:
                if "not found" in str(worksheet_error).lower() or "worksheet" in str(worksheet_error).lower():
                    logger.warning("'Installments' worksheet not found. Creating it...")
                    self._setup_default_worksheets()
                    installments_sheet = self.spreadsheet.worksheet('Installments')
                else:
                    raise worksheet_error
            
            # Prepare data row
            row_data = [
                installment.get('chit_name', ''),
                installment.get('month', 0),
                installment.get('date', ''),
                installment.get('installment_amount', 0),
                installment.get('auction_amount', 0),
                installment.get('dividend', 0),
                installment.get('net_payment', 0),
                installment.get('member_name', ''),
                installment.get('notes', '')
            ]
            
            # Append the row
            installments_sheet.append_row(row_data)
            
            logger.info(f"Saved installment for chit: {installment.get('chit_name')}, month: {installment.get('month')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving installment: {e}")
            return False
    
    def get_installments(self, chit_name: str = None) -> List[Dict]:
        """
        Get installment data from Google Sheets
        
        Args:
            chit_name (str, optional): Filter by chit name
            
        Returns:
            List[Dict]: List of installment dictionaries
        """
        if not self.spreadsheet:
            logger.error("No spreadsheet available. Please create/get spreadsheet first.")
            return []
        
        try:
            # Get the installments worksheet
            try:
                logger.debug("Attempting to access 'Installments' worksheet...")
                installments_sheet = self.spreadsheet.worksheet('Installments')
                logger.debug("Successfully accessed 'Installments' worksheet")
            except Exception as worksheet_error:
                logger.error(f"Worksheet access error: {type(worksheet_error).__name__}: {str(worksheet_error)}")
                if "not found" in str(worksheet_error).lower() or "worksheet" in str(worksheet_error).lower():
                    logger.warning("'Installments' worksheet not found. Creating it...")
                    try:
                        self._setup_default_worksheets()
                        installments_sheet = self.spreadsheet.worksheet('Installments')
                        logger.info("Successfully created and accessed 'Installments' worksheet")
                    except Exception as creation_error:
                        logger.error(f"Failed to create Installments worksheet: {creation_error}")
                        return []  # Return empty list instead of failing
                else:
                    logger.error(f"Unexpected worksheet error: {worksheet_error}")
                    return []  # Return empty list for any worksheet access issues
            
            # Get all records
            records = installments_sheet.get_all_records()
            
            # Filter by chit name if provided
            if chit_name:
                records = [r for r in records if r.get('Chit Name') == chit_name]
            
            logger.info(f"Retrieved {len(records)} installments" + 
                       (f" for chit: {chit_name}" if chit_name else ""))
            return records
            
        except Exception as e:
            logger.error(f"Error getting installments: {type(e).__name__}: {str(e)}")
            return []
    
    def get_spreadsheet_url(self) -> Optional[str]:
        """Get the URL of the current spreadsheet"""
        return self.spreadsheet_url
    
    def logout(self):
        """Clear authentication and remove stored credentials"""
        self.client = None
        self.spreadsheet = None
        self.spreadsheet_url = None
        self.oauth_credentials = None
        
        # Remove stored token file
        if os.path.exists(self.token_file):
            try:
                os.remove(self.token_file)
                logger.info("Removed stored credentials")
            except Exception as e:
                logger.error(f"Error removing stored credentials: {e}")


# Global instance
google_sheets_service = GoogleSheetsService()