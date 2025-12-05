# Google Sheets Integration Guide

## 🔐 Setting Up Google Sheets API Access

This guide will help you set up Google Sheets integration for the Chit Fund Analyzer application.

### Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create a New Project**
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter project name (e.g., "Chit Fund Analyzer")
   - Click "Create"

### Step 2: Enable Required APIs

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" → "Library"

2. **Enable Google Sheets API**
   - Search for "Google Sheets API"
   - Click on it and press "Enable"

3. **Enable Google Drive API**
   - Search for "Google Drive API"
   - Click on it and press "Enable"

### Step 3: Create Service Account

1. **Go to Service Accounts**
   - Click "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service account"

2. **Fill Service Account Details**
   - Service account name: `chit-fund-analyzer`
   - Service account ID: (auto-generated)
   - Description: `Service account for Chit Fund Analyzer app`
   - Click "Create and Continue"

3. **Skip Role Assignment** (for now)
   - Click "Continue" without adding roles
   - Click "Done"

### Step 4: Create and Download JSON Key

1. **Find Your Service Account**
   - In the "Credentials" page, find your service account
   - Click on the service account email

2. **Create JSON Key**
   - Go to the "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" format
   - Click "Create"

3. **Download and Save**
   - The JSON file will download automatically
   - Save it securely (don't commit to version control!)

### Step 5: Share Google Sheet with Service Account

1. **Create or Open Google Sheet**
   - Create a new Google Sheet or open existing one
   - Note the sheet name

2. **Share with Service Account**
   - Click "Share" button in Google Sheets
   - Add the service account email (from JSON file)
   - Grant "Editor" permissions
   - Click "Share"

### Step 6: Prepare JSON Credentials for App

1. **Open the Downloaded JSON File**
   - Open the JSON file in a text editor
   - Copy the entire content

2. **Use in Application**
   - When prompted in the app, paste the entire JSON content
   - The app will use these credentials to access your sheets

## 📊 JSON Credentials Format

Your JSON file should look like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
```

## 🔒 Security Best Practices

### For Individual Users:
- ✅ Keep JSON credentials secure and private
- ✅ Don't share credentials publicly
- ✅ Use specific sheet permissions
- ✅ Regularly review access

### For Organizations:
- ✅ Use separate Google Cloud projects for different environments
- ✅ Implement proper IAM roles and permissions
- ✅ Monitor API usage and costs
- ✅ Set up proper backup and recovery procedures

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**
   ```bash
   python run_sheets_app.py
   ```

3. **Authenticate**
   - Paste your JSON credentials in the app
   - Enter spreadsheet name
   - Click "Authenticate"

4. **Start Using**
   - Configure your first chit fund
   - Add installment history
   - Analyze your investments

## 🛠️ Troubleshooting

### Common Issues:

**1. Authentication Failed**
- ✅ Check JSON format is valid
- ✅ Ensure APIs are enabled in Google Cloud
- ✅ Verify service account has correct permissions

**2. Spreadsheet Access Denied**
- ✅ Share spreadsheet with service account email
- ✅ Grant "Editor" permissions
- ✅ Check spreadsheet name is correct

**3. Import Errors**
- ✅ Install all required packages: `pip install -r requirements.txt`
- ✅ Check Python version compatibility (3.8+)

**4. Connection Timeout**
- ✅ Check internet connection
- ✅ Verify firewall settings
- ✅ Try with different network

### Getting Help:

- 📖 Check the main [SETUP_GUIDE.md](SETUP_GUIDE.md) for general setup
- 🐛 Open GitHub issues for bugs
- 💡 Check Google Cloud Console for API quotas and limits
- 📧 Review Google Sheets API documentation

## 📈 Features

### Authentication Page:
- 🔐 Service account authentication
- 🧪 Connection testing
- 📊 Spreadsheet creation/access

### Configuration Page:
- 🏦 Chit fund setup
- 📅 Installment history input
- 💾 Auto-save to Google Sheets

### Analysis Page:
- 📈 IRR calculation
- 📊 Scenario analysis
- 💰 Cashflow visualization
- 📋 Historical data review

## 🔄 Data Structure

The app creates these worksheets in your Google Sheet:

### Chit_Configurations:
- Chit Name
- Chit Amount
- Total Months
- Monthly Installment
- Commission Rate
- Chit Method
- Created/Updated Dates
- Status
- Description

### Installment_History:
- Chit Name
- Month
- Installment Date
- Amount Paid
- Bid Amount
- Winner
- Commission
- Net Amount
- Payment Status
- Notes

### User_Profiles:
- User ID
- User Name
- Email/Phone
- Address
- Created Date
- Status

## 🎯 Next Steps

1. Set up Google Sheets API access using this guide
2. Run the application and authenticate
3. Create your first chit fund configuration
4. Start tracking and analyzing your investments
5. Use scenario analysis for investment planning

Happy investing! 💰