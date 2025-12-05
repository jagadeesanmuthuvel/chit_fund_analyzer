"""
Test script for Google Sheets integration
Run this to verify that the Google Sheets service works correctly
"""

import json
import sys
from google_sheets_service import GoogleSheetsService
from datetime import datetime

def test_google_sheets_integration():
    """Test Google Sheets service functionality"""
    
    print("🧪 Testing Google Sheets Integration")
    print("=" * 50)
    
    # Initialize service
    service = GoogleSheetsService()
    
    print("📝 To test the integration, you need:")
    print("1. Google Cloud Project with Sheets & Drive APIs enabled")
    print("2. Service account JSON credentials")
    print("3. A test spreadsheet name")
    print()
    
    # Get credentials from user
    print("Please paste your service account JSON credentials:")
    print("(Paste and press Enter twice)")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "" and len(lines) > 0:
                break
            lines.append(line)
        except EOFError:
            break
    
    credentials_json = "\n".join(lines)
    
    if not credentials_json.strip():
        print("❌ No credentials provided. Exiting.")
        return False
    
    print("\n🔐 Testing authentication...")
    
    # Test authentication
    try:
        success = service.authenticate_with_service_account(credentials_json)
        if not success:
            print("❌ Authentication failed!")
            return False
        
        print("✅ Authentication successful!")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test spreadsheet creation
    test_spreadsheet_name = f"Test_Chit_Analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n📊 Creating test spreadsheet: {test_spreadsheet_name}")
    
    try:
        success = service.create_or_get_spreadsheet(test_spreadsheet_name)
        if not success:
            print("❌ Failed to create spreadsheet!")
            return False
        
        print("✅ Spreadsheet created successfully!")
        print(f"🔗 URL: {service.get_spreadsheet_url()}")
        
    except Exception as e:
        print(f"❌ Spreadsheet creation error: {e}")
        return False
    
    # Test configuration save
    print("\n💾 Testing configuration save...")
    
    test_config = {
        'chit_name': 'Test Chit Fund',
        'chit_amount': 100000,
        'total_months': 20,
        'monthly_installment': 5000,
        'commission_rate': 5.0,
        'chit_method': 'Auction/Bidding',
        'description': 'Test chit fund for integration testing',
        'status': 'Active'
    }
    
    try:
        success = service.save_chit_configuration(test_config)
        if not success:
            print("❌ Failed to save configuration!")
            return False
        
        print("✅ Configuration saved successfully!")
        
    except Exception as e:
        print(f"❌ Configuration save error: {e}")
        return False
    
    # Test installment save
    print("\n📅 Testing installment save...")
    
    test_installments = [
        {
            'chit_name': 'Test Chit Fund',
            'month': 1,
            'installment_date': '2024-01-15',
            'amount_paid': 5000,
            'bid_amount': 10000,
            'winner': 'John Doe',
            'commission': 500,
            'net_amount': 9500,
            'payment_status': 'Paid',
            'notes': 'First installment - test data'
        },
        {
            'chit_name': 'Test Chit Fund',
            'month': 2,
            'installment_date': '2024-02-15',
            'amount_paid': 5000,
            'bid_amount': 8000,
            'winner': 'Jane Smith',
            'commission': 400,
            'net_amount': 7600,
            'payment_status': 'Paid',
            'notes': 'Second installment - test data'
        }
    ]
    
    try:
        success = service.save_installment_data(test_installments)
        if not success:
            print("❌ Failed to save installments!")
            return False
        
        print("✅ Installments saved successfully!")
        
    except Exception as e:
        print(f"❌ Installment save error: {e}")
        return False
    
    # Test data retrieval
    print("\n📋 Testing data retrieval...")
    
    try:
        # Get chit names
        chit_names = service.get_chit_names()
        print(f"✅ Retrieved chit names: {chit_names}")
        
        # Get configuration
        config = service.get_chit_configuration('Test Chit Fund')
        if config:
            print(f"✅ Retrieved configuration: {config['chit_name']}")
        else:
            print("⚠️  No configuration found")
        
        # Get installment history
        history = service.get_installment_history('Test Chit Fund')
        print(f"✅ Retrieved {len(history)} installment records")
        
    except Exception as e:
        print(f"❌ Data retrieval error: {e}")
        return False
    
    print("\n🎉 All tests passed successfully!")
    print(f"🗂️  Test data saved in spreadsheet: {test_spreadsheet_name}")
    print(f"🔗 You can view it at: {service.get_spreadsheet_url()}")
    print("\n📝 Note: You can delete the test spreadsheet if no longer needed.")
    
    return True


def main():
    """Main test function"""
    
    try:
        success = test_google_sheets_integration()
        
        if success:
            print("\n✅ Google Sheets integration is working correctly!")
            print("🚀 You can now run the main app: python run_sheets_app.py")
        else:
            print("\n❌ Google Sheets integration test failed!")
            print("📖 Please check the GOOGLE_SHEETS_SETUP.md guide for help.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test cancelled by user.")
    
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        print("📖 Please check your setup and try again.")


if __name__ == "__main__":
    main()