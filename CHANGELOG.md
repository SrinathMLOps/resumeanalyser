# Changelog

## Version 2.0.0 - Enhanced SDK Integration

### 🚀 New Features
- **Azure Document Intelligence SDK Integration**: Added support for the official Azure AI Document Intelligence SDK
- **Structured Content Extraction**: Enhanced text extraction with automatic section detection and paragraph organization
- **Dual Method Support**: Automatic fallback from SDK to REST API for maximum reliability
- **Enhanced Error Handling**: Robust JSON parsing with multiple fallback strategies
- **Detailed Analysis Output**: Improved GPT-4o analysis with confidence scores and structured results

### 🔧 Technical Improvements
- Added `extract_structured_content()` method for better resume parsing
- Enhanced `analyze_resume_with_gpt4o()` with multiple JSON parsing strategies
- Improved error handling and logging throughout the application
- Added comprehensive test scripts for SDK validation

### 📦 Dependencies Added
- `azure-ai-documentintelligence`: Official Azure SDK
- `numpy`: For bounding box calculations and data processing

### 🐛 Bug Fixes
- Fixed JSON parsing issues with GPT-4o responses
- Improved credential validation and error messages
- Enhanced file handling for different PDF formats

### 📚 Documentation
- Updated README with SDK usage instructions
- Added comprehensive test scripts
- Enhanced code comments and documentation

## Version 1.0.0 - Initial Release

### Features
- Basic PDF text extraction using Azure Document Intelligence REST API
- GPT-4o integration for resume analysis
- Chainlit web interface
- Command-line interface
- Basic skill extraction and role matching