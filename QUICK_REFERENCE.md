# CVPilot CV Analyzer - Quick Reference Card

## 🚀 Start the Engine

```bash
cd backend && python main.py
```

## 📡 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/analyze` | POST | Full CV analysis |
| `/extract-cv` | POST | Extract CV data only |

## 📝 Request Examples

### Full Analysis
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@cv.pdf" \
  -F "job_description=Senior React Developer needed"
```

### Extract Only
```bash
curl -X POST http://localhost:8000/extract-cv \
  -F "file=@cv.pdf"
```

## 💻 React Integration

```typescript
import { analyzeCv } from './api'

const result = await analyzeCv(cvFile, jobDescription)
console.log(result.fit_score.overall_score)        // 82.3
console.log(result.fit_score.strengths)            // ["Strong React skills", ...]
console.log(result.interview_questions)            // 4 questions
```

## 📊 Response Structure

```json
{
  "cv_data": {
    "contact": { /* Contact info */ },
    "experience": [ /* Array of jobs */ ],
    "education": [ /* Array of degrees */ ],
    "skills": { "technical": [...], "soft": [...] },
    "certifications": [ /* Certifications */ ],
    "projects": [ /* Projects */ ]
  },
  "fit_score": {
    "overall_score": 82.3,
    "skills_match": 85.5,
    "experience_fit": 79.2,
    "evidence_quality": 82.1,
    "strengths": ["...", "...", "..."],
    "gaps": ["...", "...", "..."],
    "decision_notes": "..."
  },
  "interview_questions": ["Q1", "Q2", "Q3", "Q4"]
}
```

## 🔑 Key Data Fields

### Contact
- name, email, phone, location, linkedin, website

### Experience
- role, company, start_date, end_date, description

### Education
- degree, institution, field, graduation_date, gpa

### Skills
- technical: ["python", "react", ...] (18+ keywords)
- soft: ["leadership", ...] (16+ keywords)
- languages: ["English", "Spanish"]

### Scoring
- overall_score: 0-100% (average)
- skills_match: 0-100% (keyword overlap)
- experience_fit: 0-100% (relevance)
- evidence_quality: 0-100% (depth)

## ⚙️ Configuration

Update `backend/main.py` to adjust:
- API port: `uvicorn.run(..., port=8000)`
- CORS origins: `app.add_middleware(..., allow_origins=[...])`
- Upload limits: Add file size validation

## 📚 Documentation

| File | Purpose |
|------|---------|
| `BACKEND_GUIDE.md` | Architecture & customization |
| `DEMO_USAGE.md` | Usage examples & troubleshooting |
| `backend/README.md` | Full API reference |

## 🛠️ Customization

### Add Technical Skills
Edit `backend/cv_extractor.py`:
```python
TECHNICAL_KEYWORDS = {
    'python', 'javascript', 'solidity',  # Add here
    ...
}
```

### Adjust Scoring
Edit `backend/job_fit_analyzer.py`:
```python
def analyze(self):
    overall_score = (skills_match + experience_fit + evidence_quality) / 3
    # Change weights above
```

### Modify Fit Thresholds
```python
if skills_match > 75:  # Change threshold
    strengths.append("Strong skills alignment")
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Start backend: `python main.py` |
| File not supported | Use PDF, DOCX, or DOC format |
| Empty file error | File is corrupted or empty |
| CORS error | Update CORS in `main.py` |

## 📊 Performance

| Operation | Time |
|-----------|------|
| PDF extraction | 1-3s |
| Data parsing | 200-500ms |
| Fit analysis | 100-200ms |
| **Total per CV** | **2-4 seconds** |

## 🔗 Supported File Types

✅ PDF (.pdf) - pdfplumber  
✅ Word (.docx) - python-docx  
✅ Word (.doc) - basic support  

## 📋 File Locations

```
backend/
├── main.py              ← Start here
├── cv_extractor.py      ← Core logic
├── file_parser.py       ← File parsing
├── job_fit_analyzer.py  ← Scoring
└── requirements.txt

src/
└── api.ts              ← React client
```

## 📦 Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
pdfplumber==0.10.3
python-docx==0.8.11
```

Install: `pip install -r backend/requirements.txt`

## 🎯 Common Tasks

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Swagger UI
http://localhost:8000/docs
```

### Extract Data
```python
from backend.cv_extractor import CVExtractor
cv = CVExtractor(text).extract()
print(cv.contact.name)
print(cv.skills['technical'])
```

### Analyze Fit
```python
from backend.job_fit_analyzer import JobFitAnalyzer
analyzer = JobFitAnalyzer(cv_data, job_desc)
score = analyzer.analyze()
print(score.overall_score)
```

## 🚀 Next Steps

1. Start backend: `python main.py`
2. Test API: `http://localhost:8000/docs`
3. Update React: Import `analyzeCv` from `api.ts`
4. Display results: Replace demo data with API responses
5. Add UI polish: Loading states, error messages

---

**For detailed info:** See `BACKEND_GUIDE.md`  
**For examples:** See `DEMO_USAGE.md`  
**For API specs:** See `backend/README.md`
