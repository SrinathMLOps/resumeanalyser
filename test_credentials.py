"""
Test script to verify Azure credentials
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_document_intelligence():
    """Test Azure Document Intelligence credentials"""
    print("🧪 Testing Azure Document Intelligence credentials...")
    
    di_key = os.getenv("DI_KEY")
    di_endpoint = os.getenv("DI_ENDPOINT")
    
    if not di_key or not di_endpoint:
        print("❌ Missing DI_KEY or DI_ENDPOINT in .env file")
        return False
    
    print(f"📡 Endpoint: {di_endpoint}")
    print(f"🔑 Key: {di_key[:10]}...")
    
    # Test with a simple GET request to check if the endpoint is accessible
    endpoint = di_endpoint.rstrip('/')
    
    # Try different endpoints
    test_urls = [
        f"{endpoint}/documentintelligence/documentModels?api-version=2024-02-29-preview",
        f"{endpoint}/documentintelligence/documentModels?api-version=2023-07-31",
        f"{endpoint}/formrecognizer/documentModels?api-version=2022-08-31"
    ]
    
    headers = {
        "Ocp-Apim-Subscription-Key": di_key
    }
    
    for url in test_urls:
        print(f"\n🔄 Testing: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Success! Credentials are working.")
                return True
            elif response.status_code == 401:
                print("   ❌ Authentication failed - check your key")
            elif response.status_code == 404:
                print("   ⚠️  Endpoint not found - trying next...")
            else:
                print(f"   ⚠️  Unexpected response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
    
    return False

def test_openai():
    """Test Azure OpenAI credentials"""
    print("\n🧪 Testing Azure OpenAI credentials...")
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    if not api_key or not endpoint:
        print("❌ Missing AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT in .env file")
        return False
    
    print(f"📡 Endpoint: {endpoint}")
    print(f"🔑 Key: {api_key[:10]}...")
    
    # Test with deployments endpoint
    test_url = f"{endpoint}/openai/deployments?api-version=2024-02-15-preview"
    
    headers = {
        "api-key": api_key
    }
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! OpenAI credentials are working.")
            data = response.json()
            deployments = data.get('data', [])
            print(f"📋 Found {len(deployments)} deployments:")
            for dep in deployments:
                print(f"   - {dep.get('id', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - check your key")
        else:
            print(f"⚠️  Unexpected response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    return False

def main():
    print("🔍 Azure Credentials Test")
    print("=" * 50)
    
    di_ok = test_document_intelligence()
    openai_ok = test_openai()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Document Intelligence: {'✅ OK' if di_ok else '❌ FAILED'}")
    print(f"   OpenAI: {'✅ OK' if openai_ok else '❌ FAILED'}")
    
    if di_ok and openai_ok:
        print("\n🎉 All credentials are working! You can run the resume analyzer.")
    else:
        print("\n⚠️  Please fix the failed credentials before running the resume analyzer.")
        print("\nTroubleshooting tips:")
        print("1. Check your .env file has the correct keys and endpoints")
        print("2. Verify your Azure resources are active and not expired")
        print("3. Make sure you're using the correct region endpoints")

if __name__ == "__main__":
    main()