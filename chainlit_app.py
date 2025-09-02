"""
Chainlit UI for Resume Analyzer
Interactive web interface for resume analysis with file upload and role matching
"""

import chainlit as cl
import os
import tempfile
from resume_analyzer import ResumeAnalyzer, ResumeAnalysis
from typing import Optional

# Initialize the analyzer
analyzer = ResumeAnalyzer()

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    await cl.Message(
        content="""# 🎯 Resume Analyzer with AI

Welcome! I can help you analyze resumes using Azure Document Intelligence and GPT-4o.

**How to use:**
1. Upload a PDF resume using the attachment button 📎
2. Specify the target role you want to analyze for
3. Get detailed insights including:
   - Skill extraction and scoring
   - Role match percentage
   - Strengths and gaps analysis
   - Personalized recommendations

**Example roles:**
- Senior Python Developer
- Data Scientist
- DevOps Engineer
- Product Manager
- Full Stack Developer

Ready to get started? Upload a resume and tell me the target role!
        """
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    
    # Check if there are any file attachments
    if message.elements:
        # Process file upload
        await process_file_upload(message)
    else:
        # Handle text-only messages
        await cl.Message(
            content="Please upload a PDF resume and specify the target role you'd like me to analyze for. Use the 📎 attachment button to upload your file."
        ).send()

async def process_file_upload(message: cl.Message):
    """Process uploaded resume file"""
    
    # Get the uploaded file
    pdf_file = None
    for element in message.elements:
        if hasattr(element, 'mime') and element.mime and "pdf" in element.mime:
            pdf_file = element
            break
        elif hasattr(element, 'name') and element.name and element.name.lower().endswith('.pdf'):
            pdf_file = element
            break
    
    if not pdf_file:
        await cl.Message(
            content="❌ Please upload a PDF file. Other file formats are not supported yet."
        ).send()
        return
    
    # Extract target role from message
    target_role = extract_target_role(message.content)
    if not target_role:
        await cl.Message(
            content="""📝 I see you've uploaded a resume! Now please specify the target role you'd like me to analyze for.

**Example:**
"Analyze this resume for a Senior Python Developer position"
"How well does this candidate fit a Data Scientist role?"
"Evaluate for DevOps Engineer position"
            """
        ).send()
        return
    
    # Show processing message
    await cl.Message(
        content=f"🔄 Analyzing resume for **{target_role}** position...\n\n⏳ This may take a few moments..."
    ).send()
    
    try:
        # Get file content - handle different Chainlit versions
        file_content = None
        if hasattr(pdf_file, 'content') and pdf_file.content:
            file_content = pdf_file.content
        elif hasattr(pdf_file, 'path') and pdf_file.path:
            with open(pdf_file.path, 'rb') as f:
                file_content = f.read()
        else:
            raise Exception("Could not access file content. Please try uploading the file again.")
        
        if not file_content:
            raise Exception("File content is empty. Please check your PDF file.")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        # Analyze the resume
        analysis = analyzer.analyze_resume(tmp_file_path, target_role)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        # Send results as new messages instead of updating
        await cl.Message(content=format_analysis_results(analysis, target_role)).send()
        
        # Send additional detailed breakdown
        await send_detailed_breakdown(analysis)
        
    except Exception as e:
        # Send error as new message instead of updating
        await cl.Message(
            content=f"❌ **Error analyzing resume:** {str(e)}\n\nPlease check your configuration and try again."
        ).send()

def extract_target_role(message_content: str) -> Optional[str]:
    """Extract target role from user message"""
    if not message_content or len(message_content.strip()) < 5:
        return None
    
    # Common patterns to identify role mentions
    role_indicators = [
        "for", "as", "position", "role", "job", "analyze", "evaluate"
    ]
    
    content_lower = message_content.lower()
    
    # Check if message contains role indicators
    if any(indicator in content_lower for indicator in role_indicators):
        # Simple extraction - take the message content as potential role
        # Remove common words and clean up
        cleaned = message_content.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "analyze this resume for", "analyze for", "evaluate for", 
            "check for", "how well does this fit", "analyze this for"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # Remove common suffixes
        suffixes_to_remove = [
            "position", "role", "job", "candidate"
        ]
        
        for suffix in suffixes_to_remove:
            if cleaned.lower().endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
                break
        
        return cleaned if len(cleaned) > 2 else None
    
    return message_content.strip() if len(message_content.strip()) > 2 else None

def format_analysis_results(analysis: ResumeAnalysis, target_role: str) -> str:
    """Format analysis results for display"""
    
    # Create match score visualization
    score_percentage = int(analysis.role_match_score * 100)
    score_bar = "🟩" * (score_percentage // 10) + "⬜" * (10 - score_percentage // 10)
    
    result = f"""# 🎯 Resume Analysis Results

## 📊 Overall Match Score for **{target_role}**
{score_bar} **{score_percentage}%**

## 📝 Executive Summary
{analysis.summary}

## 💪 Key Strengths
"""
    
    for strength in analysis.strengths[:5]:  # Limit to top 5
        result += f"✅ {strength}\n"
    
    result += "\n## ⚠️ Areas for Improvement\n"
    
    for gap in analysis.gaps[:5]:  # Limit to top 5
        result += f"❌ {gap}\n"
    
    return result

async def send_detailed_breakdown(analysis: ResumeAnalysis):
    """Send detailed skill breakdown and recommendations"""
    
    # Skills breakdown
    skills_content = "## 🛠️ Skills Analysis\n\n"
    
    # Group skills by category
    skills_by_category = {}
    for skill in analysis.skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    for category, skills in skills_by_category.items():
        skills_content += f"### {category.title()} Skills\n"
        
        # Sort by relevance score and take top 8 per category
        sorted_skills = sorted(skills, key=lambda x: x.relevance_score, reverse=True)[:8]
        
        for skill in sorted_skills:
            score_percentage = int(skill.relevance_score * 100)
            score_bar = "🟦" * (score_percentage // 20) + "⬜" * (5 - score_percentage // 20)
            skills_content += f"- **{skill.skill}** {score_bar} {score_percentage}%\n"
        
        skills_content += "\n"
    
    await cl.Message(content=skills_content).send()
    
    # Recommendations
    if analysis.recommendations:
        rec_content = "## 💡 Personalized Recommendations\n\n"
        for i, rec in enumerate(analysis.recommendations, 1):
            rec_content += f"{i}. {rec}\n\n"
        
        await cl.Message(content=rec_content).send()

if __name__ == "__main__":
    # This won't be called when running with chainlit run
    pass