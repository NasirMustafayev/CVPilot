"""
FastAPI server for CVPilot CV analysis engine.
Provides endpoints for CV upload, parsing, and job fit analysis.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import json
from dataclasses import asdict

from file_parser import FileParser
from cv_extractor import CVExtractor, CVData
from job_fit_analyzer import JobFitAnalyzer

app = FastAPI(title="CVPilot Analysis Engine", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "127.0.0.1", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CVDataResponse(BaseModel):
    """Response schema for CV data."""
    contact: dict
    summary: Optional[str]
    experience: list[dict]
    education: list[dict]
    skills: dict
    certifications: list[dict]
    projects: list[dict]


class FitAnalysisResponse(BaseModel):
    """Response schema for fit analysis."""
    cv_data: CVDataResponse
    fit_score: dict
    interview_questions: list[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=FitAnalysisResponse)
async def analyze_cv(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    role_title: str = Form(default="")
) -> dict:
    """
    Upload a CV and job description to analyze fit.
    
    Args:
        file: CV file (PDF, DOCX, DOC)
        job_description: Job description text
        role_title: Job title/role name (optional)
    
    Returns:
        Fit analysis with scores, strengths, gaps, and interview questions
    """
    try:
        # Validate file type
        allowed_extensions = ['pdf', 'docx', 'doc']
        file_ext = file.filename.lower().split('.')[-1]
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Parse file
        try:
            cv_text = FileParser.parse_file(file_content, file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        if not cv_text or len(cv_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        # Extract CV data
        extractor = CVExtractor(cv_text)
        cv_data = extractor.extract()
        
        # Analyze job fit
        analyzer = JobFitAnalyzer(cv_data, job_description, role_title)
        fit_score = analyzer.analyze()
        interview_questions = analyzer.generate_interview_questions()
        
        # Format response
        return {
            "cv_data": {
                "contact": asdict(cv_data.contact),
                "summary": cv_data.summary,
                "experience": [asdict(e) for e in cv_data.experience],
                "education": [asdict(e) for e in cv_data.education],
                "skills": cv_data.skills,
                "certifications": [asdict(c) for c in cv_data.certifications],
                "projects": [asdict(p) if p else {} for p in cv_data.projects],
            },
            "fit_score": {
                "overall_score": round(fit_score.overall_score, 1),
                "skills_match": round(fit_score.skills_match, 1),
                "experience_fit": round(fit_score.experience_fit, 1),
                "evidence_quality": round(fit_score.evidence_quality, 1),
                "strengths": fit_score.strengths,
                "gaps": fit_score.gaps,
                "decision_notes": fit_score.decision_notes,
            },
            "interview_questions": interview_questions,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CV: {str(e)}"
        )


@app.post("/extract-cv")
async def extract_cv(file: UploadFile = File(...)) -> dict:
    """
    Upload a CV file and extract its data.
    
    Args:
        file: CV file (PDF, DOCX, DOC)
    
    Returns:
        Extracted CV data
    """
    try:
        # Validate file type
        allowed_extensions = ['pdf', 'docx', 'doc']
        file_ext = file.filename.lower().split('.')[-1]
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Parse file
        try:
            cv_text = FileParser.parse_file(file_content, file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Extract CV data
        extractor = CVExtractor(cv_text)
        cv_data = extractor.extract()
        
        # Format response
        return {
            "contact": asdict(cv_data.contact),
            "summary": cv_data.summary,
            "experience": [asdict(e) for e in cv_data.experience],
            "education": [asdict(e) for e in cv_data.education],
            "skills": cv_data.skills,
            "certifications": [asdict(c) for c in cv_data.certifications],
            "projects": [asdict(p) if p else {} for p in cv_data.projects],
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CV: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
