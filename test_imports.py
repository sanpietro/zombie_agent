#!/usr/bin/env python3
"""
Test script to verify Azure AI Projects installation and imports
"""

try:
    print("Testing imports...")
    
    # Test core imports
    import azure.ai.projects
    print("✅ azure.ai.projects imported successfully")
    
    import azure.identity
    print("✅ azure.identity imported successfully")
    
    import streamlit as st
    print("✅ streamlit imported successfully")
    
    # Test specific classes
    from azure.ai.projects import AIProjectClient
    print("✅ AIProjectClient imported successfully")
    
    from azure.identity import DefaultAzureCredential
    print("✅ DefaultAzureCredential imported successfully")
    
    from azure.ai.agents.models import ListSortOrder
    print("✅ ListSortOrder imported successfully")
    
    print("\n🎉 All imports successful! Your environment is ready.")
    print("\nTo run the Streamlit app:")
    print("streamlit run app.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTry installing the missing packages with:")
    print("pip install azure-ai-projects azure-identity streamlit azure-core")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
