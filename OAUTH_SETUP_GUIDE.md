# Google OAuth Setup Guide for Chit Fund Analyzer

## 🔐 Google OAuth Authentication

OAuth authentication allows you to use your personal Google account to access and create spreadsheets directly in your Google Drive. This is easier than service accounts for personal use.

## 🆚 OAuth vs Service Account

### Google OAuth (Personal Account):
- ✅ **Easy Setup**: Use your personal Google account
- ✅ **Direct Access**: Create files in your Google Drive
- ✅ **No Sharing Required**: Automatic access to your spreadsheets
- ✅ **User-Friendly**: Familiar Google login flow
- ⚠️ **Personal Use**: Best for individual users

### Service Account:
- ✅ **Organization Use**: Better for teams/organizations
- ✅ **Programmatic Access**: Doesn't require user interaction
- ✅ **Security**: Isolated permissions
- ⚠️ **Complex Setup**: Requires manual spreadsheet sharing

## 🛠️ OAuth Setup Instructions

### Step 1: Create OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Select/Create Project**
   - Use your existing project or create a new one
   - Project name: "Chit Fund Analyzer" (or any name you prefer)

3. **Enable Required APIs**
   - Go to "APIs & Services" → "Library"
   - Search and enable "Google Sheets API"
   - Search and enable "Google Drive API"

### Step 2: Create OAuth 2.0 Client ID

1. **Go to Credentials**
   - Navigate to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"

2. **Configure OAuth Consent Screen** (if prompted)
   - User type: "External" (unless you have a workspace)
   - App name: "Chit Fund Analyzer"
   - User support email: Your email
   - Developer contact: Your email
   - Save and continue through the steps

3. **Create OAuth Client**
   - Application type: **"Desktop application"**
   - Name: "Chit Fund Analyzer OAuth"
   - Click "Create"

4. **Download Credentials**
   - Click "Download JSON" for your OAuth client
   - Save the file securely

### Step 3: Use in Application

1. **Open the JSON file** you downloaded
2. **Copy the entire contents**
3. **In the app**, select "Google OAuth (Personal Account)"
4. **Paste the JSON** in the credentials field
5. **Follow the OAuth flow** in the app

## 📋 JSON Format Example

Your OAuth credentials JSON should look like this:

```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob","http://localhost"]
  }
}
```

**Note**: The key can also be `"web"` instead of `"installed"` depending on the application type you chose.

## 🔄 OAuth Authentication Flow

### In the App:

1. **Select OAuth Method**: Choose "Google OAuth (Personal Account)"
2. **Paste Credentials**: Enter your OAuth JSON credentials
3. **Start OAuth Flow**: Click "Start OAuth Flow"
4. **Authorize**: Click the generated authorization link
5. **Sign In**: Use your Google account to sign in
6. **Grant Permissions**: Allow access to Google Sheets and Drive
7. **Copy Code**: Copy the authorization code provided
8. **Complete**: Paste the code back in the app

### What Happens:
- ✅ You'll be redirected to Google's authorization page
- ✅ Grant permissions to access your Google Sheets and Drive
- ✅ Google provides an authorization code
- ✅ App exchanges code for access tokens
- ✅ Direct access to your Google Drive

## 🎯 Benefits of OAuth

### For Users:
- **No Manual Sharing**: Spreadsheets are automatically accessible
- **Your Google Drive**: Files created in your personal Drive
- **Familiar Process**: Standard Google login you're used to
- **Full Control**: You control permissions through your Google account

### For the App:
- **Direct File Creation**: Can create spreadsheets in your Drive
- **No Quota Issues**: Uses your personal Drive storage
- **Real-time Access**: Immediate access to your files

## 🔒 Security Considerations

### What the App Can Access:
- ✅ **Google Sheets**: Read, write, create spreadsheets
- ✅ **Google Drive**: Create files in your Drive
- ❌ **Other Data**: No access to emails, photos, or other services

### Security Best Practices:
- ✅ **Review Permissions**: Check what you're granting access to
- ✅ **Revoke Access**: You can revoke access anytime in your Google account
- ✅ **Secure Credentials**: Keep your OAuth JSON file secure
- ✅ **Regular Review**: Periodically review connected apps in Google account

## 🚀 Quick Start with OAuth

### For New Users:
```bash
# 1. Set up OAuth credentials (follow guide above)
# 2. Start the app
python run_sheets_app.py

# 3. In the app:
# - Select "Google OAuth (Personal Account)"
# - Paste your OAuth JSON credentials
# - Follow the authentication flow
# - Start using!
```

### Migration from Service Account:
If you're already using service accounts and want to switch:

1. **Export Data**: Download your data as CSV from existing sheets
2. **Set Up OAuth**: Follow this guide to create OAuth credentials
3. **Re-authenticate**: Use OAuth method in the app
4. **Import Data**: Re-enter or import your configurations

## 🛠️ Troubleshooting OAuth

### Common Issues:

**1. "Error 400: redirect_uri_mismatch"**
- ✅ Ensure you selected "Desktop application" type
- ✅ Check that redirect URIs include `urn:ietf:wg:oauth:2.0:oob`

**2. "Access blocked: authorization_error"**
- ✅ Complete the OAuth consent screen configuration
- ✅ Add your email to test users if app is in testing mode

**3. "Invalid authorization code"**
- ✅ Copy the entire code without extra spaces
- ✅ Use the code immediately (they expire quickly)
- ✅ Generate a new code if needed

**4. "Insufficient permissions"**
- ✅ Ensure Google Sheets and Drive APIs are enabled
- ✅ Check OAuth scopes include necessary permissions

### Getting Help:
- 📖 Check Google's [OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)
- 🔧 Review your Google Cloud Console setup
- 📞 Open GitHub issues for app-specific problems

## 🎉 Ready to Go!

With OAuth set up, you can:
- ✅ **Create spreadsheets** directly in your Google Drive
- ✅ **Access all your sheets** without manual sharing
- ✅ **Use familiar Google authentication**
- ✅ **Enjoy seamless integration** with your Google account

**Start using OAuth authentication now**: http://localhost:8507

Choose "Google OAuth (Personal Account)" and follow the flow! 🚀