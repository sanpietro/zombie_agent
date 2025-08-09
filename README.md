# Azure AI Foundry Streamlit Agent

A production-ready Streamlit application that integrates with Azure AI Foundry agents.

## Features

✅ **Secure Authentication**: Uses Azure DefaultAzureCredential (Managed Identity)  
✅ **Error Handling**: Comprehensive error handling with retry logic  
✅ **Chat Interface**: Interactive chat with conversation history  
✅ **Session Management**: Maintains thread context across interactions  
✅ **Production Ready**: Logging, configuration management, and best practices  

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuration

You can configure the application in three ways (in order of preference):

#### Option A: Environment Variables (Recommended)
```bash
set AZURE_AI_FOUNDRY_ENDPOINT=https://your-foundry-endpoint.com/api/projects/your-project
set AZURE_AI_FOUNDRY_AGENT_ID=your-agent-id
```

#### Option B: Streamlit Secrets
Create `.streamlit/secrets.toml`:
```toml
AZURE_AI_FOUNDRY_ENDPOINT = "https://your-foundry-endpoint.com/api/projects/your-project"
AZURE_AI_FOUNDRY_AGENT_ID = "your-agent-id"
```

#### Option C: Default Values (Development Only)
The app will use the hardcoded values from your original code if no configuration is found.

### 3. Azure Authentication

Ensure you're authenticated with Azure:
```bash
az login
```

For production deployments, use Managed Identity or Service Principal.

## Running the Application

```bash
streamlit run app.py
```

## Features Explained

### 🔐 Secure Authentication
- Uses `DefaultAzureCredential` following Azure best practices
- No hardcoded credentials
- Supports multiple authentication methods (Managed Identity, Service Principal, etc.)

### 🔄 Error Handling & Retry Logic
- Exponential backoff for transient failures
- Comprehensive logging for debugging
- Graceful error messages for users

### 💬 Chat Interface
- Persistent conversation threads
- Message history within sessions
- Easy conversation reset

### 📊 Monitoring & Logging
- Structured logging for production monitoring
- Session state tracking
- Configuration display in sidebar

## Deployment

### Azure Container Instances (Recommended)
1. Build container with your app
2. Deploy to ACI with Managed Identity
3. Configure environment variables

### Azure App Service
1. Deploy code to App Service
2. Enable Managed Identity
3. Set application settings

## Troubleshooting

### Authentication Issues
- Ensure `az login` is successful
- Check that your account has access to the AI Foundry project
- Verify the endpoint URL and agent ID

### Connection Issues
- Check network connectivity
- Verify the AI Foundry endpoint is accessible
- Check Azure service health

### Performance Issues
- Monitor logs for retry patterns
- Check Azure AI Foundry service limits
- Consider implementing caching for frequently asked questions

## Architecture

```
User Input → Streamlit UI → AzureAIFoundryAgent → Azure AI Foundry → Agent Response
     ↑                            ↓
Session State ← Chat History ← Response Processing
```

## Security Considerations

- ✅ No hardcoded credentials
- ✅ Secure Azure authentication
- ✅ Error handling prevents information leakage
- ✅ Logging excludes sensitive data
- ✅ Configuration through secure channels

## Next Steps

1. **Add User Authentication**: Implement user-specific threads
2. **Persistent Storage**: Store chat history in Azure Cosmos DB
3. **Advanced Features**: File uploads, image processing
4. **Monitoring**: Application Insights integration
5. **Scaling**: Deploy to Azure Container Apps for auto-scaling
