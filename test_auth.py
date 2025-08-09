#!/usr/bin/env python3
"""
Azure Authentication Test Script
Run this to diagnose authentication issues
"""

import os
import sys

def test_azure_auth():
    print("🔍 Testing Azure Authentication...")
    print("=" * 50)
    
    # Test 1: Check Azure CLI
    print("\n1. Testing Azure CLI...")
    try:
        import subprocess
        result = subprocess.run(['az', 'account', 'show'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Azure CLI: Authenticated")
            print(f"   Account: {result.stdout[:100]}...")
        else:
            print("❌ Azure CLI: Not authenticated")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Azure CLI: Not available - {e}")
    
    # Test 2: Test DefaultAzureCredential
    print("\n2. Testing DefaultAzureCredential...")
    try:
        from azure.identity import DefaultAzureCredential
        credential = DefaultAzureCredential()
        
        # Try to get a token
        token = credential.get_token("https://management.azure.com/.default")
        print("✅ DefaultAzureCredential: Working")
        print(f"   Token type: {type(token)}")
    except Exception as e:
        print(f"❌ DefaultAzureCredential: Failed - {e}")
    
    # Test 3: Check environment variables
    print("\n3. Checking Environment Variables...")
    env_vars = [
        'AZURE_CLIENT_ID',
        'AZURE_CLIENT_SECRET', 
        'AZURE_TENANT_ID',
        'AZURE_SUBSCRIPTION_ID'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set (length: {len(value)})")
        else:
            print(f"❌ {var}: Not set")
    
    # Test 4: Test AI Foundry connection
    print("\n4. Testing Azure AI Foundry Connection...")
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        
        endpoint = "https://azureaiserviceshubdemo.services.ai.azure.com/api/projects/azureaiserviceshubdemo-project"
        
        credential = DefaultAzureCredential()
        client = AIProjectClient(credential=credential, endpoint=endpoint)
        
        print("✅ AI Foundry Client: Created successfully")
        
        # Try to get the agent
        agent_id = "asst_Mlew8M6WPiUMrQlPgEg5ZRMo"
        agent = client.agents.get_agent(agent_id)
        print(f"✅ Agent Retrieved: {agent.id}")
        
    except Exception as e:
        print(f"❌ AI Foundry Connection: Failed - {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Authentication Test Complete")

if __name__ == "__main__":
    test_azure_auth()
