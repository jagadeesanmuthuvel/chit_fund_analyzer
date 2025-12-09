import unittest
from unittest.mock import MagicMock, patch
import os
import shutil
import tempfile
from datetime import date, datetime
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_app.data_manager.local import LocalDataManager
from streamlit_app.data_manager.gsheets import GoogleSheetsDataManager
from streamlit_app.data_manager.auth import GoogleAuthManager

class TestLocalDataManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_db.xlsx")
        self.db = LocalDataManager(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_and_get_chit(self):
        metadata = {
            'name': 'Test Chit',
            'total_installments': 12,
            'full_chit_value': 120000,
            'chit_frequency_per_year': 12,
            'start_date': date(2024, 1, 1)
        }
        chit_id = self.db.create_chit(metadata)
        
        chit = self.db.get_chit_by_id(chit_id)
        self.assertIsNotNone(chit)
        self.assertEqual(chit['name'], 'Test Chit')
        
        installments = self.db.get_installments(chit_id)
        self.assertEqual(len(installments), 12)

class TestGoogleAuthManager(unittest.TestCase):
    @patch('streamlit_app.data_manager.auth.st')
    def test_get_secret(self, mock_st):
        mock_st.secrets = {'TEST_KEY': 'secret_value'}
        val = GoogleAuthManager.get_secret('TEST_KEY')
        self.assertEqual(val, 'secret_value')
        
        # Test fallback to env var
        with patch.dict(os.environ, {'ENV_KEY': 'env_value'}):
             val = GoogleAuthManager.get_secret('ENV_KEY')
             self.assertEqual(val, 'env_value')

class TestGoogleSheetsDataManager(unittest.TestCase):
    @patch('streamlit_app.data_manager.gsheets.gspread')
    def test_init(self, mock_gspread):
        mock_creds = MagicMock()
        mock_client = MagicMock()
        mock_gspread.authorize.return_value = mock_client
        
        # Mock spreadsheet open/create
        mock_sheet = MagicMock()
        mock_client.open.return_value = mock_sheet
        
        # Mock worksheets
        mock_worksheet = MagicMock()
        mock_sheet.worksheet.return_value = mock_worksheet
        
        db = GoogleSheetsDataManager(mock_creds)
        
        mock_gspread.authorize.assert_called_with(mock_creds)
        mock_client.open.assert_called_with("ChitFundDB")

if __name__ == '__main__':
    unittest.main()
