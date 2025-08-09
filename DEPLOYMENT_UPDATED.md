# Streamlit Cloud Deployment Guide

## Prerequisites
You've now updated your app to support both local development and cloud deployment with proper Azure authentication.

## Deployment Steps

### 1. Push Your Code to GitHub
Make sure your latest changes are committed and pushed:

```bash
git add .
git commit -m "Add service principal authentication for cloud deployment"
git push origin main
```

### 2. Configure Streamlit Cloud Secrets
In your Streamlit Cloud app settings, add these secrets:

```toml
AZURE_AI_FOUNDRY_ENDPOINT = "https://azureaiserviceshubdemo.services.ai.azure.com/api/projects/azureaiserviceshubdemo-project"
AZURE_AI_FOUNDRY_AGENT_ID = "asst_Mlew8M6WPiUMrQlPgEg5ZRMo"

# Azure Service Principal for Cloud Authentication  
AZURE_CLIENT_ID = "0c449aa6-2dc1-4946-8278-ce748769d7fc"
AZURE_CLIENT_SECRET = "EeN8Q~Nn2EUeSrRx~n5na7n4MrU03H9zEVSHVcvP" 
AZURE_TENANT_ID = "603f70f9-1661-464b-b868-585fe260812a"
```

### 3. Deploy on Streamlit Cloud
1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Click "New app"
3. Connect your GitHub repository: `zombie_agent`
4. Set main file path: `app.py`
5. Click "Deploy!"

## Authentication Flow

### Local Development
- Uses `DefaultAzureCredential` (Azure CLI login)
- Falls back to `InteractiveBrowserCredential` if needed

### Cloud Deployment  
- Uses `ClientSecretCredential` with service principal
- Automatically detects cloud environment
- More secure and reliable for production

## Service Principal Details
- **Name**: streamlit-zombinator-app
- **Role**: Cognitive Services User  
- **Scope**: Your Azure subscription
- **App ID**: 0c449aa6-2dc1-4946-8278-ce748769d7fc

## Troubleshooting

### If deployment fails with authentication errors:
1. Verify all secrets are correctly set in Streamlit Cloud
2. Check that service principal has proper permissions
3. Ensure your AI Foundry project is accessible

### If you need to recreate the service principal:
```bash
az ad sp create-for-rbac --name "streamlit-zombinator-app-v2" --role "Cognitive Services User" --scopes "/subscriptions/0984f555-fee3-41c5-8497-7e1f7f82f19c"
```

### Common issues:
- **403 Forbidden**: Service principal lacks permissions
- **401 Unauthorized**: Wrong client secret or tenant ID
- **Connection timeout**: Network or endpoint issues

## Testing Locally
The app now supports both authentication methods, so you can test locally with:
```bash
conda activate zombinator
streamlit run app.py
```

The app will automatically detect your environment and use the appropriate authentication method.
