"""
Job fit analysis module.
Compares CV data against job descriptions to calculate fit scores and identify gaps.
"""

from dataclasses import dataclass
from typing import Optional
import re
from collections import Counter
import math


@dataclass
class FitScore:
    overall_score: float
    skills_match: float
    experience_fit: float
    evidence_quality: float
    strengths: list[str]
    gaps: list[str]
    decision_notes: str


class JobFitAnalyzer:
    """Analyze CV fit against job description and role requirements."""

    # Common technical skills keywords
    TECHNICAL_KEYWORDS = {
        'python', 'javascript', 'typescript', 'java', 'csharp', 'c++', 'c#', 'go', 'rust',
        'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'fastapi',
        'sql', 'nosql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'gitlab',
        'git', 'agile', 'scrum', 'rest', 'graphql', 'api', 'microservices',
        'machine learning', 'ai', 'deep learning', 'tensorflow', 'pytorch', 'numpy', 'pandas'
    }

    def __init__(self, cv_data, job_description: str, role_title: str = ""):
        """
        Initialize analyzer.
        
        Args:
            cv_data: CVData object from extractor
            job_description: Job description text
            role_title: Job title/role name
        """
        self.cv_data = cv_data
        self.job_description = job_description.lower()
        self.role_title = role_title.lower()
        
        # Combine role title and description for comprehensive keyword extraction
        combined_job_text = f"{role_title} {job_description}".lower()
        self.job_keywords = self._extract_keywords(combined_job_text)
        self.role_keywords = self._extract_keywords(role_title) if role_title else set()

    def analyze(self) -> FitScore:
        """Perform fit analysis and return scores."""
        skills_match = self._calculate_skills_match()
        experience_fit = self._calculate_experience_fit()
        evidence_quality = self._calculate_evidence_quality()
        overall_score = (skills_match + experience_fit + evidence_quality) / 3
        
        strengths = self._identify_strengths(skills_match, experience_fit)
        gaps = self._identify_gaps(skills_match, experience_fit)
        decision_notes = self._generate_decision_notes(overall_score, strengths, gaps)

        return FitScore(
            overall_score=overall_score,
            skills_match=skills_match,
            experience_fit=experience_fit,
            evidence_quality=evidence_quality,
            strengths=strengths,
            gaps=gaps,
            decision_notes=decision_notes
        )

    def _extract_keywords(self, text: str) -> set[str]:
        """Extract significant keywords from text."""
        # Remove common words and split into keywords
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'we', 'you', 'i', 'they', 'he', 'she', 'it', 'that', 'this', 'which',
            'will', 'should', 'could', 'would', 'can', 'must', 'may', 'might'
        }
        
        words = re.findall(r'\b[a-z]+(?:[.\-][a-z]+)*\b', text.lower())
        keywords = {w for w in words if len(w) > 2 and w not in stop_words}
        return keywords

    def _calculate_skills_match(self) -> float:
        """Calculate how well CV skills match job requirements."""
        cv_skills = set()
        cv_skills.update(self.cv_data.skills.get('technical', []))
        cv_skills.update(self.cv_data.skills.get('soft', []))
        cv_skills_lower = {s.lower() for s in cv_skills}
        
        job_skills = self.job_keywords
        
        if not job_skills:
            return 50.0
        
        # Count exact matches
        exact_matches = cv_skills_lower & job_skills
        
        # Count partial matches (substring matching for flexibility)
        partial_matches = set()
        for cv_skill in cv_skills_lower:
            for job_skill in job_skills:
                if len(cv_skill) > 3 and len(job_skill) > 3:
                    # Check if either is substring of other
                    if cv_skill in job_skill or job_skill in cv_skill:
                        partial_matches.add(job_skill)
        
        total_matches = len(exact_matches) + len(partial_matches)
        match_percentage = (total_matches / len(job_skills)) * 100
        
        return min(100.0, match_percentage)

    def _calculate_experience_fit(self) -> float:
        """Calculate fit based on work experience and role relevance."""
        if not self.cv_data.experience:
            return 20.0
        
        # Check if CV roles match the target role
        role_keywords = self._extract_keywords(self.role_title) if self.role_title else set()
        
        # Score based on role title similarity
        role_match_score = 0.0
        num_relevant_roles = 0
        
        for exp in self.cv_data.experience:
            exp_role_lower = exp.role.lower()
            
            # Check for direct role title overlap
            if role_keywords:
                for role_kw in role_keywords:
                    if role_kw in exp_role_lower:
                        num_relevant_roles += 1
                        role_match_score += 25.0
                        break
            
            # Check for generic role alignment (engineer, developer, manager, etc.)
            generic_roles = ['engineer', 'developer', 'manager', 'director', 'analyst', 'architect', 'lead']
            if any(role in self.role_title.lower() for role in generic_roles):
                if any(role in exp_role_lower for role in generic_roles):
                    role_match_score += 15.0
        
        # Check experience text against job keywords
        experience_text = ' '.join([
            f"{e.role} {e.company} {e.description or ''}"
            for e in self.cv_data.experience
        ]).lower()
        
        exp_keywords = self._extract_keywords(experience_text)
        job_keywords = self.job_keywords
        
        if not job_keywords:
            return max(50.0, role_match_score)
        
        overlaps = exp_keywords & job_keywords
        experience_match = (len(overlaps) / len(job_keywords)) * 100
        
        # Combine role match and keyword match
        final_score = (experience_match + role_match_score) / 2
        
        return min(100.0, final_score)

    def _calculate_evidence_quality(self) -> float:
        """Calculate quality of evidence (projects, certifications, education)."""
        score = 50.0  # Base score
        
        # Projects that demonstrate skills
        if self.cv_data.projects:
            score += 15.0
        
        # Certifications
        if self.cv_data.certifications:
            score += 15.0
        
        # Education
        if self.cv_data.education:
            score += 10.0
        
        # Description quality in experience
        detailed_roles = sum(
            1 for exp in self.cv_data.experience
            if exp.description and len(exp.description) > 100
        )
        score += min(10, detailed_roles * 3)
        
        return min(100.0, score)

    def _identify_strengths(self, skills_match: float, experience_fit: float) -> list[str]:
        """Identify CV strengths tailored to the job."""
        strengths = []
        
        # Role-specific strengths
        if self.role_title:
            if any(role in ' '.join(exp.role.lower() for exp in self.cv_data.experience) 
                  for role in self.role_title.lower().split()):
                strengths.append(f"Direct experience in {self.role_title} role")
        
        # Strong skills match
        if skills_match > 75:
            strengths.append("Strong alignment with required technical skills")
        elif skills_match > 60:
            strengths.append("Good match with core job requirements")
        
        # Relevant experience
        if experience_fit > 75:
            strengths.append("Highly relevant work background for this role")
        elif experience_fit > 60:
            strengths.append("Solid experience in related positions")
        
        # Technical depth
        tech_count = len(self.cv_data.skills.get('technical', []))
        if tech_count > 8:
            strengths.append(f"Strong technical foundation ({tech_count} technologies)")
        
        # Project portfolio
        if len(self.cv_data.projects) >= 3:
            strengths.append("Demonstrated hands-on project work")
        
        # Certifications
        if len(self.cv_data.certifications) >= 2:
            strengths.append("Professional certifications demonstrate commitment")
        
        # Education
        if any('master' in e.degree.lower() for e in self.cv_data.education):
            strengths.append("Advanced degree adds credibility")
        
        if not strengths:
            strengths.append("Candidate profile available for evaluation")
        
        return strengths[:3]  # Return top 3 strengths

    def _identify_gaps(self, skills_match: float, experience_fit: float) -> list[str]:
        """Identify gaps and areas to validate, tailored to the job."""
        gaps = []
        
        # Extract required skills from job description
        required_technical = [
            skill for skill in self.TECHNICAL_KEYWORDS 
            if skill in self.job_description
        ]
        
        cv_technical = {s.lower() for s in self.cv_data.skills.get('technical', [])}
        missing_skills = [s for s in required_technical if s not in cv_technical]
        
        # Missing critical skills
        if missing_skills and len(missing_skills) > 0:
            gap_text = ', '.join(missing_skills[:2])
            gaps.append(f"Validate practical experience with: {gap_text}")
        
        # Limited experience in area
        if experience_fit < 70:
            gaps.append("Clarify depth of experience in relevant domain areas")
        
        # Role transition validation
        if self.role_title and experience_fit < 60:
            gaps.append(f"Confirm readiness for transition to {self.role_title} role")
        
        # Missing certifications for specialized roles
        specialized_keywords = ['certified', 'certificate', 'certification', 'aws', 'gcp', 'azure']
        if any(kw in self.job_description for kw in specialized_keywords):
            if not self.cv_data.certifications:
                gaps.append("No certifications listed - validate relevant credentials")
        
        # Limited project evidence
        if len(self.cv_data.projects) == 0:
            gaps.append("Add specific project examples demonstrating key skills")
        
        # Soft skills validation (especially for leadership roles)
        if 'lead' in self.role_title.lower() and 'leadership' not in self.cv_data.skills.get('soft', []):
            gaps.append("Leadership experience should be validated in interview")
        
        if not gaps:
            gaps.append("CV well-aligned - focus interview on depth and problem-solving ability")
        
        return gaps[:3]  # Return top 3 gaps

    def _generate_decision_notes(self, score: float, strengths: list[str], gaps: list[str]) -> str:
        """Generate decision summary."""
        if score >= 80:
            level = "Strong fit"
        elif score >= 70:
            level = "Good fit"
        elif score >= 60:
            level = "Moderate fit"
        else:
            level = "Consider carefully"
        
        summary = f"{level} candidate. "
        
        if score >= 70:
            summary += "Recommended for interview. "
        
        # Add validation focus
        if gaps:
            gap_text = ', '.join([g.lower().replace('validate ', '').replace(' in interview', '') for g in gaps[:2]])
            summary += f"Validate {gap_text} during interview."
        
        return summary

    def generate_interview_questions(self) -> list[str]:
        """Generate interview questions tailored to CV, role, and job description."""
        questions = []
        
        # Question 1: Role-specific experience
        if self.role_title:
            questions.append(f"Tell us about your experience with {self.role_title} - what's your greatest achievement in this type of role?")
        elif self.cv_data.skills.get('technical'):
            top_skill = self.cv_data.skills['technical'][0]
            questions.append(f"Describe your most significant project using {top_skill} and the impact you had.")
        else:
            questions.append("What was your biggest achievement in your most recent role?")
        
        # Question 2: Specific skill deep dive
        if 'leadership' in self.role_title.lower() and self.cv_data.experience:
            questions.append("Tell us about a time you had to lead through a challenging situation - how did you handle it?")
        elif self.cv_data.experience:
            questions.append("Walk us through how you approach solving a complex technical problem.")
        
        # Question 3: Job requirement alignment
        required_keywords = list(self.job_keywords)[:3]
        if required_keywords:
            req_text = ', '.join(required_keywords)
            questions.append(f"How have you applied {req_text} in your previous roles?")
        else:
            questions.append("What aspect of this role excites you most based on your background?")
        
        # Question 4: Growth and fit
        questions.append("What's an area in this role where you'd like to grow, and how would you approach it?")
        
        # Question 5: Optional - culture and motivation
        if len(questions) < 5:
            if 'startup' in self.job_description.lower():
                questions.append("Have you worked in a startup environment? What's your experience with fast-paced, dynamic teams?")
            elif 'enterprise' in self.job_description.lower():
                questions.append("Describe your experience working in large, established organizations with complex structures.")
        
        # Remove duplicates and return top 4
        unique_questions = []
        seen = set()
        for q in questions:
            if q not in seen:
                unique_questions.append(q)
                seen.add(q)
        
        return unique_questions[:4]
