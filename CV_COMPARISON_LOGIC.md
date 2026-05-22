# CV-to-Job Comparison Logic - Enhanced Analysis

## How the Analyzer Now Works

The CVPilot analyzer now performs **intelligent role-to-CV comparison** using both the job title and job description to provide context-aware analysis.

### Input Parameters

```
POST /analyze
  - file: CV file (PDF/DOCX/DOC)
  - job_description: Full job description text
  - role_title: Job title/position name (e.g., "Senior Frontend Engineer")
```

### Three-Part Scoring System

#### 1. **Skills Match** (0-100%)
- **What it measures:** How well the candidate's skills align with job requirements
- **How it works:**
  - Extracts keywords from both job title and description
  - Compares against candidate's technical + soft skills
  - Includes both exact matches and partial matches
  - Example: "React" matches "ReactJS" or "React.js"

#### 2. **Experience Fit** (0-100%)
- **What it measures:** How relevant the candidate's work history is to the role
- **How it works:**
  - Checks if candidate has held similar roles
  - Analyzes job descriptions for keyword overlap
  - Considers role title relevance (e.g., "Senior Engineer" for "Senior Developer")
  - Factors in number of years in related positions

#### 3. **Evidence Quality** (0-100%)
- **What it measures:** How well-documented and substantiated the CV is
- **How it works:**
  - Evaluates presence of projects, certifications, education
  - Assesses depth of experience descriptions
  - Checks for concrete evidence of stated skills

### Dynamic Strengths & Gaps

The analyzer now generates strengths and gaps that are **specific to the job**:

#### Example 1: Senior Leadership Role
- **Detected Role:** "Senior Frontend Engineer"
- **Strength:** "Direct experience in senior frontend engineer role"
- **Gap:** "Leadership experience should be validated in interview"

#### Example 2: Cloud-Heavy Role
- **Job Description:** Contains "AWS", "cloud", "deployment"
- **Strength (if matched):** "AWS cloud architecture experience"
- **Gap (if missing):** "Validate practical experience with: AWS, Kubernetes"

### Tailored Interview Questions

Questions are now customized based on:
1. **Role title** - "Tell us about your experience with [specific role]"
2. **Candidate's skills** - "How have you applied [extracted skills]"
3. **Job requirements** - "Describe your work with [required technologies]"
4. **Role type** - Startup vs. Enterprise questions differ
5. **Leadership requirements** - Different questions for management roles

### Example Comparison Flow

```
INPUT:
  CV: "5 years React, worked at startups, no certifications"
  Role: "Senior Frontend Engineer at Enterprise"
  Job: "Need 5+ years, React, TypeScript, AWS, team lead experience"

ANALYSIS:
  ✓ Skills Match: 70% (React ✓, missing TypeScript specifics)
  ✓ Experience Fit: 60% (Years match, but startup ≠ enterprise)
  ✓ Evidence Quality: 50% (No certs, limited projects)

OUTPUT:
  Overall: 60% - "Moderate fit"
  Strengths:
    - Good React experience matches core requirement
    - Startup background shows adaptability
  Gaps:
    - Validate enterprise-scale project experience
    - Leadership team management not evident
    - AWS certification/experience missing

  Questions:
    1. Leadership approach in scaling teams
    2. Enterprise vs. startup differences
    3. AWS infrastructure knowledge
    4. Team mentoring experience
```

## Features Unique to This Comparison

### 1. **Role-Aware Matching**
The system understands that:
- "Frontend Engineer" ≠ "Backend Engineer"
- "Senior Developer" > "Junior Developer"
- "Tech Lead" requires leadership skills

### 2. **Contextual Skill Evaluation**
- "React" for Frontend Engineer is critical
- "React" for DevOps Engineer is a nice-to-have
- Different jobs weight skills differently

### 3. **Experience Mapping**
- Maps candidate roles to required roles
- Considers career progression (Junior → Senior)
- Validates domain expertise (startup vs. enterprise)

### 4. **Smart Gap Detection**
- Identifies missing skills specific to the role
- Suggests validation areas in interview
- Doesn't penalize for irrelevant skills

## API Usage in React

```typescript
import { analyzeCv } from './api'

const result = await analyzeCv(
  cvFile,
  jobDescription,
  roleTitle  // NEW: Include the job title!
)

console.log(result.fit_score.overall_score)      // 75.3
console.log(result.fit_score.strengths)          // Role-specific strengths
console.log(result.interview_questions)          // Role-tailored questions
```

## Configuration

### Add Custom Skills Keywords

Edit `backend/job_fit_analyzer.py`:

```python
TECHNICAL_KEYWORDS = {
    'python', 'javascript',
    'your-new-skill',  # Add here
}
```

### Adjust Scoring Weights

Edit the `analyze()` method:

```python
overall_score = (
    skills_match * 0.4 +      # Weight skills more heavily
    experience_fit * 0.35 +
    evidence_quality * 0.25
) / 3
```

### Customize Role Matching

Edit `_calculate_experience_fit()`:

```python
# Add role aliases
role_aliases = {
    'engineer': ['developer', 'programmer', 'coder'],
    'lead': ['manager', 'senior', 'principal'],
}
```

## Examples of Role-Aware Analysis

### Example: Frontend Developer Role
```
Job Title: "Senior React Developer"
Key Skills: React, TypeScript, REST APIs

CV Result:
✅ Strong React & TypeScript match
⚠️  Validate REST API design patterns
✓ Direct role experience detected
```

### Example: DevOps Role
```
Job Title: "DevOps Engineer"
Key Skills: Kubernetes, Docker, AWS, CI/CD

CV Result:
✅ Docker & CI/CD experience found
⚠️  Kubernetes depth needs validation
✓ Cloud infrastructure experience shown
```

### Example: Manager Role
```
Job Title: "Engineering Manager"
Key Skills: Leadership, Communication, Hiring

CV Result:
✅ Leadership mentioned in CV
✓ Team mentoring experience
⚠️  Hiring/recruitment experience not shown
```

## Best Practices

### For Hiring Managers

1. **Use Specific Job Titles**
   - ✅ "Senior Frontend Engineer"
   - ❌ "Engineer"

2. **Write Clear Job Descriptions**
   - Include must-haves and nice-to-haves
   - Specify technologies and tools
   - Mention soft skills needed

3. **Review Score Context**
   - 80%+ = Strong candidate, consider interviewing
   - 60-80% = Good fit, validate gaps in interview
   - 40-60% = Consider with caution
   - <40% = Significant misalignment

### For Candidates Optimizing CVs

1. **Match the Job Description**
   - Use same terminology as job posting
   - Highlight relevant experience
   - Quantify achievements

2. **Provide Evidence**
   - Add projects demonstrating skills
   - Include certifications
   - Describe your specific contributions

3. **Show Growth**
   - Progress from junior to senior
   - Demonstrate learning and mentoring
   - Show impact on teams/organizations

---

**The analyzer now understands context and provides role-specific recommendations!**
