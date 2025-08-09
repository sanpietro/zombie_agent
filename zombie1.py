

import os
import logging
import streamlit as st
import time
from typing import List, Dict, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
from azure.core.exceptions import AzureError, ClientAuthenticationError, HttpResponseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.credential = DefaultAzureCredential()
        self.project_client = None
        self.agent = None
        self._initialize_client()
    
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
            raise
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
    
    def send_message(self, thread_id: str, message: str, max_retries: int = 3) -> Dict:
        """
        Send a message to the agent and get the response
        
        Args:
            thread_id: The conversation thread ID
            message: The user message
            max_retries: Maximum number of retry attempts
            
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
                        assistant_messages.append(msg.text_messages[-1].text.value)
                
                if assistant_messages:
                    return {"success": True, "response": assistant_messages[-1]}
                else:
                    return {"success": False, "error": "No response from assistant"}
                    
            except HttpResponseError as e:
                logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return {"success": False, "error": f"HTTP error after {max_retries} attempts: {e}"}
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return {"success": False, "error": f"Unexpected error: {e}"}
                time.sleep(2 ** attempt)
        
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

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Azure AI Foundry Agent Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Azure AI Foundry Agent Interface")
    st.markdown("Chat with your Azure AI Foundry agent powered by **The Zombinator**!")
    
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
            st.error(f"❌ Failed to initialize agent: {str(e)}")
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
                    error_msg = f"❌ Error: {response['error']}"
                    st.error(error_msg)
                    # Add error to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
    
    # Sidebar with configuration info
    with st.sidebar:
        st.header("🔧 Configuration")
        st.write("**Endpoint:**")
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
        - Responses are processed with retry logic for reliability
        """)

if __name__ == "__main__":
    main()
