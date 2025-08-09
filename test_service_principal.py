#!/usr/bin/env python3
"""
Test script to verify service principal authentication works
"""

import os
import sys
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient

# Service Principal credentials
CLIENT_ID = "0c449aa6-2dc1-4946-8278-ce748769d7fc"
CLIENT_SECRET = "EeN8Q~Nn2EUeSrRx~n5na7n4MrU03H9zEVSHVcvP"
TENANT_ID = "603f70f9-1661-464b-b868-585fe260812a"

# AI Foundry settings
ENDPOINT = "https://azureaiserviceshubdemo.services.ai.azure.com/api/projects/azureaiserviceshubdemo-project"
AGENT_ID = "asst_Mlew8M6WPiUMrQlPgEg5ZRMo"

def test_service_principal_auth():
    """Test service principal authentication"""
    try:
        print("🔐 Testing service principal authentication...")
        
        # Create credential
        credential = ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        
        # Test token acquisition
        print("🎟️ Getting token...")
        token = credential.get_token("https://management.azure.com/.default")
        print(f"✅ Token acquired successfully! (expires: {token.expires_on})")
        
        # Test AI Foundry connection
        print("🤖 Testing AI Foundry connection...")
        project_client = AIProjectClient(
            credential=credential,
            endpoint=ENDPOINT
        )
        
        # Get agent
        print("🎭 Getting agent...")
        agent = project_client.agents.get_agent(AGENT_ID)
        print(f"✅ Agent retrieved: {agent.id}")
        print(f"   Name: {agent.name}")
        print(f"   Model: {agent.model}")
        
        # Create a test thread
        print("💬 Creating test thread...")
        thread = project_client.agents.threads.create()
        print(f"✅ Thread created: {thread.id}")
        
        print("\n🎉 All tests passed! Service principal authentication is working.")
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_service_principal_auth()
    sys.exit(0 if success else 1)
