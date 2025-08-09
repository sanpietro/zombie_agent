# Streamlit Cloud Deployment Guide

## 🚀 Deploying Your Azure AI Foundry Streamlit App

### Step 1: Prepare Your Repository
✅ Your repo is already prepared with:
- `.gitignore` to exclude sensitive files
- `.env.template` with placeholder values
- `.streamlit/secrets.toml` (excluded from git)

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Click "New app"**
3. **Connect your GitHub repository**: `sanpietro/zombie_agent`
4. **Set the main file path**: `app.py`
5. **Click "Deploy!"**

### Step 3: Configure Secrets in Streamlit Cloud

After deployment, you only need to add your Azure AI Foundry credentials:

1. **Go to your app dashboard** on share.streamlit.io
2. **Click the "⚙️ Settings" button** (gear icon)
3. **Navigate to "Secrets" tab**
4. **Add the following secrets** in TOML format:

```toml
# Required for Azure AI Foundry Agent
AZURE_AI_FOUNDRY_ENDPOINT = "https://azureaiserviceshubdemo.services.ai.azure.com/api/projects/azureaiserviceshubdemo-project"
AZURE_AI_FOUNDRY_AGENT_ID = "asst_Mlew8M6WPiUMrQlPgEg5ZRMo"
```

**Note**: Azure Maps, Weather APIs, and other external services are handled within your Azure AI Foundry agent service, so you don't need to provide those credentials to Streamlit.

### Step 4: Verify Configuration

**IMPORTANT**: Your Azure AI Foundry agent should already have the external API credentials configured:

1. **Azure Maps API** - Configured in your Foundry agent's connected resources
2. **OpenWeatherMap API** - Handled by your agent's tools and functions
3. **Other external services** - Managed within the agent service

You only need to provide the **agent endpoint** and **agent ID** to Streamlit.

### Step 5: Save and Restart

1. **Click "Save"** in the Secrets tab
2. **Your app will automatically restart** with the new configuration
3. **Test the deployment** to ensure everything works

## 🔐 Security Best Practices

### ✅ What's Secure:
- Secrets are encrypted in Streamlit Cloud
- `.env` file is excluded from git
- API keys are not visible in your code

### 🚨 Remember to:
- **Rotate your Azure Maps key** (since it was exposed earlier)
- **Never commit secrets to git**
- **Use environment-specific keys** (dev/prod)

## 🛠️ Alternative Deployment Methods

### Azure Container Instances
```bash
# Build and deploy to Azure
docker build -t zombie-agent .
az container create --resource-group your-rg --name zombie-agent --image zombie-agent
```

### Azure App Service
```bash
# Deploy directly to Azure App Service
az webapp up --name zombie-agent --sku B1
```

## 🔧 Environment Variables Reference

Your app supports multiple configuration methods (in priority order):

1. **Environment Variables** (highest priority)
2. **Streamlit Secrets** (recommended for cloud deployment)  
3. **Hardcoded defaults** (development only)

### Required Variables:
- `AZURE_AI_FOUNDRY_ENDPOINT` - Your AI Foundry project endpoint
- `AZURE_AI_FOUNDRY_AGENT_ID` - Your Zombinator agent ID

**Note**: External API credentials (Azure Maps, Weather APIs, etc.) are managed within your Azure AI Foundry agent service and don't need to be provided to the Streamlit app.

## 🏃‍♂️ Quick Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] Secrets configured in Streamlit Cloud
- [ ] Azure Maps key rotated (security)
- [ ] App deployed and tested
- [ ] Error handling verified
- [ ] Rate limiting working correctly

## 🆘 Troubleshooting

### Common Issues:
1. **"Secrets not found"** → Check secrets.toml format in Streamlit Cloud
2. **"Authentication failed"** → Verify Azure credentials and key rotation
3. **"Rate limit exceeded"** → Your app handles this gracefully now
4. **"Module not found"** → Check requirements.txt is complete

### Logs:
- Check Streamlit Cloud logs in the app dashboard
- Look for authentication and API call errors
- Monitor Azure billing for unexpected usage
