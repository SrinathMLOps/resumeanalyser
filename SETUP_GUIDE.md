# 🚀 Complete Setup Guide

## Prerequisites
- Python 3.8 or later
- Azure subscription with Document Intelligence and OpenAI resources

## Step 1: Azure Resource Setup

### Azure Document Intelligence
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new "Document Intelligence" resource
3. Copy the **Key** and **Endpoint** from the resource

### Azure OpenAI
1. Create an "Azure OpenAI" resource
2. Deploy a **GPT-4o** model
3. Copy the **API Key**, **Endpoint**, and **Deployment Name**

## Step 2: Environment Setup

### Option A: Automatic Installation (Windows)
```bash
install.bat
```

### Option B: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install python-dotenv
pip install azure-ai-documentintelligence
pip install azure-core
pip install numpy
pip install openai
pip install chainlit
pip install requests
```

## Step 3: Configuration

1. Copy `.env.example` to `.env`
2. Update your credentials:

```env
# Azure Document Intelligence
DI_KEY=your_document_intelligence_key_here
DI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/

# Azure OpenAI GPT-4o
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

## Step 4: Testing

### Test Credentials
```bash
python test_credentials.py
```

### Test Document Intelligence SDK
```bash
python test_document_intelligence_sdk.py
```

### Test Full Analysis
```bash
python resume_analyzer.py
```

## Step 5: Running the Application

### Web Interface (Recommended)
```bash
chainlit run chainlit_app.py -w
```
Then open http://localhost:8000

### Command Line
```bash
python resume_analyzer.py
```

## Troubleshooting

### Common Issues

1. **SDK Import Error**
   ```bash
   pip install azure-ai-documentintelligence --upgrade
   ```

2. **Authentication Failed**
   - Verify your keys and endpoints in `.env`
   - Check Azure resource status and quotas

3. **JSON Parsing Error**
   - The system has automatic fallbacks
   - Check GPT-4o deployment status

4. **File Upload Issues**
   - Ensure PDF files are not corrupted
   - Check file size limits (typically 50MB max)

### Getting Help
- Check the console output for detailed error messages
- Verify all environment variables are set correctly
- Ensure Azure resources are active and have available quotas

## Advanced Configuration

### Using Different Models
Update the deployment name in `.env`:
```env
AZURE_OPENAI_DEPLOYMENT_NAME=your-model-name
```

### Forcing REST API (if SDK issues)
```python
analyzer = ResumeAnalyzer(use_sdk=False)
```

### Custom Analysis Prompts
Modify the `system_prompt` in `resume_analyzer.py` to customize analysis criteria.