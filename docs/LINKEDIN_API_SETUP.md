# LinkedIn API Setup Guide

## Step 1: Create LinkedIn Developer App

1. Go to https://www.linkedin.com/developers/
2. Click **"Create App"**
3. Fill in the required details:
   - **App name**: Multi-Agent Workflow System
   - **LinkedIn Page**: Select your company page (or create one if needed)
   - **App logo**: Upload any logo image
   - **Legal agreement**: Check the box to agree
4. Click **"Create app"**

## Step 2: Configure OAuth Settings

1. In your app dashboard, go to the **"Auth"** tab
2. Under **"OAuth 2.0 settings"**, find **"Redirect URLs"**
3. Click **"Add redirect URL"**
4. Enter: `http://localhost:8080/callback`
5. Click **"Update"**

## Step 3: Request API Access

1. In your app dashboard, go to the **"Products"** tab
2. Request access to these products:
   - **Sign In with LinkedIn** (for basic profile access)
   - **Share on LinkedIn** (for posting updates)
   - **Marketing Developer Platform** (for advanced features - optional)

Note: Some products require verification and may take 1-2 business days for approval.

## Step 4: Get Your Credentials

1. Go back to the **"Auth"** tab
2. Copy your **Client ID**
3. Copy your **Client Secret** (click "Show" to reveal it)

## Step 5: Configure OAuth Setup Script

1. Open `linkedin_oauth_setup.py`
2. Replace these lines:
   ```python
   CLIENT_ID = "your-linkedin-client-id-here"
   CLIENT_SECRET = "your-linkedin-client-secret-here"
   ```
   With your actual credentials:
   ```python
   CLIENT_ID = "your-actual-client-id"
   CLIENT_SECRET = "your-actual-client-secret"
   ```

## Step 6: Run OAuth Flow

```bash
python linkedin_oauth_setup.py
```

This will:
- Open your browser for LinkedIn authorization
- Start a local server to receive the OAuth callback
- Exchange the authorization code for an access token
- Save the token to `.claude/mcp_config.json`

## Step 7: Test Connection

```bash
python .claude/skills/executor/linkedin_api.py
```

This will verify your LinkedIn API connection is working.

## Available API Scopes

The default scopes requested are:
- `r_liteprofile` - Read basic profile info
- `r_emailaddress` - Read email address
- `w_member_social` - Post, comment, and share on LinkedIn

## Troubleshooting

### "Invalid redirect_uri"
- Make sure you added `http://localhost:8080/callback` exactly in the Auth tab
- Check for typos or extra spaces

### "Insufficient permissions"
- Request the required Products in the Products tab
- Wait for approval if verification is needed

### "Access token expired"
- LinkedIn access tokens expire after 60 days
- Re-run `linkedin_oauth_setup.py` to get a new token

### "Product not approved"
- Some LinkedIn API products require manual approval
- You can still use basic features while waiting for approval
- Check your email for approval notifications

## Next Steps

Once setup is complete:
1. LinkedIn notifications will be automatically fetched
2. The system will create high-priority tasks in /Inbox
3. Approved LinkedIn posts/comments will be sent via the API
