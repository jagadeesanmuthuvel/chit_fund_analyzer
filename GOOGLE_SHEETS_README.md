# Chit Fund Analyzer - Google Sheets Integration

## 🆕 New Features

### 🔐 Google Sheets Authentication
- Secure service account authentication
- Connection testing and validation
- Support for multiple Google accounts

### 📊 Cloud Data Storage
- **Chit Fund Configurations**: Store all your chit fund details in the cloud
- **Installment History**: Track payments, bids, and winners automatically
- **Multi-Device Sync**: Access your data from any device with internet
- **Real-time Updates**: Changes are immediately saved to Google Sheets

### 🚀 Multi-Page Application
- **Authentication Page**: Connect to Google Sheets securely
- **Configuration Page**: Set up new chit funds and add installment data
- **Analysis Page**: Select and analyze any saved chit fund with full IRR calculations

### 🔄 App Versions Available

#### 1. Standard App (Local Storage)
- **File**: `streamlit_app.py`
- **Run**: `python run_app.py`
- **Features**: Full analysis capabilities with manual data input
- **Best for**: Quick analysis, offline use, privacy-focused users

#### 2. Google Sheets App (Cloud Storage)
- **File**: `app_with_sheets.py`
- **Run**: `python run_sheets_app.py`
- **Features**: Everything from standard app + cloud storage + data persistence
- **Best for**: Regular users, multiple devices, data backup needs

## 🚀 Quick Start

### For Google Sheets Integration:

1. **Setup Google Cloud API**:
   ```bash
   # Follow the guide
   see GOOGLE_SHEETS_SETUP.md
   ```

2. **Install and Test**:
   ```bash
   # Install dependencies
   uv sync  # or pip install -r requirements.txt
   
   # Test Google Sheets connection
   python test_sheets_integration.py
   ```

3. **Run the App**:
   ```bash
   # Start the Google Sheets integrated app
   python run_sheets_app.py
   ```

4. **Authenticate and Use**:
   - Paste your Google service account JSON credentials
   - Enter a spreadsheet name
   - Start configuring your chit funds!

## 📊 What Gets Stored in Google Sheets

### Chit_Configurations Worksheet:
- Chit Fund Name, Amount, Duration
- Monthly Installment, Commission Rate
- Chit Method (Auction/Lucky Draw/Fixed)
- Status, Creation Date, Description

### Installment_History Worksheet:
- Monthly payment records
- Bid amounts and winners
- Commission calculations
- Payment status and notes

### User_Profiles Worksheet:
- User information (future feature)
- Contact details and preferences

## 🔒 Security & Privacy

### Data Security:
- ✅ Service account authentication (recommended by Google)
- ✅ Encrypted API communication (HTTPS)
- ✅ No password storage in the app
- ✅ Credentials used only for session authentication

### Data Privacy:
- ✅ Your data stays in your Google account
- ✅ Only you control access permissions
- ✅ App doesn't store credentials permanently
- ✅ You can revoke access anytime via Google Cloud Console

## 💡 Use Cases

### Personal Use:
- Track your own chit fund investments
- Calculate optimal bidding strategies
- Monitor ROI across multiple chits
- Export data for tax purposes

### Family Use:
- Share chit fund data with family members
- Collaborative tracking of family chits
- Centralized record keeping
- Multi-device access for all members

### Financial Advisory:
- Manage multiple clients' chit funds
- Generate investment reports
- Track performance across portfolios
- Maintain detailed audit trails

## 🛠️ Technical Features

### Robust Error Handling:
- Connection timeout handling
- Invalid credential detection
- Data validation and correction
- User-friendly error messages

### Performance Optimization:
- Efficient Google Sheets API usage
- Cached data retrieval
- Minimal API calls
- Responsive UI updates

### Scalability:
- Support for multiple chit funds
- Unlimited installment history
- Batch data operations
- Future-proof architecture

## 📈 Analysis Capabilities

All the powerful analysis features from the original app:
- **IRR Calculation**: For any bid amount and winning month
- **Scenario Analysis**: Compare different bidding strategies
- **Cashflow Visualization**: Interactive charts and graphs
- **Investment Insights**: Automated recommendations
- **Export Options**: Download data as CSV/Excel

## 🔄 Migration from Standard App

If you're using the standard app and want to migrate to Google Sheets:

1. **Export your current data** (if any) from the standard app
2. **Set up Google Sheets integration** using the setup guide
3. **Re-enter your configurations** in the new app
4. **Continue using** with cloud storage benefits

## 🎯 Coming Soon

- OAuth authentication (alternative to service accounts)
- Advanced user management
- Multi-user collaboration features
- Automated email notifications
- Integration with banking APIs
- Mobile app companion

## 📞 Support

- 📖 **Setup Guide**: [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)
- 🔧 **General Setup**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 🧪 **Testing**: Run `python test_sheets_integration.py`
- 🐛 **Issues**: Open GitHub issues for bugs
- 💡 **Ideas**: Suggest features via GitHub discussions

---

**Ready to get started? Follow the [Google Sheets Setup Guide](GOOGLE_SHEETS_SETUP.md) and start tracking your chit fund investments in the cloud!** 🚀