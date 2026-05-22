# CVPilot Quick Start Guide 🚀

## 30-Second Setup

### Terminal 1: Start Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

✅ Backend ready at `http://localhost:8000`

### Terminal 2: Start Frontend
```bash
npm install
npm run dev
```

✅ Frontend ready at `http://localhost:5173`

---

## Using the App

### Step 1: Prepare Documents
- Have a CV file ready (PDF, DOCX, or DOC)
- Have a job description ready (copy-paste from job posting)
- Optional: Know the job title/role

### Step 2: Upload & Analyze
1. Click file upload → select CV
2. Enter job title (optional but helps)
3. Paste job description
4. Click "Analyze" button
5. See results instantly!

### Step 3: Review Results
- **Fit Scores:** Overall, Skills, Experience, Evidence
- **Strengths:** What matches well
- **Gaps:** What's missing
- **Interview Questions:** Role-specific, custom questions

---

## API Examples

### Example 1: Analyze CV
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@resume.pdf" \
  -F "job_description=Senior Python developer with AWS and React experience" \
  -F "role_title=Senior Backend Engineer"
```

Response:
```json
{
  "fit_scores": {
    "overall": 78,
    "skills_match": 82,
    "experience_fit": 75,
    "evidence_quality": 77
  },
  "strengths": ["Python expertise", "AWS certified", "React experience"],
  "gaps": ["Limited Kubernetes", "No Docker Compose"],
  "interview_questions": [
    "Tell me about your biggest AWS project...",
    "How would you handle Kubernetes deployment?"
  ],
  "cv_data": { ... }
}
```

### Example 2: Extract CV Data Only
```bash
curl -X POST http://localhost:8000/extract-cv \
  -F "file=@resume.pdf"
```

Response:
```json
{
  "contact": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "location": "San Francisco, CA"
  },
  "experience": [
    {
      "role": "Senior Engineer",
      "company": "Tech Corp",
      "dates": "2020-2024",
      "description": "Led team of 5..."
    }
  ],
  "skills": {
    "technical": ["Python", "AWS", "React", "Docker"],
    "soft": ["Leadership", "Communication"]
  },
  ...
}
```

### Example 3: Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## File Formats Supported

✅ **PDF** - Any PDF with text (not scanned images)
✅ **DOCX** - Microsoft Word (.docx files)
✅ **DOC** - Microsoft Word (.doc files)

❌ Image PDFs (scanned documents)
❌ RTF, TXT, Google Docs

---

## Scoring System Explained

### Overall Fit Score (0-100)
Average of three components:
- 40% = Skills Match
- 30% = Experience Fit  
- 30% = Evidence Quality

### Skills Match
CV keywords vs job keywords. How many required skills does candidate have?

### Experience Fit
Did candidate work in similar roles? Do job descriptions match?

### Evidence Quality
Do they have projects, certifications, education to prove skills?

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version (needs 3.8+)
python --version

# Install dependencies again
pip install -r requirements.txt

# Check port 8000 is free
lsof -i :8000
```

### Frontend connection errors
- Make sure backend is running on :8000
- Check CORS in `/backend/main.py`
- Try `http://localhost:8000/health` from browser

### File upload fails
- File size < 25 MB ✓
- File is PDF, DOCX, or DOC ✓
- File has readable text (>50 chars) ✓
- Not corrupted

### Low fit scores
- Job description too specific? Use broader keywords
- CV sections not recognized? Check formatting
- Add job title to get better context
- Try different wording in job description

---

## Tips for Best Results

1. **Add Job Title** - Improves analysis accuracy significantly
2. **Use Full Job Description** - Copy-paste entire description, not just summary
3. **Well-Formatted CV** - Clear sections (Experience, Skills, Education)
4. **Specific Job Descriptions** - More detail = better analysis
5. **Common Keywords** - Use standard titles (Senior Engineer vs L6 IC)

---

## What Gets Extracted

### Contact Information
- Name, Email, Phone, Location
- LinkedIn URL, Website, GitHub

### Experience
- Job Title, Company, Dates
- Job Description/Responsibilities
- Multiple positions supported

### Education
- Degree (BS, MS, MBA, etc.)
- School/University
- Graduation Date
- Field of Study

### Skills
- Technical (Python, JavaScript, AWS, etc.)
- Soft (Leadership, Communication, etc.)
- Languages
- Tools and Frameworks

### Certifications
- AWS Certified Solutions Architect
- PMP, CISSP, etc.
- Training and courses

### Projects
- Personal projects
- Open source contributions
- Side hustles

---

## Architecture at a Glance

```
Frontend (React)
    ↓ (file, job description, role title)
API Client (TypeScript)
    ↓ (HTTP POST)
Backend API (FastAPI)
    ↓
File Parser → CV Extractor → Fit Analyzer
    ↓ (fits scores, strengths, gaps, questions)
API Response
    ↓
Frontend Display
```

---

## Performance

- **PDF Upload:** 0.2-0.5s
- **CV Extraction:** 0.3-1s
- **Fit Analysis:** 0.2-0.5s
- **Total:** < 2 seconds per CV

---

## Next Steps

🎯 **Now you can:**
- Analyze unlimited CVs
- Compare against job descriptions
- Get AI-powered fit scores
- Generate interview questions
- Customize scoring weights

📚 **Want to learn more?**
- `/backend/README.md` - API documentation
- `/CV_COMPARISON_LOGIC.md` - How scoring works
- `/BACKEND_GUIDE.md` - Customization guide
- `/IMPLEMENTATION_COMPLETE.md` - Full documentation

---

**Ready to go? Start both servers and upload a CV!** 🚀
