"""
Resume Analyzer with Azure Document Intelligence and GPT-4o
Features:
- PDF text extraction using Azure Document Intelligence REST API
- Skill extraction and role matching using GPT-4o
- Structured analysis and scoring
"""

import os
import json
import requests
import time
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import AzureOpenAI
from dotenv import load_dotenv

# Azure Document Intelligence SDK imports
try:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import ContentFormat
    SDK_AVAILABLE = True
except ImportError as e:
    SDK_AVAILABLE = False
    print(f"⚠️  Azure Document Intelligence SDK not available: {e}")
    print("Using REST API fallback.")

# Load environment variables
load_dotenv()

@dataclass
class SkillMatch:
    skill: str
    relevance_score: float
    category: str

@dataclass
class ResumeAnalysis:
    extracted_text: str
    skills: List[SkillMatch]
    role_match_score: float
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]
    summary: str

class ResumeAnalyzer:
    def __init__(self, use_sdk: bool = True):
        # Azure Document Intelligence credentials
        self.di_endpoint = os.getenv("DI_ENDPOINT")
        self.di_key = os.getenv("DI_KEY")
        self.use_sdk = use_sdk and SDK_AVAILABLE
        
        # Initialize Document Intelligence client if SDK is available and requested
        if self.use_sdk:
            try:
                self.di_client = DocumentIntelligenceClient(
                    endpoint=self.di_endpoint, 
                    credential=AzureKeyCredential(self.di_key)
                )
                print("✅ Using Azure Document Intelligence SDK")
            except Exception as e:
                print(f"⚠️  Failed to initialize SDK client: {e}")
                self.use_sdk = False
                print("🔄 Falling back to REST API")
        else:
            print("🔄 Using REST API for Document Intelligence")
        
        # Initialize Azure OpenAI client
        self.openai_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

    def format_bounding_box(self, bounding_box):
        """Format bounding box coordinates for display"""
        if not bounding_box:
            return "N/A"
        reshaped_bounding_box = np.array(bounding_box).reshape(-1, 2)
        return ", ".join(["[{}, {}]".format(x, y) for x, y in reshaped_bounding_box])

    def extract_text_from_pdf_sdk(self, pdf_path: str) -> str:
        """Extract text from PDF using Azure Document Intelligence SDK"""
        try:
            if not self.use_sdk:
                raise Exception("SDK not available, use extract_text_from_pdf_rest instead")
            
            # Validate credentials
            if not self.di_key or not self.di_endpoint:
                raise Exception("Azure Document Intelligence credentials not found. Please check your .env file.")
            
            print(f"📄 Analyzing PDF with SDK: {pdf_path}")
            
            # Read PDF file
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            
            # Analyze document using SDK - Updated API based on Microsoft docs
            poller = self.di_client.begin_analyze_document(
                model_id="prebuilt-read",
                analyze_request=pdf_data,
                content_type="application/pdf"
            )
            
            print("🔄 Processing document...")
            result = poller.result()
            
            # Extract structured content with sections
            structured_content = self.extract_structured_content(result)
            
            print(f"✅ Successfully extracted {len(structured_content)} characters using SDK")
            
            # Optional: Print detailed analysis
            if hasattr(result, 'styles') and result.styles:
                for idx, style in enumerate(result.styles):
                    handwritten_text = "handwritten" if (hasattr(style, 'is_handwritten') and style.is_handwritten) else "no handwritten"
                    print(f"📝 Document contains {handwritten_text} content")
            
            if hasattr(result, 'pages') and result.pages:
                for page in result.pages:
                    print(f"📄 Page #{page.page_number}: {page.width}x{page.height} {page.unit}")
                    if hasattr(page, 'lines') and page.lines:
                        print(f"   📝 Found {len(page.lines)} lines of text")
                    if hasattr(page, 'words') and page.words:
                        confidences = [word.confidence for word in page.words if hasattr(word, 'confidence') and word.confidence is not None]
                        if confidences:
                            avg_confidence = sum(confidences) / len(confidences)
                            print(f"   🎯 Average word confidence: {avg_confidence:.2%}")
            
            return structured_content
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF using SDK: {str(e)}")

    def extract_structured_content(self, result) -> str:
        """Extract structured content with sections and paragraphs"""
        try:
            # Start with the raw content
            content = result.content if result.content else ""
            
            # Try to identify and structure sections
            structured_sections = []
            
            if hasattr(result, 'pages') and result.pages:
                for page in result.pages:
                    if hasattr(page, 'lines') and page.lines:
                        current_section = None
                        current_paragraph = []
                        
                        for line in page.lines:
                            line_text = line.content.strip()
                            
                            # Skip empty lines
                            if not line_text:
                                if current_paragraph:
                                    if current_section:
                                        current_section += " " + " ".join(current_paragraph)
                                    current_paragraph = []
                                continue
                            
                            # Detect section headers (common resume sections)
                            section_keywords = [
                                'work experience', 'experience', 'employment', 'professional experience',
                                'education', 'academic background', 'qualifications',
                                'skills', 'technical skills', 'core competencies', 'expertise',
                                'projects', 'key projects', 'notable projects',
                                'certifications', 'certificates', 'achievements',
                                'summary', 'profile', 'objective', 'about',
                                'contact', 'personal information'
                            ]
                            
                            is_section_header = any(keyword in line_text.lower() for keyword in section_keywords)
                            
                            # Check if line looks like a header (short, potentially bold/larger)
                            is_likely_header = (
                                len(line_text.split()) <= 4 and 
                                not line_text.endswith('.') and
                                not line_text.startswith('•') and
                                not line_text.startswith('-')
                            )
                            
                            if is_section_header or is_likely_header:
                                # Save previous section
                                if current_section and current_paragraph:
                                    current_section += " " + " ".join(current_paragraph)
                                if current_section:
                                    structured_sections.append(current_section)
                                
                                # Start new section
                                current_section = f"\n\n=== {line_text.upper()} ===\n"
                                current_paragraph = []
                            else:
                                # Add to current paragraph
                                current_paragraph.append(line_text)
                                
                                # End paragraph on certain conditions
                                if (line_text.endswith('.') or 
                                    line_text.endswith(':') or 
                                    len(current_paragraph) > 3):
                                    if current_section:
                                        current_section += " " + " ".join(current_paragraph) + "\n"
                                    current_paragraph = []
                        
                        # Don't forget the last section
                        if current_section and current_paragraph:
                            current_section += " " + " ".join(current_paragraph)
                        if current_section:
                            structured_sections.append(current_section)
            
            # If we found structured sections, use them; otherwise use original content
            if structured_sections:
                structured_content = "\n".join(structured_sections)
                print(f"📋 Identified {len(structured_sections)} sections")
                return structured_content
            else:
                print("📋 Using original content (no clear sections detected)")
                return content
                
        except Exception as e:
            print(f"⚠️  Error structuring content: {e}")
            # Fallback to original content
            return result.content if result.content else ""

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using the best available method (SDK preferred, REST API fallback)"""
        if self.use_sdk:
            try:
                return self.extract_text_from_pdf_sdk(pdf_path)
            except Exception as e:
                print(f"⚠️  SDK method failed: {e}")
                print("🔄 Falling back to REST API")
                return self.extract_text_from_pdf_rest(pdf_path)
        else:
            return self.extract_text_from_pdf_rest(pdf_path)

    def extract_text_from_pdf_rest(self, pdf_path: str) -> str:
        """Extract text from PDF using Azure Document Intelligence REST API"""
        try:
            # Validate credentials
            if not self.di_key or not self.di_endpoint:
                raise Exception("Azure Document Intelligence credentials not found. Please check your .env file.")
            
            # Read PDF file
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            
            print(f"📡 Using endpoint: {self.di_endpoint}")
            print(f"🔑 Using key: {self.di_key[:10]}...")
            
            # Prepare headers
            headers = {
                "Ocp-Apim-Subscription-Key": self.di_key,
                "Content-Type": "application/pdf"
            }
            
            # Ensure endpoint doesn't have trailing slash
            endpoint = self.di_endpoint.rstrip('/')
            
            # Start analysis - try different API versions
            api_versions = ["2024-02-29-preview", "2023-07-31", "2022-08-31"]
            
            for api_version in api_versions:
                analyze_url = f"{endpoint}/documentintelligence/documentModels/prebuilt-read:analyze?api-version={api_version}"
                print(f"🔄 Trying API version {api_version}...")
                
                response = requests.post(analyze_url, headers=headers, data=pdf_data)
                
                if response.status_code == 202:
                    print(f"✅ Successfully started analysis with API version {api_version}")
                    break
                elif response.status_code == 401:
                    print(f"❌ Authentication failed with API version {api_version}")
                    continue
                else:
                    print(f"⚠️  API version {api_version} returned {response.status_code}")
                    continue
            else:
                # If all API versions failed, try the older Form Recognizer endpoint
                print("🔄 Trying legacy Form Recognizer endpoint...")
                analyze_url = f"{endpoint}/formrecognizer/documentModels/prebuilt-read:analyze?api-version=2022-08-31"
                response = requests.post(analyze_url, headers=headers, data=pdf_data)
            
            if response.status_code != 202:
                error_details = f"Status: {response.status_code}, Response: {response.text}"
                if response.status_code == 401:
                    raise Exception(f"Authentication failed. Please check your Azure Document Intelligence key and endpoint.\n{error_details}")
                else:
                    raise Exception(f"Failed to start analysis: {error_details}")
            
            # Get operation location
            operation_location = response.headers.get("Operation-Location")
            if not operation_location:
                raise Exception("No operation location returned")
            
            print(f"📍 Operation location: {operation_location}")
            
            # Poll for results
            headers_get = {
                "Ocp-Apim-Subscription-Key": self.di_key
            }
            
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(2)  # Wait 2 seconds between polls
                
                result_response = requests.get(operation_location, headers=headers_get)
                
                if result_response.status_code != 200:
                    raise Exception(f"Failed to get results: {result_response.status_code} - {result_response.text}")
                
                result_data = result_response.json()
                status = result_data.get("status")
                
                print(f"📊 Analysis status: {status} (attempt {attempt + 1}/{max_attempts})")
                
                if status == "succeeded":
                    # Extract content from result
                    analyze_result = result_data.get("analyzeResult", {})
                    content = analyze_result.get("content", "")
                    print(f"✅ Successfully extracted {len(content)} characters")
                    return content
                elif status == "failed":
                    error = result_data.get("error", {})
                    raise Exception(f"Analysis failed: {error}")
                elif status in ["running", "notStarted"]:
                    continue
                else:
                    raise Exception(f"Unknown status: {status}")
            
            raise Exception("Analysis timed out")
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def analyze_resume_with_gpt4o(self, resume_text: str, target_role: str) -> Dict:
        """Analyze resume using GPT-4o for skill extraction and role matching"""
        
        system_prompt = """You are an expert HR analyst and technical recruiter. Analyze the provided resume text and extract relevant information for the specified role.

Return your analysis as a JSON object with the following structure:
{
    "skills": [
        {
            "skill": "skill name",
            "relevance_score": 0.0-1.0,
            "category": "technical/soft/domain"
        }
    ],
    "role_match_score": 0.0-1.0,
    "strengths": ["strength 1", "strength 2"],
    "gaps": ["gap 1", "gap 2"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "summary": "Brief summary of candidate fit"
}

Focus on:
1. Technical skills, programming languages, frameworks, tools
2. Soft skills and leadership qualities
3. Domain expertise and industry knowledge
4. How well the candidate matches the target role
5. Specific gaps and improvement areas
6. Actionable recommendations
"""

        user_prompt = f"""
Target Role: {target_role}

Resume Text:
{resume_text}

Please analyze this resume for the specified role and provide detailed insights.
"""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse the JSON response
            response_content = response.choices[0].message.content.strip()
            print(f"🔍 GPT-4o Response length: {len(response_content)} characters")
            print(f"🔍 First 300 chars: {response_content[:300]}")
            
            # Try multiple JSON parsing strategies
            analysis_json = None
            
            # Strategy 1: Direct JSON parsing
            try:
                analysis_json = json.loads(response_content)
                print("✅ Direct JSON parsing successful")
            except json.JSONDecodeError as e:
                print(f"❌ Direct JSON parsing failed: {e}")
                
                # Strategy 2: Extract JSON from markdown code blocks
                if "```json" in response_content:
                    try:
                        json_start = response_content.find("```json") + 7
                        json_end = response_content.find("```", json_start)
                        if json_end > json_start:
                            json_content = response_content[json_start:json_end].strip()
                            analysis_json = json.loads(json_content)
                            print("✅ Markdown JSON extraction successful")
                    except json.JSONDecodeError:
                        print("❌ Markdown JSON extraction failed")
                
                # Strategy 3: Find JSON object in response
                if not analysis_json:
                    import re
                    json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                    if json_match:
                        try:
                            analysis_json = json.loads(json_match.group())
                            print("✅ Regex JSON extraction successful")
                        except json.JSONDecodeError:
                            print("❌ Regex JSON extraction failed")
                
                # Strategy 4: Create fallback response
                if not analysis_json:
                    print("🔄 Creating fallback analysis response")
                    analysis_json = {
                        "skills": [
                            {"skill": "Communication", "relevance_score": 0.7, "category": "soft"},
                            {"skill": "Problem Solving", "relevance_score": 0.8, "category": "soft"},
                            {"skill": "Technical Skills", "relevance_score": 0.6, "category": "technical"}
                        ],
                        "role_match_score": 0.65,
                        "strengths": ["Professional experience", "Educational background"],
                        "gaps": ["Analysis incomplete due to response parsing issues"],
                        "recommendations": ["Review and update resume format", "Consider professional resume review"],
                        "summary": "Candidate shows potential but full analysis was limited due to technical issues."
                    }
            
            return analysis_json
            
        except Exception as e:
            raise Exception(f"Error analyzing resume with GPT-4o: {str(e)}")

    def analyze_resume(self, pdf_path: str, target_role: str) -> ResumeAnalysis:
        """Complete resume analysis pipeline"""
        
        # Step 1: Extract text from PDF
        print("📄 Extracting text from PDF...")
        extracted_text = self.extract_text_from_pdf(pdf_path)
        
        # Step 2: Analyze with GPT-4o
        print("🤖 Analyzing resume with GPT-4o...")
        gpt_analysis = self.analyze_resume_with_gpt4o(extracted_text, target_role)
        
        # Step 3: Structure the results
        skills = [
            SkillMatch(
                skill=skill["skill"],
                relevance_score=skill["relevance_score"],
                category=skill["category"]
            )
            for skill in gpt_analysis.get("skills", [])
        ]
        
        return ResumeAnalysis(
            extracted_text=extracted_text,
            skills=skills,
            role_match_score=gpt_analysis.get("role_match_score", 0.0),
            strengths=gpt_analysis.get("strengths", []),
            gaps=gpt_analysis.get("gaps", []),
            recommendations=gpt_analysis.get("recommendations", []),
            summary=gpt_analysis.get("summary", "")
        )

    def print_analysis(self, analysis: ResumeAnalysis, target_role: str):
        """Print formatted analysis results"""
        print("\n" + "="*80)
        print(f"🎯 RESUME ANALYSIS FOR: {target_role.upper()}")
        print("="*80)
        
        print(f"\n📊 OVERALL ROLE MATCH SCORE: {analysis.role_match_score:.1%}")
        
        print(f"\n📝 SUMMARY:")
        print(f"   {analysis.summary}")
        
        print(f"\n💪 STRENGTHS:")
        for strength in analysis.strengths:
            print(f"   ✅ {strength}")
        
        print(f"\n⚠️  GAPS TO ADDRESS:")
        for gap in analysis.gaps:
            print(f"   ❌ {gap}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        for rec in analysis.recommendations:
            print(f"   💡 {rec}")
        
        print(f"\n🛠️  EXTRACTED SKILLS:")
        
        # Group skills by category
        skills_by_category = {}
        for skill in analysis.skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
        
        for category, skills in skills_by_category.items():
            print(f"\n   {category.upper()} SKILLS:")
            # Sort by relevance score
            sorted_skills = sorted(skills, key=lambda x: x.relevance_score, reverse=True)
            for skill in sorted_skills:
                score_bar = "█" * int(skill.relevance_score * 10) + "░" * (10 - int(skill.relevance_score * 10))
                print(f"     {skill.skill:<25} [{score_bar}] {skill.relevance_score:.1%}")

def main():
    """Main function for testing"""
    # You can choose to use SDK (preferred) or REST API
    # analyzer = ResumeAnalyzer(use_sdk=True)   # Use SDK (default)
    # analyzer = ResumeAnalyzer(use_sdk=False)  # Force REST API
    analyzer = ResumeAnalyzer()  # Auto-detect best method
    
    # Example usage
    pdf_path = "Inamdar_Mihir-CV.pdf"  # Update with your PDF path
    target_role = "Senior Python Developer"  # Update with target role
    
    try:
        analysis = analyzer.analyze_resume(pdf_path, target_role)
        analyzer.print_analysis(analysis, target_role)
        
    except FileNotFoundError:
        print("❌ Error: PDF file not found. Please check the file path.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()