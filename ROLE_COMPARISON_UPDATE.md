# CVPilot CV Analyzer - Role Comparison Enhancement

## What Changed

The CV analyzer now **compares candidate CVs against specific job requirements** using both the job title and job description.

## Key Improvements

### 1. **Role Title Support**
- Added `role_title` parameter to `/analyze` endpoint
- System now understands the specific position you're hiring for
- Enables role-aware skill matching and gap analysis

### 2. **Smart Skill Matching**
- Keywords extracted from both job title AND job description
- Matches candidate skills against role requirements
- Handles variants: "React" matches "React.js", "ReactJS", etc.
- Calculates skills match score (0-100%) for the specific role

### 3. **Experience Fit by Role**
- Checks if candidate held similar positions
- Validates role progression (Junior → Senior)
- Considers domain experience (startup vs. enterprise)
- Compares with specific role requirements

### 4. **Role-Specific Strengths & Gaps**
- Strengths are now tailored to the job
- Gaps highlight areas specific to this role
- Interview questions target role requirements

### 5. **Context-Aware Interview Questions**
- Questions reference the specific role
- Validate role-critical skills
- Consider role type (management vs. IC, startup vs. enterprise)

## Usage

### In the UI
When using CVPilot Dashboard:

1. **HR Mode - Candidate Analysis:**
   - Enter the role title: "Senior Frontend Engineer"
   - Enter job description with requirements
   - Upload candidate CV
   - Get analysis specific to that position

2. **Candidate Mode - Self-Assessment:**
   - Enter target role: "Senior Frontend Engineer"
   - Paste job description from job posting
   - Upload your CV
   - Get feedback on fit for this role

### In the API

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@cv.pdf" \
  -F "role_title=Senior Frontend Engineer" \
  -F "job_description=We need a Senior Frontend Engineer with React, TypeScript, and AWS experience..."
```

### In React Code

```typescript
import { analyzeCv } from './api'

// Now includes role_title
const result = await analyzeCv(
  cvFile,
  jobDescription,
  roleTitle  // "Senior Frontend Engineer"
)

console.log(result.fit_score.overall_score)      // Score for THIS role
console.log(result.fit_score.strengths)          // Role-specific strengths
console.log(result.interview_questions)          // Role-tailored questions
```

## Examples

### Example 1: Exact Role Match
```
Position: Senior Frontend Engineer
Requirements: React, TypeScript, AWS, Leadership, 5+ years

Candidate CV:
  - Senior React Developer for 6 years
  - Led team of 4
  - AWS infrastructure work
  - Strong TypeScript background

Result:
  Overall: 88%
  Strengths:
    ✓ Direct experience in senior frontend engineer role
    ✓ Strong React and TypeScript expertise
    ✓ AWS cloud architecture experience
  Gaps:
    ⚠️ Validate leadership at scale
    ⚠️ Confirm AWS certification
  Questions:
    1. "Tell us about your experience leading frontend teams..."
    2. "How do you approach React architecture..."
```

### Example 2: Career Transition
```
Position: Senior DevOps Engineer
Requirements: Kubernetes, Docker, AWS, Python, CI/CD

Candidate CV:
  - 5 years Backend Developer
  - Docker and CI/CD experience
  - Some Python scripting
  - No Kubernetes mentioned

Result:
  Overall: 52%
  Strengths:
    ✓ Docker and CI/CD knowledge
    ✓ Python scripting skills
  Gaps:
    ⚠️ Kubernetes orchestration not demonstrated
    ⚠️ DevOps-specific AWS tools unclear
    ⚠️ No infrastructure-as-code examples
  Questions:
    1. "What's your Kubernetes experience?"
    2. "How would you transition from backend to DevOps?"
    3. "AWS infrastructure management experience?"
    4. "CI/CD pipeline design at scale?"
```

## Technical Details

### Updated Endpoints

**POST /analyze** (Enhanced)
```
Parameters:
  - file (required): CV file
  - job_description (required): Job requirements
  - role_title (optional): Job title/position

Response includes:
  - fit_score with 3-part breakdown
  - role-specific strengths
  - role-specific gaps
  - tailored interview questions
```

### Backend Changes

- `backend/main.py`: Added `role_title` parameter
- `backend/job_fit_analyzer.py`: 
  - Accepts `role_title` in constructor
  - Enhanced `_calculate_skills_match()` with context
  - Enhanced `_calculate_experience_fit()` for role relevance
  - Improved `_identify_strengths()` and `_identify_gaps()`
  - Better `generate_interview_questions()` with role context

### Frontend Changes

- `src/api.ts`: Updated `analyzeCv()` to include `roleTitle` parameter

## Configuration

### Customize Role Matching

Edit `backend/job_fit_analyzer.py`:

```python
# Add role aliases for better matching
role_aliases = {
    'engineer': ['developer', 'programmer', 'coder'],
    'lead': ['manager', 'senior', 'principal'],
}

# Customize what constitutes a "relevant" role
relevant_roles = ['engineer', 'developer', 'architect']
```

### Adjust Scoring Formula

```python
# Current formula:
overall_score = (skills_match + experience_fit + evidence_quality) / 3

# You can change weights:
overall_score = (
    skills_match * 0.4 +      # Weight skills more
    experience_fit * 0.35 +
    evidence_quality * 0.25
) / 3
```

## Benefits

✅ **Better Hiring Decisions**
   - Compare candidates fairly for the specific role
   - Identify critical skill gaps early

✅ **Improved Candidate Feedback**
   - Candidates see how well they fit a specific role
   - Get actionable feedback on what to improve

✅ **Smarter Interview Questions**
   - Questions target role-critical skills
   - Validate exactly what the role needs

✅ **Role Flexibility**
   - Same system works for different roles
   - Hiring managers don't need multiple tools

## Files Changed

```
backend/main.py                 - Added role_title parameter
backend/job_fit_analyzer.py     - Enhanced comparison logic
src/api.ts                      - Updated function signature
backend/README.md               - Updated documentation
CV_COMPARISON_LOGIC.md          - NEW: Detailed explanation
ROLE_COMPARISON_UPDATE.md       - This file
```

## Next Steps

1. **Integrate Role Title in React UI**
   - Update Dashboard to capture role_title
   - Pass to analyzeCv() function

2. **Test with Real Job Postings**
   - Try different roles
   - Verify scores make sense
   - Adjust scoring if needed

3. **Optimize for Your Use Cases**
   - Add domain-specific keywords
   - Customize role aliases
   - Adjust weights based on priorities

## Backward Compatibility

- The `role_title` parameter is optional
- If not provided, system still works with just job_description
- Existing code continues to work without changes

## Support

For questions or issues:
- Check `CV_COMPARISON_LOGIC.md` for detailed examples
- Review `backend/README.md` for API specs
- See `QUICK_REFERENCE.md` for quick usage guide

---

**Your CV analyzer is now role-aware and ready to compare candidates against specific job requirements!**
