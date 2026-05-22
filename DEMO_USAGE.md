# CVPilot CV Analyzer - Demo Usage Guide

## Quick Start (5 minutes)

### 1. Start the Backend Server

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test the API (Optional)

Open in your browser or use curl:
```bash
# Health check
curl http://localhost:8000/health

# Swagger UI (interactive API docs)
http://localhost:8000/docs
```

### 3. Prepare Test Files

Create a sample CV file (or use an existing one):
- PDF, DOCX, or DOC format
- Any typical resume/CV

### 4. Test with curl (Optional)

```bash
# Test CV extraction
curl -X POST http://localhost:8000/extract-cv \
  -F "file=@path/to/your/cv.pdf"

# Test full analysis
curl -X POST http://localhost:8000/analyze \
  -F "file=@path/to/your/cv.pdf" \
  -F "job_description=Senior Frontend Engineer with React and TypeScript experience. Must have AWS knowledge."
```

### 5. Integrate with React (Next)

Update `src/App.tsx` to use the backend:

```typescript
import { analyzeCv } from './api'

// In your form submit handler:
const handleAnalyze = async () => {
  try {
    const result = await analyzeCv(cvFile, jobDescription)
    setFitScore(result.fit_score)
    setInterviewQuestions(result.interview_questions)
    setCvData(result.cv_data)
  } catch (error) {
    console.error('Analysis failed:', error)
  }
}
```

## Example Response

When you upload a CV and job description, you get back:

```json
{
  "cv_data": {
    "contact": {
      "name": "Sarah Johnson",
      "email": "sarah@example.com",
      "phone": "(555) 123-4567",
      "location": "San Francisco, CA",
      "linkedin": "linkedin.com/in/sarahjohnson"
    },
    "summary": "Experienced React developer with 6+ years...",
    "experience": [
      {
        "role": "Senior Frontend Engineer",
        "company": "Tech Startup Inc",
        "start_date": "2021",
        "end_date": "Present",
        "description": "Led team of 5 developers building React components..."
      }
    ],
    "education": [
      {
        "degree": "Bachelor of Science",
        "institution": "UC Berkeley",
        "field": "Computer Science",
        "graduation_date": "2018"
      }
    ],
    "skills": {
      "technical": ["react", "typescript", "javascript", "aws", "docker"],
      "soft": ["leadership", "communication", "mentoring"],
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
        "name": "E-commerce Dashboard",
        "description": "Built real-time analytics dashboard...",
        "technologies": ["React", "Node.js", "PostgreSQL"]
      }
    ]
  },
  "fit_score": {
    "overall_score": 87.3,
    "skills_match": 92.0,
    "experience_fit": 84.5,
    "evidence_quality": 85.4,
    "strengths": [
      "Strong React and TypeScript expertise matches job perfectly",
      "AWS experience aligns well with cloud infrastructure role",
      "Leadership experience demonstrated with team mentoring"
    ],
    "gaps": [
      "Validate depth of Kubernetes knowledge for orchestration work",
      "Clarify production deployment experience at scale",
      "Confirm AWS certifications match current requirements"
    ],
    "decision_notes": "Strong fit candidate. Recommended for interview. Validate Kubernetes experience and production deployment scale during interview."
  },
  "interview_questions": [
    "Tell me about your experience with React and TypeScript - what's the most complex component architecture you've built?",
    "Describe your experience with AWS - which services have you worked with most and why?",
    "Walk us through a challenging problem you solved leading a development team.",
    "What's your approach to keeping up with the rapidly changing frontend ecosystem?"
  ]
}
```

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] Health endpoint responds: `GET /health`
- [ ] Can upload a PDF file via `/analyze`
- [ ] Receives JSON response with fit scores
- [ ] Interview questions are specific and relevant
- [ ] Skills extraction includes technical keywords
- [ ] Experience is parsed with company and role
- [ ] Education section is populated
- [ ] Strengths and gaps make sense

## Troubleshooting

### "Connection refused" error
- Backend server not running
- Solution: Run `python main.py` in backend folder

### "File format not supported"
- Only PDF, DOCX, DOC supported
- Solution: Convert file or use supported format

### "Empty or invalid file" error
- File is corrupted or too large
- Solution: Try different file or reduce size

### "Failed to parse file"
- Text extraction failed
- Solution: Try re-saving file in PDF format

### CORS errors in browser
- FastAPI CORS not configured for your origin
- Solution: Update CORS settings in `main.py` if needed

## Performance Notes

- First analysis takes ~3-5 seconds (imports load)
- Subsequent analyses take ~2-3 seconds
- Larger PDFs (10+ pages) may take longer
- This is normal for text extraction

## API Limits (Development)

- No file size limit (add in production)
- No rate limiting (add in production)
- No authentication (add in production)

## Next Steps

1. **Complete React Integration**
   - Update Dashboard component
   - Add loading states
   - Display real data

2. **Add Validation**
   - File size checks
   - Input sanitization
   - Error messages

3. **Deploy**
   - Containerize with Docker
   - Use production ASGI server
   - Add reverse proxy (nginx)
   - Enable SSL/HTTPS

---

**Need help?** Check:
- `backend/README.md` - API documentation
- `BACKEND_GUIDE.md` - Architecture & customization
- `backend/main.py` - FastAPI code
