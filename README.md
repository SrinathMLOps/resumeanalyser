# 🎯 AI-Powered Resume Analyzer

An intelligent resume analysis tool that combines Azure Document Intelligence for PDF text extraction and Azure OpenAI GPT-4o for advanced skill extraction, role matching, and candidate evaluation.

## ✨ Features

- **Advanced PDF Text Extraction**: 
  - Azure Document Intelligence SDK (preferred) with automatic fallback to REST API
  - Detailed document analysis with confidence scores and bounding boxes
  - Support for handwritten text detection
- **AI-Powered Analysis**: Leverages GPT-4o for intelligent skill extraction and role matching
- **Interactive Web UI**: Clean Chainlit interface for easy file upload and analysis
- **Comprehensive Insights**:
  - Skill extraction with relevance scoring
  - Role match percentage
  - Strengths and gaps analysis
  - Personalized recommendations
  - Skills categorization (Technical/Soft/Domain)
- **Flexible Architecture**: Automatic method selection with graceful fallbacks

## 🚀 Quick Start

### 1. Install Dependencies

**Option A: Automatic Installation (Windows)**
```bash
install.bat
```

**Option B: Manual Installation**
```bash
pip install -r requirements.txt
```

**Option C: Step by Step (if you have issues)**
```bash
pip install python-dotenv
pip install numpy
pip install azure-core
pip install azure-ai-documentintelligence
pip install openai
pip install chainlit
pip install requests
```

### 2. Configure Environment Variables
Update your `.env` file with your Azure credentials:

```env
# Azure Document Intelligence
DI_KEY=your_document_intelligence_key
DI_ENDPOINT=your_document_intelligence_endpoint

# Azure AI Foundry GPT-4o
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 3. Run the Application

#### Option A: Web UI (Recommended)
```bash
chainlit run chainlit_app.py -w
```
Then open http://localhost:8000 in your browser.

#### Option B: Command Line
```bash
python resume_analyzer.py
```

## 🎮 How to Use

### Web Interface
1. Open the Chainlit web interface
2. Upload a PDF resume using the 📎 attachment button
3. Specify the target role (e.g., "Senior Python Developer")
4. Get comprehensive analysis results

### Command Line
1. Update the `pdf_path` and `target_role` in `resume_analyzer_enhanced.py`
2. Run the script to see detailed console output

## 📊 Analysis Output

The tool provides:

- **Overall Match Score**: Percentage match for the target role
- **Executive Summary**: AI-generated summary of candidate fit
- **Strengths**: Key positive aspects of the candidate
- **Gaps**: Areas that need improvement
- **Skills Breakdown**: Categorized skills with relevance scores
- **Recommendations**: Actionable advice for improvement

## 🔧 Configuration

### Azure Document Intelligence
- Create a Document Intelligence resource in Azure
- Copy the key and endpoint to your `.env` file

### Azure OpenAI (GPT-4o)
- Create an Azure OpenAI resource
- Deploy a GPT-4o model
- Copy the API key, endpoint, and deployment name to your `.env` file

## 📁 Project Structure

```
resume_analyzer/
├── chainlit_app.py                    # Chainlit web interface
├── resume_analyzer.py                 # Enhanced core analysis logic (SDK + REST API)
├── test_document_intelligence_sdk.py  # SDK testing and demonstration
├── test_credentials.py                # Credential validation
├── requirements.txt                   # Python dependencies
├── install.bat                        # Windows installation script
├── install.py                         # Python installation script
├── .env                              # Environment variables
└── README.md                         # This file
```

## 🛠️ Customization

### Choosing Extraction Method
```python
# Use SDK (default, preferred)
analyzer = ResumeAnalyzer(use_sdk=True)

# Force REST API (fallback)
analyzer = ResumeAnalyzer(use_sdk=False)

# Auto-detect best method
analyzer = ResumeAnalyzer()
```

### Adding New Role Templates
Modify the system prompt in `resume_analyzer.py` to include specific requirements for different roles.

### Adjusting Analysis Criteria
Update the GPT-4o prompts to focus on different aspects of resume analysis.

### UI Customization
Modify `chainlit_app.py` to change the interface layout and messaging.

## 🧪 Testing

### Test Document Intelligence SDK
```bash
python test_document_intelligence_sdk.py
```

### Test Credentials
```bash
python test_credentials.py
```

## 🔍 Troubleshooting

### Common Issues

1. **PDF Not Found**: Ensure the PDF path is correct and the file exists
2. **Azure Credentials**: Verify all environment variables are set correctly
3. **Model Deployment**: Ensure your GPT-4o model is deployed and accessible
4. **File Upload Issues**: Check file size limits and ensure PDF format

### Error Messages
- Check the console output for detailed error messages
- Verify your Azure resource quotas and limits
- Ensure your API keys have the necessary permissions

## 📝 License

This project is for educational and demonstration purposes. Please ensure you comply with Azure service terms and conditions.