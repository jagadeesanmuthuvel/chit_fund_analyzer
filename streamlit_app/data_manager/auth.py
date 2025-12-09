import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import json
from typing import Optional, Dict, Any

class GoogleAuthManager:
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    @staticmethod
    def get_secret(key: str, default: str = None) -> str:
        """
        Get secret from st.secrets or os.environ.
        """
        # Try st.secrets first
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
        
        # Fallback to environment variables
        return os.environ.get(key, default)

    @staticmethod
    def get_client_config() -> Dict[str, Any]:
        """
        Construct client config from secrets.
        Expects standard Google OAuth client config structure.
        """
        # Try to get full json from a secret first
        client_config_json = GoogleAuthManager.get_secret("GOOGLE_CLIENT_SECRETS_JSON")
        if client_config_json:
            if isinstance(client_config_json, str):
                return json.loads(client_config_json)
            return client_config_json
            
        # Construct from individual fields
        return {
            "web": {
                "client_id": GoogleAuthManager.get_secret("GOOGLE_CLIENT_ID"),
                "client_secret": GoogleAuthManager.get_secret("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GoogleAuthManager.get_secret("GOOGLE_REDIRECT_URI", "http://localhost:8501")]
            }
        }

    @staticmethod
    def get_credentials() -> Optional[Credentials]:
        """
        Get valid credentials or None if login required.
        Handles token refresh.
        """
        creds = None
        
        # Check if token exists in session state
        if 'google_token' in st.session_state:
            token_info = st.session_state['google_token']
            try:
                creds = Credentials.from_authorized_user_info(token_info, GoogleAuthManager.SCOPES)
            except ValueError:
                return None
            
        # Validate and refresh if needed
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Update session state with refreshed token
                st.session_state['google_token'] = json.loads(creds.to_json())
            except Exception:
                creds = None
                
        return creds

    @staticmethod
    def get_auth_url() -> str:
        """
        Generate the authorization URL.
        """
        client_config = GoogleAuthManager.get_client_config()
        flow = Flow.from_client_config(
            client_config,
            scopes=GoogleAuthManager.SCOPES,
            redirect_uri=client_config['web']['redirect_uris'][0]
        )
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url

    @staticmethod
    def exchange_code(code: str) -> Credentials:
        """
        Exchange auth code for credentials.
        """
        client_config = GoogleAuthManager.get_client_config()
        flow = Flow.from_client_config(
            client_config,
            scopes=GoogleAuthManager.SCOPES,
            redirect_uri=client_config['web']['redirect_uris'][0]
        )
        
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Store in session state
        st.session_state['google_token'] = json.loads(creds.to_json())
        
        return creds
