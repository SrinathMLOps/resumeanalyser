"""
Test script for Azure Document Intelligence SDK
Based on the reference code provided
"""

import os
import numpy as np
from dotenv import load_dotenv

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import ContentFormat
    SDK_AVAILABLE = True
except ImportError as e:
    SDK_AVAILABLE = False
    print(f"❌ Azure Document Intelligence SDK not available: {e}")
    print("Please install: pip install azure-ai-documentintelligence azure-core numpy")

# Load environment variables
load_dotenv()

def format_bounding_box(bounding_box):
    """Format bounding box coordinates for display"""
    if not bounding_box:
        return "N/A"
    reshaped_bounding_box = np.array(bounding_box).reshape(-1, 2)
    return ", ".join(["[{}, {}]".format(x, y) for x, y in reshaped_bounding_box])

def analyze_read_from_file(pdf_path: str):
    """Analyze document using Azure Document Intelligence SDK - file version"""
    if not SDK_AVAILABLE:
        print("❌ SDK not available")
        return
    
    # Get credentials from environment
    endpoint = os.getenv("DI_ENDPOINT")
    key = os.getenv("DI_KEY")
    
    if not endpoint or not key:
        print("❌ Missing Azure Document Intelligence credentials in .env file")
        return
    
    print(f"📄 Analyzing document: {pdf_path}")
    print(f"🔗 Endpoint: {endpoint}")
    print(f"🔑 Key: {key[:10]}...")
    
    try:
        # Initialize client
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        
        # Read PDF file
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        
        # Analyze document using correct API
        poller = document_intelligence_client.begin_analyze_document(
            model_id="prebuilt-read",
            analyze_request=pdf_data,
            content_type="application/pdf"
        )
        
        print("🔄 Processing document...")
        result = poller.result()
        
        print(f"📝 Document contains content: {len(result.content)} characters")
        print(f"📄 First 200 characters: {result.content[:200]}...")
        
        # Check for handwritten content
        if hasattr(result, 'styles') and result.styles:
            for idx, style in enumerate(result.styles):
                print(f"📝 Document contains {('handwritten' if style.is_handwritten else 'no handwritten')} content")
        
        # Analyze pages
        if hasattr(result, 'pages') and result.pages:
            for page in result.pages:
                print(f"\n----Analyzing Read from page #{page.page_number}----")
                print(f"📄 Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}")
                
                # Analyze lines
                if hasattr(page, 'lines') and page.lines:
                    print(f"📝 Found {len(page.lines)} lines")
                    for line_idx, line in enumerate(page.lines[:3]):  # Show first 3 lines
                        print(f"   Line #{line_idx} has text content '{line.content}' within bounding box '{format_bounding_box(line.polygon)}'")
                
                # Analyze words
                if hasattr(page, 'words') and page.words:
                    print(f"🔤 Found {len(page.words)} words")
                    high_confidence_words = [word for word in page.words if word.confidence and word.confidence > 0.9]
                    print(f"✅ {len(high_confidence_words)} words with >90% confidence")
                    
                    # Show a few example words
                    for word in page.words[:5]:  # Show first 5 words
                        if word.confidence:
                            print(f"   Word '{word.content}' has confidence of {word.confidence:.2%}")
                
                print("----------------------------------------")
        
        return result.content
        
    except Exception as e:
        print(f"❌ Error analyzing document: {str(e)}")
        return None

def analyze_read_from_url():
    """Analyze document using Azure Document Intelligence SDK - URL version (from reference)"""
    if not SDK_AVAILABLE:
        print("❌ SDK not available")
        return
    
    # Get credentials from environment
    endpoint = os.getenv("DI_ENDPOINT")
    key = os.getenv("DI_KEY")
    
    if not endpoint or not key:
        print("❌ Missing Azure Document Intelligence credentials in .env file")
        return
    
    # Sample document from the reference code
    form_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"
    
    print(f"📄 Analyzing sample document from URL: {form_url}")
    
    try:
        # Initialize client
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        
        # Analyze document from URL using correct API
        poller = document_intelligence_client.begin_analyze_document(
            model_id="prebuilt-read",
            analyze_request={"urlSource": form_url}
        )
        
        print("🔄 Processing document...")
        result = poller.result()
        
        print(f"📝 Document contains content: {result.content}")
        
        # Check for handwritten content
        for idx, style in enumerate(result.styles):
            print(f"📝 Document contains {('handwritten' if style.is_handwritten else 'no handwritten')} content")
        
        # Analyze pages (exact code from reference)
        for page in result.pages:
            print(f"\n----Analyzing Read from page #{page.page_number}----")
            print(f"📄 Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}")
            
            for line_idx, line in enumerate(page.lines):
                print(f"   Line #{line_idx} has text content '{line.content}' within bounding box '{format_bounding_box(line.polygon)}'")
            
            for word in page.words:
                print(f"   Word '{word.content}' has a confidence of {word.confidence}")
            
            print("----------------------------------------")
        
        return result.content
        
    except Exception as e:
        print(f"❌ Error analyzing document: {str(e)}")
        return None

def main():
    """Test both methods"""
    print("🧪 Testing Azure Document Intelligence SDK")
    print("=" * 60)
    
    if not SDK_AVAILABLE:
        print("❌ Please install the SDK first: pip install azure-ai-documentintelligence numpy")
        return
    
    # Test 1: Analyze sample document from URL (reference code)
    print("\n🌐 Test 1: Analyzing sample document from URL")
    analyze_read_from_url()
    
    # Test 2: Analyze local PDF file
    print("\n📁 Test 2: Analyzing local PDF file")
    pdf_files = ["Inamdar_Mihir-CV.pdf", "Srinivas_Potla_Resume.pdf"]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"\n📄 Found {pdf_file}, analyzing...")
            content = analyze_read_from_file(pdf_file)
            if content:
                print(f"✅ Successfully extracted {len(content)} characters")
            break
    else:
        print("⚠️  No PDF files found in current directory")

if __name__ == "__main__":
    main()