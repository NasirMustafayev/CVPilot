"""
FastAPI server for CVPilot CV analysis engine.
Provides endpoints for CV upload, parsing, and job fit analysis.
"""

from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Optional
from dataclasses import asdict

from auth import (
    get_current_user,
    init_auth,
    login_user,
    register_user,
    user_response,
)
from database import delete_analyses, get_analysis, list_analyses, save_analysis
from file_parser import FileParser
from cv_extractor import CVExtractor
from job_fit_analyzer import JobFitAnalyzer
from insight_generator import generate_insights

# Configuration
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
ALLOWED_EXTENSIONS = ['pdf', 'docx', 'doc']

@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_auth()
    yield


app = FastAPI(title="CVPilot Analysis Engine", version="1.1.0", lifespan=lifespan)

# Enable CORS for React frontend
# Allow all origins for development. For production, restrict to your domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development/hackathon)
    # For production, use: allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"]
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
    id: Optional[int] = None
    cv_filename: Optional[str] = None
    role_title: Optional[str] = None
    job_description: Optional[str] = None
    cv_data: CVDataResponse
    fit_score: dict
    interview_questions: list[str]
    analysis_mode: str = "rules"
    matched_skills: list[str] = []
    missing_skills: list[str] = []


class AnalysisSummary(BaseModel):
    id: int
    workspace: Literal["hr", "candidate"]
    cv_filename: str
    candidate_name: Optional[str] = None
    role_title: str
    overall_score: float
    created_at: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    role: Literal["hr", "candidate"]
    display_name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    display_name: str
    role: Literal["hr", "candidate"]
    created_at: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@app.post("/auth/register", response_model=AuthResponse)
async def auth_register(body: RegisterRequest):
    user, token = register_user(
        body.email,
        body.password,
        body.role,
        body.display_name,
    )
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/auth/login", response_model=AuthResponse)
async def auth_login(body: LoginRequest):
    user, token = login_user(body.email, body.password)
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.get("/auth/me", response_model=UserResponse)
async def auth_me(current_user: dict = Depends(get_current_user)):
    return user_response(current_user)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/analyses", response_model=list[AnalysisSummary])
async def get_analyses(
    workspace: Optional[Literal["hr", "candidate"]] = None,
    current_user: dict = Depends(get_current_user),
):
    rows = list_analyses(current_user["id"], workspace=workspace)
    return rows


@app.delete("/analyses")
async def clear_analyses(
    workspace: Optional[Literal["hr", "candidate"]] = None,
    current_user: dict = Depends(get_current_user),
):
    deleted = delete_analyses(current_user["id"], workspace=workspace)
    return {"deleted": deleted}


@app.get("/analyses/{analysis_id}", response_model=FitAnalysisResponse)
async def get_analysis_by_id(
    analysis_id: int,
    current_user: dict = Depends(get_current_user),
):
    row = get_analysis(current_user["id"], analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    result = row["result"]
    result["id"] = row["id"]
    result["cv_filename"] = row["cv_filename"]
    result["role_title"] = row["role_title"]
    result["job_description"] = row["job_description"]
    return result


@app.post("/analyze", response_model=FitAnalysisResponse)
async def analyze_cv(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    role_title: str = Form(default=""),
    workspace: str = Form(default="hr"),
    current_user: dict = Depends(get_current_user),
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
        file_ext = file.filename.lower().split('.')[-1]
        
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: 25 MB"
            )
        
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Parse file
        try:
            cv_text = FileParser.parse_file(file_content, file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Debug: Print extracted text length
        print(f"[DEBUG] Extracted text length: {len(cv_text)} characters")
        print(f"[DEBUG] Job description length: {len(job_description)} characters")
        print(f"[DEBUG] Role title: '{role_title}'")
        
        if not cv_text or len(cv_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        # Extract CV data
        extractor = CVExtractor(cv_text)
        cv_data = extractor.extract()
        
        # Debug: Print extracted data
        print(f"[DEBUG] Extracted skills: {cv_data.skills}")
        print(f"[DEBUG] Extracted experience roles: {[e.role for e in cv_data.experience]}")
        
        # Analyze job fit
        analyzer = JobFitAnalyzer(cv_data, job_description, role_title)
        fit_score = analyzer.analyze()
        interview_questions = analyzer.generate_interview_questions(
            fit_score.missing_skills
        )

        llm_insights = generate_insights(
            cv_data,
            job_description,
            role_title,
            fit_score,
            fit_score.matched_skills,
            fit_score.missing_skills,
        )
        if llm_insights:
            analyzer.apply_insights(fit_score, llm_insights)
            interview_questions = llm_insights.get(
                "interview_questions", interview_questions
            )

        analysis_mode = fit_score.analysis_mode

        if workspace not in ("hr", "candidate"):
            raise HTTPException(status_code=400, detail="workspace must be hr or candidate")

        candidate_name = cv_data.contact.name if cv_data.contact else None

        # Format response
        response = {
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
                "overall_score": fit_score.overall_score,
                "skills_match": fit_score.skills_match,
                "experience_fit": fit_score.experience_fit,
                "evidence_quality": fit_score.evidence_quality,
                "strengths": fit_score.strengths,
                "gaps": fit_score.gaps,
                "decision_notes": fit_score.decision_notes,
            },
            "interview_questions": interview_questions,
            "analysis_mode": analysis_mode,
            "matched_skills": fit_score.matched_skills,
            "missing_skills": fit_score.missing_skills,
        }

        analysis_id = save_analysis(
            user_id=current_user["id"],
            workspace=workspace,
            cv_filename=file.filename or "cv.pdf",
            role_title=role_title or "Role",
            job_description=job_description,
            overall_score=fit_score.overall_score,
            result=response,
            candidate_name=candidate_name,
        )
        response["id"] = analysis_id
        response["cv_filename"] = file.filename
        response["role_title"] = role_title
        response["job_description"] = job_description
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CV: {str(e)}"
        )


@app.post("/extract-cv")
async def extract_cv(
    file: UploadFile = File(...),
    _current_user: dict = Depends(get_current_user),
) -> dict:
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
