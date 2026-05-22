# CVPilot CV Analyzer Engine - Quick Start Guide

## 🚀 What You've Built

A complete **CV analysis engine** that:
- ✅ Extracts data from PDF, DOCX, DOC files
- ✅ Parses contact info, skills, experience, education, certifications, projects
- ✅ Calculates job fit scores (0-100%)
- ✅ Identifies strengths and gaps
- ✅ Generates tailored interview questions
- ✅ Provides decision notes for hiring

## 📦 Backend Modules

### 1. **`cv_extractor.py`** - Core extraction engine
- `CVExtractor` class with intelligent pattern matching
- Regex-based parsing for contact info, dates, skills
- Keyword-based section detection
- Supports 60+ technical skills and soft skills

### 2. **`file_parser.py`** - File parsing utilities
- `FileParser.parse_file()` - Auto-detects and parses PDF/DOCX/DOC
- Handles encoding and formatting issues
- Returns clean text for extraction

### 3. **`job_fit_analyzer.py`** - Scoring engine
- `JobFitAnalyzer` class calculates three-part scores:
  - **Skills Match**: Technical + soft skills overlap
  - **Experience Fit**: Relevant work history alignment
  - **Evidence Quality**: Projects, certs, education depth
- Generates strengths, gaps, and interview questions

### 4. **`main.py`** - FastAPI server
- REST API with CORS enabled for React frontend
- Endpoints: `/analyze`, `/extract-cv`, `/health`
- Handles file uploads and returns structured JSON

## 🔧 Setup & Run

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Start server
python main.py

# Server runs on http://localhost:8000
# API Docs: http://localhost:8000/docs (Swagger UI)
```

## 📱 React Integration

The React frontend (`src/api.ts`) connects to the backend:

```typescript
import { analyzeCv } from './api'

// Upload CV and job description
const result = await analyzeCv(cvFile, jobDescription)

// Access results
result.fit_score.overall_score        // 0-100
result.fit_score.strengths             // ["Strong skills...", ...]
result.fit_score.gaps                  // ["Validate...", ...]
result.interview_questions             // 4 tailored questions
result.cv_data.contact.name            // Extracted contact info
result.cv_data.skills.technical        // ["react", "python", ...]
result.cv_data.experience              // [{ role, company, dates, ... }]
```

## 📊 Sample Output

```json
{
  "cv_data": {
    "contact": { "name": "Jane Smith", "email": "jane@example.com", ... },
    "experience": [
      { "role": "Senior Engineer", "company": "TechCorp", "start_date": "2022", ... }
    ],
    "skills": {
      "technical": ["react", "typescript", "python", "aws"],
      "soft": ["leadership", "communication"],
      "languages": ["English", "Spanish"]
    }
  },
  "fit_score": {
    "overall_score": 82.3,
    "skills_match": 85.5,
    "experience_fit": 79.2,
    "evidence_quality": 82.1,
    "strengths": [
      "Strong skills alignment with job requirements",
      "Highly relevant work experience"
    ],
    "gaps": [
      "Validate experience with cloud deployment",
      "Leadership experience should be validated"
    ],
    "decision_notes": "Strong fit candidate. Recommended for interview..."
  },
  "interview_questions": [
    "Tell me about your experience with React...",
    "Walk us through how you approach solving...",
    "Describe a situation where you had to lead...",
    "What's an area where you'd like to grow..."
  ]
}
```

## 🎯 Next Steps for Integration

### 1. Start Backend Server
```bash
cd backend && python main.py
```

### 2. Update React Dashboard to use Backend

The main changes needed in `src/App.tsx`:
- Import `analyzeCv` from `api.ts`
- Add file upload state management
- Call `analyzeCv()` on form submit
- Display real data instead of hardcoded demo data
- Add loading/error states

### 3. Test End-to-End
- Upload a real CV
- Enter job description
- See real extraction and scores

## 🛠️ Customization

### Add New Skills to Extract
Edit `cv_extractor.py`:
```python
TECHNICAL_KEYWORDS = {
    'python', 'javascript', 'solidity', 'rust',  # Add new ones
    ...
}
```

### Adjust Scoring Weights
Edit `job_fit_analyzer.py`:
```python
def analyze(self):
    # Change these weights:
    overall_score = (skills_match + experience_fit + evidence_quality) / 3
```

### Modify Fit Score Rules
Edit the scoring methods in `JobFitAnalyzer`:
- `_calculate_skills_match()` - Adjust skill matching logic
- `_calculate_experience_fit()` - Tweak experience evaluation
- `_calculate_evidence_quality()` - Change evidence scoring

## 📝 Architecture Decisions

| Decision | Why |
|----------|-----|
| FastAPI | Modern, fast, great async support |
| pdfplumber + python-docx | Best open-source PDF/DOCX parsing |
| Regex + Keywords | Fast, no ML overhead, hackathon-friendly |
| Three-part scoring | Captures different dimensions of fit |
| REST API | Simple integration with React frontend |

## ⚡ Performance Notes

- **PDF parsing**: ~1-3 seconds for typical CV
- **Data extraction**: ~200-500ms
- **Fit analysis**: ~100-200ms
- **Total**: ~2-4 seconds per CV

For batch processing, consider:
- Async processing with Celery
- Result caching
- Database storage

## 🐛 Known Limitations

- Doesn't handle heavily formatted/scanned PDFs well (consider OCR)
- Limited to single CV per request
- No handwriting recognition
- Date parsing can be fragile (standardize formats)
- Soft skills detection is keyword-based (not contextual)

## 🚀 Production Checklist

- [ ] Add file size limits (e.g., 25MB max)
- [ ] Implement rate limiting
- [ ] Add request/response logging
- [ ] Use environment variables for config
- [ ] Add database storage for results
- [ ] Implement caching layer
- [ ] Add async processing for large files
- [ ] Security: validate file types, sanitize inputs
- [ ] Deploy with reverse proxy (nginx)
- [ ] Add monitoring and alerting

---

**Built for CVPilot Hackathon** 🎉
