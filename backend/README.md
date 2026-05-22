# CVPilot Backend - CV Analyzer Engine

## Overview

The backend is a FastAPI server that provides CV extraction and job fit analysis capabilities. It extracts structured data from PDF, DOCX, and DOC files and analyzes how well a candidate matches a job description.

## Architecture

### Core Modules

1. **`main.py`** - FastAPI server with REST API endpoints
2. **`file_parser.py`** - PDF/DOCX/DOC text extraction
3. **`cv_extractor.py`** - CV data parsing and structure extraction
4. **`job_fit_analyzer.py`** - Job fit scoring and analysis

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Running the Server

```bash
# Development
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000

# Access API docs
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## API Endpoints

### Health Check
```
GET /health
```

Returns server status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Analyze CV Against Job Description
```
POST /analyze
```

Upload a CV file and job description to get fit analysis **compared to the open position**.

**Request:**
- `file` (form-data, required): PDF, DOCX, or DOC file
- `job_description` (form-data, required): Job description text
- `role_title` (form-data, optional): Job title/position name (e.g., "Senior Frontend Engineer")

**Why role_title matters:**
- Enables role-aware skill matching
- Detects if candidate has held similar positions
- Tailors interview questions to the specific role
- Generates role-specific strengths and gaps

**Response:**
```json
{
  "cv_data": {
    "contact": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-123-4567",
      "location": "San Francisco, CA",
      "linkedin": "https://linkedin.com/in/johndoe",
      "website": "https://johndoe.dev"
    },
    "summary": "Experienced software engineer...",
    "experience": [
      {
        "role": "Senior Frontend Engineer",
        "company": "TechCorp",
        "start_date": "01/2022",
        "end_date": "Present",
        "description": "Led frontend team...",
        "duration_months": 24
      }
    ],
    "education": [
      {
        "degree": "Bachelor of Science",
        "institution": "UC Berkeley",
        "field": "Computer Science",
        "graduation_date": "2018",
        "gpa": "3.8"
      }
    ],
    "skills": {
      "technical": ["react", "typescript", "python", "aws"],
      "soft": ["leadership", "communication"],
      "languages": ["English", "Spanish"]
    },
    "certifications": [
      {
        "name": "AWS Certified Solutions Architect",
        "issuer": "Amazon",
        "date": "2023"
      }
    ],
    "projects": [
      {
        "name": "Project Name",
        "description": "Description...",
        "technologies": ["React", "Node.js"]
      }
    ]
  },
  "fit_score": {
    "overall_score": 82.3,
    "skills_match": 85.5,
    "experience_fit": 79.2,
    "evidence_quality": 82.1,
    "strengths": [
      "Strong skills alignment with job requirements",
      "Highly relevant work experience",
      "Strong technical foundation (12 skills mentioned)"
    ],
    "gaps": [
      "Validate experience with cloud deployment",
      "Clarify depth in specific framework areas",
      "Leadership experience should be validated"
    ],
    "decision_notes": "Strong fit candidate. Recommended for interview. Validate cloud deployment, specific frameworks during interview."
  },
  "interview_questions": [
    "Tell me about your experience with React and how you've used it in your most recent role.",
    "Walk us through how you approach solving a complex technical problem.",
    "Describe a situation where you had to lead a team or influence others to achieve a goal.",
    "What's an area where you'd like to grow in this role, and how would you approach it?"
  ]
}
```

### Extract CV Only
```
POST /extract-cv
```

Upload a CV file to extract data without job comparison.

**Request:**
- `file` (form-data, required): PDF, DOCX, or DOC file

**Response:** Same as `cv_data` object from `/analyze` endpoint.

## Data Extraction

### Supported File Formats
- PDF (.pdf)
- Word documents (.docx, .doc)

### Extracted Fields

#### Contact Information
- Name
- Email
- Phone
- Location
- LinkedIn URL
- Personal website

#### Professional Information
- Professional summary
- Work experience (role, company, dates, description)
- Education (degree, institution, field, graduation date, GPA)
- Skills (technical, soft, languages)
- Certifications
- Projects

## Fit Analysis

### Scoring Components

1. **Skills Match (0-100%)**
   - Compares technical and soft skills against job keywords
   - Higher score if more required skills are mentioned

2. **Experience Fit (0-100%)**
   - Analyzes work history for relevant experience
   - Considers role titles, company types, and job descriptions
   - Boosts score for multiple relevant positions

3. **Evidence Quality (0-100%)**
   - Evaluates projects, certifications, education
   - Checks description depth and detail
   - Rewards well-documented experience

4. **Overall Score**
   - Average of the three components

### Strengths & Gaps
- Identifies matching strengths based on scores
- Highlights areas to validate in interview
- Provides actionable feedback

### Interview Questions
- Tailored to CV skills and experience
- Addresses identified gaps
- Focuses on relevant competencies

## Integration with React Frontend

The React app connects to the backend via the `api.ts` module:

```typescript
import { analyzeCv } from './api'

// Usage
const result = await analyzeCv(cvFile, jobDescription)
console.log(result.fit_score)
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid file format, empty file, or missing required fields
- `500 Internal Server Error` - Processing error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Development Notes

### Adding New Extraction Fields

1. Add field to relevant dataclass in `cv_extractor.py`
2. Implement extraction logic in `CVExtractor._extract_*()` method
3. Update response schema if needed
4. Test with sample CVs

### Improving Parsing Accuracy

- Adjust regex patterns in `cv_extractor.py`
- Add more keywords to `TECHNICAL_KEYWORDS` and `SOFT_SKILLS`
- Implement section detection improvements
- Consider adding NLP-based parsing with spaCy for future versions

### Performance Considerations

- File size limit (current: no limit, consider adding 25MB)
- Text extraction is the most resource-intensive operation
- Consider async processing for batch uploads
- Cache common keyword lists

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Multi-language support
- [ ] Salary range estimation
- [ ] Candidate vs job description ranking
- [ ] Batch CV analysis
- [ ] Candidate profile database
- [ ] Advanced NLP for better parsing
- [ ] Resume rewriting suggestions
