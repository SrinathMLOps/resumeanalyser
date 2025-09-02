# 📚 API Reference

## ResumeAnalyzer Class

### Constructor
```python
ResumeAnalyzer(use_sdk: bool = True)
```
- `use_sdk`: Whether to use Azure Document Intelligence SDK (True) or REST API (False)

### Methods

#### `analyze_resume(pdf_path: str, target_role: str) -> ResumeAnalysis`
Complete resume analysis pipeline.

**Parameters:**
- `pdf_path`: Path to the PDF resume file
- `target_role`: Target job role for analysis (e.g., "Senior Python Developer")

**Returns:** `ResumeAnalysis` object with structured results

#### `extract_text_from_pdf(pdf_path: str) -> str`
Extract text using the best available method (SDK preferred, REST API fallback).

#### `extract_text_from_pdf_sdk(pdf_path: str) -> str`
Extract text using Azure Document Intelligence SDK.

#### `extract_text_from_pdf_rest(pdf_path: str) -> str`
Extract text using Azure Document Intelligence REST API.

#### `extract_structured_content(result) -> str`
Extract structured content with automatic section detection.

#### `analyze_resume_with_gpt4o(resume_text: str, target_role: str) -> Dict`
Analyze resume using GPT-4o for skill extraction and role matching.

## Data Classes

### ResumeAnalysis
```python
@dataclass
class ResumeAnalysis:
    extracted_text: str
    skills: List[SkillMatch]
    role_match_score: float
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]
    summary: str
```

### SkillMatch
```python
@dataclass
class SkillMatch:
    skill: str
    relevance_score: float  # 0.0 to 1.0
    category: str          # "technical", "soft", or "domain"
```

## Usage Examples

### Basic Usage
```python
from resume_analyzer import ResumeAnalyzer

analyzer = ResumeAnalyzer()
analysis = analyzer.analyze_resume("resume.pdf", "Senior Python Developer")
print(f"Match Score: {analysis.role_match_score:.1%}")
```

### Force REST API
```python
analyzer = ResumeAnalyzer(use_sdk=False)
analysis = analyzer.analyze_resume("resume.pdf", "Data Scientist")
```

### Extract Text Only
```python
analyzer = ResumeAnalyzer()
text = analyzer.extract_text_from_pdf("resume.pdf")
print(text)
```

### Custom Analysis
```python
analyzer = ResumeAnalyzer()
text = analyzer.extract_text_from_pdf("resume.pdf")
gpt_analysis = analyzer.analyze_resume_with_gpt4o(text, "DevOps Engineer")
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DI_KEY` | Document Intelligence API Key | `abc123...` |
| `DI_ENDPOINT` | Document Intelligence Endpoint | `https://resource.cognitiveservices.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API Key | `def456...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI Endpoint | `https://resource.openai.azure.com/` |
| `AZURE_OPENAI_API_VERSION` | API Version | `2024-02-15-preview` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model Deployment Name | `gpt-4o` |

## Error Handling

The analyzer includes comprehensive error handling:

- **SDK Fallback**: Automatically falls back to REST API if SDK fails
- **JSON Parsing**: Multiple strategies for parsing GPT-4o responses
- **Credential Validation**: Clear error messages for missing/invalid credentials
- **File Handling**: Graceful handling of file access issues

## Performance Notes

- **SDK vs REST API**: SDK is generally faster and more reliable
- **File Size**: Supports PDFs up to 50MB (Azure limit)
- **Processing Time**: Typically 5-15 seconds depending on document complexity
- **Rate Limits**: Subject to Azure service rate limits