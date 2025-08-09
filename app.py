import os
import logging
import streamlit as st
import time
import re
from typing import List, Dict, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
from azure.core.exceptions import AzureError, ClientAuthenticationError, HttpResponseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_response(response_text: str) -> str:
    """
    Clean up the response text by removing metadata tags and citations
    
    Args:
        response_text (str): Raw response from the agent
        
    Returns:
        str: Cleaned response text
    """
    if not response_text:
        return response_text
    
    # Remove citation patterns like 【message_idx:search_idx†source】
    response_text = re.sub(r'【[^】]*】', '', response_text)
    
    # Remove other common metadata patterns
    response_text = re.sub(r'\[citation:\d+\]', '', response_text)
    response_text = re.sub(r'\[source:\d+\]', '', response_text)
    response_text = re.sub(r'\[ref:\d+\]', '', response_text)
    
    # Clean up extra whitespace
    response_text = re.sub(r'\s+', ' ', response_text).strip()
    
    return response_text

class AzureAIFoundryAgent:
    """Azure AI Foundry Agent client with error handling and retry logic"""
    
    def __init__(self, endpoint: str, agent_id: str):
        """
        Initialize the Azure AI Foundry Agent client
        
        Args:
            endpoint: The AI Foundry project endpoint URL
            agent_id: The specific agent ID to use
        """
        self.endpoint = endpoint
        self.agent_id = agent_id
        self.credential = self._get_credential()
        self.project_client = None
        self.agent = None
        self._initialize_client()
    
    def _get_credential(self):
        """Get Azure credential with support for both local and cloud deployment"""
        try:
            # Check if we're in Streamlit Cloud (or other cloud environment)
            # Look for service principal credentials first (for cloud deployment)
            client_id = os.getenv('AZURE_CLIENT_ID') or st.secrets.get('AZURE_CLIENT_ID')
            client_secret = os.getenv('AZURE_CLIENT_SECRET') or st.secrets.get('AZURE_CLIENT_SECRET')
            tenant_id = os.getenv('AZURE_TENANT_ID') or st.secrets.get('AZURE_TENANT_ID')
            
            if client_id and client_secret and tenant_id:
                logger.info("Using service principal authentication for cloud deployment")
                from azure.identity import ClientSecretCredential
                credential = ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
                # Test the credential
                try:
                    credential.get_token("https://management.azure.com/.default")
                    logger.info("Service principal authentication successful")
                    return credential
                except Exception as e:
                    logger.error(f"Service principal authentication failed: {e}")
                    raise
            
            # If no service principal, try DefaultAzureCredential for local development
            logger.info("Trying DefaultAzureCredential for local development")
            from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
            credential = DefaultAzureCredential()
            
            # Test the credential by attempting to get a token
            try:
                credential.get_token("https://management.azure.com/.default")
                logger.info("DefaultAzureCredential authentication successful")
                return credential
            except Exception as e:
                logger.warning(f"DefaultAzureCredential failed: {e}")
                
                # Fallback to Interactive Browser Authentication (local only)
                if not self._is_cloud_environment():
                    logger.info("Trying InteractiveBrowserCredential...")
                    try:
                        interactive_credential = InteractiveBrowserCredential()
                        interactive_credential.get_token("https://management.azure.com/.default")
                        logger.info("InteractiveBrowserCredential authentication successful")
                        return interactive_credential
                    except Exception as ie:
                        logger.error(f"InteractiveBrowserCredential also failed: {ie}")
                else:
                    logger.error("Running in cloud environment but no service principal configured")
                    
                raise e  # Raise the original DefaultAzureCredential error
                
        except Exception as e:
            logger.error(f"Authentication setup failed: {e}")
            raise Exception(f"Azure authentication failed. For cloud deployment, configure AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID. For local development, run 'az login'. Error: {e}")
    
    def _is_cloud_environment(self):
        """Check if running in a cloud environment"""
        # Common indicators of cloud environments
        cloud_indicators = [
            os.getenv('STREAMLIT_SHARING'),  # Streamlit Cloud
            os.getenv('HEROKU_APP_NAME'),    # Heroku
            os.getenv('VERCEL'),             # Vercel
            os.getenv('NETLIFY'),            # Netlify
            os.getenv('AWS_LAMBDA_FUNCTION_NAME'),  # AWS Lambda
        ]
        return any(cloud_indicators) or 'streamlit.io' in os.getenv('HOSTNAME', '')
    
    def _initialize_client(self):
        """Initialize the AI project client and get the agent"""
        try:
            self.project_client = AIProjectClient(
                credential=self.credential,
                endpoint=self.endpoint
            )
            self.agent = self.project_client.agents.get_agent(self.agent_id)
            logger.info(f"Successfully initialized agent: {self.agent_id}")
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise Exception(f"Azure authentication failed. Please run 'az login' in your terminal or check your Azure credentials. Error: {e}")
        except HttpResponseError as e:
            logger.error(f"HTTP error during initialization: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {e}")
            raise
    
    def create_thread(self) -> str:
        """
        Create a new conversation thread
        
        Returns:
            str: The thread ID
        """
        try:
            thread = self.project_client.agents.threads.create()
            logger.info(f"Created thread: {thread.id}")
            return thread.id
        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            raise
    
    def send_message(self, thread_id: str, message: str, max_retries: int = 2) -> Dict:
        """
        Send a message to the agent and get the response
        
        Args:
            thread_id: The conversation thread ID
            message: The user message
            max_retries: Maximum number of retry attempts (reduced to prevent loops)
            
        Returns:
            Dict: Response containing success status and message/error
        """
        for attempt in range(max_retries):
            try:
                # Create user message
                self.project_client.agents.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=message
                )
                
                # Create and process the run
                run = self.project_client.agents.runs.create_and_process(
                    thread_id=thread_id,
                    agent_id=self.agent.id
                )
                
                # Check run status
                if run.status == "failed":
                    error_msg = f"Run failed: {run.last_error}"
                    logger.error(error_msg)
                    
                    # Check if it's a rate limit error
                    if isinstance(run.last_error, dict) and run.last_error.get('code') == 'rate_limit_exceeded':
                        # Extract retry time from error message
                        error_message = run.last_error.get('message', '')
                        retry_seconds = min(10, 7)  # Cap at 10 seconds max
                        
                        # Try to extract the retry time from message
                        match = re.search(r'Try again in (\d+) seconds?', error_message)
                        if match:
                            retry_seconds = min(int(match.group(1)), 10)  # Cap at 10 seconds
                        
                        logger.warning(f"Rate limit exceeded (attempt {attempt + 1}/{max_retries}), retrying in {retry_seconds} seconds...")
                        
                        # If this isn't the last retry, wait and continue
                        if attempt < max_retries - 1:
                            time.sleep(retry_seconds)
                            continue
                        else:
                            # On final attempt, return a user-friendly rate limit message
                            return {
                                "success": False, 
                                "error": "rate_limit_exceeded",
                                "user_message": f"The Zombinator is currently overloaded. Please try again in {retry_seconds} seconds."
                            }
                    
                    return {"success": False, "error": error_msg}
                
                # Get the response messages
                messages = self.project_client.agents.messages.list(
                    thread_id=thread_id, 
                    order=ListSortOrder.ASCENDING
                )
                
                # Extract the latest assistant message
                assistant_messages = []
                for msg in messages:
                    if msg.role == "assistant" and msg.text_messages:
                        raw_message = msg.text_messages[-1].text.value
                        # Clean the message to remove metadata
                        cleaned_message = clean_response(raw_message)
                        assistant_messages.append(cleaned_message)
                
                if assistant_messages:
                    return {"success": True, "response": assistant_messages[-1]}
                else:
                    return {"success": False, "error": "No response from assistant"}
                    
            except HttpResponseError as e:
                logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return {"success": False, "error": f"HTTP error after {max_retries} attempts: {e}"}
                time.sleep(min(2 ** attempt, 5))  # Exponential backoff with cap
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return {"success": False, "error": f"Unexpected error: {e}"}
                time.sleep(min(2 ** attempt, 5))  # Exponential backoff with cap
        
        return {"success": False, "error": "Max retries exceeded"}

def get_config() -> Dict[str, str]:
    """
    Get configuration from environment variables or Streamlit secrets
    
    Returns:
        Dict containing endpoint and agent_id
    """
    config = {}
    
    # Try to get from environment variables first
    config["endpoint"] = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
    config["agent_id"] = os.getenv("AZURE_AI_FOUNDRY_AGENT_ID")
    
    # Fallback to Streamlit secrets
    if not config["endpoint"] and hasattr(st, 'secrets'):
        config["endpoint"] = st.secrets.get("AZURE_AI_FOUNDRY_ENDPOINT")
        config["agent_id"] = st.secrets.get("AZURE_AI_FOUNDRY_AGENT_ID")
    
    # Fallback to hardcoded values (for development only)
    if not config["endpoint"]:
        config["endpoint"] = "https://azureaiserviceshubdemo.services.ai.azure.com/api/projects/azureaiserviceshubdemo-project"
    if not config["agent_id"]:
        config["agent_id"] = "asst_Mlew8M6WPiUMrQlPgEg5ZRMo"
    
    return config

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "agent_client" not in st.session_state:
        st.session_state.agent_client = None
    if "processing" not in st.session_state:
        st.session_state.processing = False

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Azure AI Foundry Agent Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Welcome to the Zombie Survival Service!")
    st.markdown("🧟 Your undead lifeline, 24/7.")
    
    # Initialize session state
    initialize_session_state()
    
    # Get configuration
    config = get_config()
    
    # Initialize agent client if not already done
    if st.session_state.agent_client is None:
        try:
            with st.spinner("Initializing Azure AI Foundry Agent..."):
                st.session_state.agent_client = AzureAIFoundryAgent(
                    endpoint=config["endpoint"],
                    agent_id=config["agent_id"]
                )
                st.success("✅ Agent initialized successfully!")
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Failed to initialize agent: {error_msg}")
            
            # Provide specific guidance based on the error
            if "authentication" in error_msg.lower() or "defaultazurecredential" in error_msg.lower():
                st.info("🔧 **Authentication Setup Required:**")
                st.markdown("""
                **To fix this issue, run one of these commands in your terminal:**
                
                ```bash
                # Option 1: Azure CLI (Recommended)
                az login
                
                # Option 2: Azure Developer CLI
                azd auth login
                ```
                
                **Or install the required packages:**
                ```bash
                pip install azure-identity-broker
                ```
                
                **Then restart your Streamlit app.**
                """)
            
            st.info("Please check your Azure credentials and configuration.")
            st.stop()
    
    # Create new thread button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🆕 New Conversation"):
            try:
                thread_id = st.session_state.agent_client.create_thread()
                st.session_state.thread_id = thread_id
                st.session_state.messages = []
                st.success("Started new conversation!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create new conversation: {str(e)}")
    
    # Display current thread ID
    with col2:
        if st.session_state.thread_id:
            st.info(f"💬 Thread ID: {st.session_state.thread_id[:20]}...")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to ask The Zombinator?"):
        # Create thread if it doesn't exist
        if st.session_state.thread_id is None:
            try:
                with st.spinner("Creating conversation thread..."):
                    thread_id = st.session_state.agent_client.create_thread()
                    st.session_state.thread_id = thread_id
            except Exception as e:
                st.error(f"Failed to create conversation thread: {str(e)}")
                st.stop()
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("The Zombinator is thinking..."):
                response = st.session_state.agent_client.send_message(
                    thread_id=st.session_state.thread_id,
                    message=prompt
                )
                
                if response["success"]:
                    st.markdown(response["response"])
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response["response"]
                    })
                else:
                    error_msg = response["error"]
                    
                    # Check if it's a rate limit error for user-friendly message
                    if response.get("user_message"):
                        # Use the user-friendly message from rate limiting
                        st.warning(f"🕐 {response['user_message']}")
                        st.info("💡 Tip: Try refreshing the page or starting a new conversation if the issue persists.")
                        # Add user-friendly message to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"🕐 {response['user_message']}"
                        })
                    elif "rate_limit_exceeded" in error_msg or "Rate limit is exceeded" in error_msg:
                        friendly_msg = "🕐 The Zombinator is experiencing high demand. Please wait a moment and try again."
                        st.warning(friendly_msg)
                        st.info("💡 Tip: Azure AI services have rate limits to ensure fair usage. Your request will be processed shortly.")
                        # Add user-friendly message to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": friendly_msg
                        })
                    else:
                        st.error(f"❌ Error: {error_msg}")
                        # Add error to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"❌ Error: {error_msg}"
                        })
    
    # Sidebar with configuration info
    with st.sidebar:
        st.header("🔧 Configuration")
        st.write("**AI Foundry Endpoint:**")
        st.code(config["endpoint"][:50] + "..." if len(config["endpoint"]) > 50 else config["endpoint"])
        st.write("**Agent ID:**")
        st.code(config["agent_id"])
        
        st.header("📊 Session Info")
        st.write(f"**Messages:** {len(st.session_state.messages)}")
        st.write(f"**Thread Active:** {'✅' if st.session_state.thread_id else '❌'}")
        
        st.header("💡 Tips")
        st.markdown("""
        - Click "New Conversation" to start fresh
        - Your conversation history is maintained per session
        - The agent uses Azure AI Foundry's capabilities
        - External APIs (Maps, Weather) are handled by the agent
        - Responses are processed with retry logic for reliability
        """)

if __name__ == "__main__":
    main()
