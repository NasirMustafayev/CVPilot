"""
CV data extraction module for parsing PDF and DOCX files.
Extracts structured CV data including contact, experience, education, skills, etc.
"""

import re
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ContactInfo:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None


@dataclass
class Experience:
    role: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    duration_months: Optional[int] = None


@dataclass
class Education:
    degree: str
    institution: str
    field: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None


@dataclass
class Certification:
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None


@dataclass
class Project:
    name: str
    description: Optional[str] = None
    technologies: Optional[list[str]] = None


@dataclass
class CVData:
    contact: ContactInfo
    summary: Optional[str] = None
    experience: list[Experience] = None
    education: list[Education] = None
    skills: dict = None
    certifications: list[Certification] = None
    projects: list[Project] = None
    raw_text: str = ""

    def __post_init__(self):
        if self.experience is None:
            self.experience = []
        if self.education is None:
            self.education = []
        if self.skills is None:
            self.skills = {"technical": [], "soft": [], "languages": []}
        if self.certifications is None:
            self.certifications = []
        if self.projects is None:
            self.projects = []


class CVExtractor:
    """Extracts structured data from CV text."""

    # Regex patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}\b'
    LINKEDIN_PATTERN = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
    WEBSITE_PATTERN = r'https?://[^\s]+|www\.[^\s]+'

    # Common soft skills
    SOFT_SKILLS = {
        'communication', 'leadership', 'teamwork', 'problem solving',
        'critical thinking', 'time management', 'collaboration', 'adaptability',
        'creativity', 'interpersonal', 'attention to detail', 'project management',
        'analytical', 'negotiation', 'presentation', 'customer service'
    }

    # Common programming languages & frameworks
    TECHNICAL_KEYWORDS = {
        'python', 'javascript', 'typescript', 'java', 'csharp', 'c++', 'c#', 'go', 'rust',
        'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'fastapi',
        'sql', 'nosql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'gitlab',
        'git', 'agile', 'scrum', 'rest', 'graphql', 'api', 'microservices',
        'machine learning', 'ai', 'deep learning', 'tensorflow', 'pytorch', 'numpy', 'pandas'
    }

    def __init__(self, text: str):
        self.text = text
        self.lines = text.split('\n')
        self.lower_text = text.lower()

    def extract(self) -> CVData:
        """Extract all CV data from text."""
        contact = self._extract_contact()
        summary = self._extract_summary()
        experience = self._extract_experience()
        education = self._extract_education()
        skills = self._extract_skills()
        certifications = self._extract_certifications()
        projects = self._extract_projects()

        return CVData(
            contact=contact,
            summary=summary,
            experience=experience,
            education=education,
            skills=skills,
            certifications=certifications,
            projects=projects,
            raw_text=self.text
        )

    def _extract_contact(self) -> ContactInfo:
        """Extract contact information."""
        contact = ContactInfo()

        # Extract email
        email_match = re.search(self.EMAIL_PATTERN, self.text)
        if email_match:
            contact.email = email_match.group(0)

        # Extract phone
        phone_match = re.search(self.PHONE_PATTERN, self.text)
        if phone_match:
            contact.phone = phone_match.group(0)

        # Extract LinkedIn
        linkedin_match = re.search(self.LINKEDIN_PATTERN, self.text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = linkedin_match.group(0)

        # Extract website
        website_match = re.search(self.WEBSITE_PATTERN, self.text)
        if website_match and 'linkedin' not in website_match.group(0).lower():
            contact.website = website_match.group(0)

        # Extract name (first non-empty line, usually)
        for line in self.lines[:10]:
            line = line.strip()
            if line and len(line) < 100 and not re.match(r'^[a-z0-9._%+-]+@', line, re.IGNORECASE):
                # Heuristic: likely a name if it's short, capitalized, and not an email
                if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', line):
                    contact.name = line
                    break

        return contact

    def _extract_summary(self) -> Optional[str]:
        """Extract professional summary."""
        summary_keywords = ['summary', 'objective', 'professional summary', 'about']
        
        for i, line in enumerate(self.lines):
            if any(keyword in line.lower() for keyword in summary_keywords):
                # Get next few lines as summary
                summary_lines = []
                for j in range(i + 1, min(i + 6, len(self.lines))):
                    line_text = self.lines[j].strip()
                    if line_text and not any(
                        section in line_text.lower() 
                        for section in ['experience', 'education', 'skills', 'certification']
                    ):
                        summary_lines.append(line_text)
                    else:
                        break
                
                if summary_lines:
                    return ' '.join(summary_lines)
        
        return None

    def _extract_experience(self) -> list[Experience]:
        """Extract work experience."""
        experiences = []
        
        # Find experience section
        exp_start = -1
        section_keywords = ['experience', 'work experience', 'professional experience']
        
        for i, line in enumerate(self.lines):
            if any(keyword in line.lower() for keyword in section_keywords):
                exp_start = i
                break
        
        if exp_start == -1:
            return experiences
        
        # Extract until next section
        section_end = len(self.lines)
        next_sections = ['education', 'skills', 'certification', 'project', 'language']
        
        for i in range(exp_start + 1, len(self.lines)):
            if any(section in self.lines[i].lower() for section in next_sections):
                section_end = i
                break
        
        # Parse each job entry
        current_role = None
        current_company = None
        current_dates = None
        current_desc = []
        
        for i in range(exp_start + 1, section_end):
            line = self.lines[i].strip()
            
            if not line:
                continue
            
            # Detect dates (format: "Jan 2022 - Present" or "01/01/2022 - 12/31/2022")
            is_date_line = re.search(r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|present|current|\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4})', line.lower())
            
            # Detect job title (has common job keywords)
            is_job_line = any(
                role in line.lower() 
                for role in ['engineer', 'developer', 'manager', 'designer', 'analyst', 'lead', 'architect', 'director', 'consultant']
            ) and len(line) < 150
            
            if is_job_line:
                if current_role:
                    # Save previous job
                    exp = Experience(
                        role=current_role,
                        company=current_company or '',
                        start_date=self._parse_date_range(current_dates)[0] if current_dates else None,
                        end_date=self._parse_date_range(current_dates)[1] if current_dates else None,
                        description=' '.join(current_desc) if current_desc else None
                    )
                    experiences.append(exp)
                
                # Parse new job (format: "Role at Company" or "Role | Company")
                if ' at ' in line:
                    parts = line.split(' at ', 1)
                    current_role = parts[0].strip()
                    current_company = parts[1].strip()
                elif ' | ' in line:
                    parts = line.split(' | ', 1)
                    current_role = parts[0].strip()
                    current_company = parts[1].strip()
                else:
                    current_role = line
                    current_company = ''
                
                current_dates = None
                current_desc = []
            
            # Detect dates
            elif is_date_line and (current_role or current_company):
                current_dates = line
            
            # Accumulate description (bullet points or regular text)
            elif current_role and line:
                if line.startswith(('•', '-', '*')):
                    # Remove bullet point and add description
                    current_desc.append(line[1:].strip())
                else:
                    current_desc.append(line)
        
        # Add last job
        if current_role:
            exp = Experience(
                role=current_role,
                company=current_company or '',
                start_date=self._parse_date_range(current_dates)[0] if current_dates else None,
                end_date=self._parse_date_range(current_dates)[1] if current_dates else None,
                description=' '.join(current_desc) if current_desc else None
            )
            experiences.append(exp)
        
        return experiences

    def _extract_education(self) -> list[Education]:
        """Extract education."""
        education = []
        
        edu_start = -1
        for i, line in enumerate(self.lines):
            if 'education' in line.lower():
                edu_start = i
                break
        
        if edu_start == -1:
            return education
        
        # Find section end
        section_end = len(self.lines)
        next_sections = ['experience', 'skills', 'certification', 'project', 'language']
        
        for i in range(edu_start + 1, len(self.lines)):
            if any(section in self.lines[i].lower() for section in next_sections):
                section_end = i
                break
        
        # Parse degrees
        degree_keywords = ['bachelor', 'master', 'phd', 'associate', 'b.s.', 'b.a.', 'm.s.', 'm.a.']
        
        for i in range(edu_start + 1, section_end):
            line = self.lines[i].strip()
            
            if any(degree in line.lower() for degree in degree_keywords):
                parts = re.split(r' in | - | at |from', line, flags=re.IGNORECASE)
                degree = parts[0].strip()
                field = parts[1].strip() if len(parts) > 1 else None
                
                # Look for institution and dates nearby
                institution = None
                grad_date = None
                
                if i + 1 < section_end:
                    next_line = self.lines[i + 1].strip()
                    if not any(d in next_line for d in degree_keywords):
                        institution = next_line
                        
                        if i + 2 < section_end:
                            date_line = self.lines[i + 2].strip()
                            if re.search(r'\d{4}', date_line):
                                grad_date = date_line
                
                education.append(Education(
                    degree=degree,
                    institution=institution or '',
                    field=field,
                    graduation_date=grad_date
                ))
        
        return education

    def _extract_skills(self) -> dict:
        """Extract skills."""
        skills = {"technical": [], "soft": [], "languages": []}
        
        # Find skills section
        skills_start = -1
        for i, line in enumerate(self.lines):
            if 'skill' in line.lower():
                skills_start = i
                break
        
        if skills_start == -1:
            # Extract from entire text
            skills_text = self.lower_text
        else:
            # Find section end
            section_end = len(self.lines)
            next_sections = ['experience', 'education', 'certification', 'project', 'language']
            
            for i in range(skills_start + 1, len(self.lines)):
                if any(section in self.lines[i].lower() for section in next_sections):
                    section_end = i
                    break
            
            skills_text = ' '.join(self.lines[skills_start:section_end]).lower()
        
        # Extract technical skills
        for keyword in self.TECHNICAL_KEYWORDS:
            if keyword in skills_text:
                skills["technical"].append(keyword)
        
        # Extract soft skills
        for skill in self.SOFT_SKILLS:
            if skill in skills_text:
                skills["soft"].append(skill)
        
        # Extract languages
        language_keywords = ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'arabic', 'portuguese', 'russian', 'korean']
        for lang in language_keywords:
            if lang in skills_text:
                skills["languages"].append(lang.capitalize())
        
        # Remove duplicates and sort
        skills["technical"] = sorted(list(set(skills["technical"])))
        skills["soft"] = sorted(list(set(skills["soft"])))
        skills["languages"] = sorted(list(set(skills["languages"])))
        
        return skills

    def _extract_certifications(self) -> list[Certification]:
        """Extract certifications."""
        certifications = []
        
        cert_start = -1
        for i, line in enumerate(self.lines):
            if 'certification' in line.lower() or 'certificate' in line.lower():
                cert_start = i
                break
        
        if cert_start == -1:
            return certifications
        
        # Find section end
        section_end = len(self.lines)
        next_sections = ['experience', 'education', 'skills', 'project', 'language']
        
        for i in range(cert_start + 1, len(self.lines)):
            if any(section in self.lines[i].lower() for section in next_sections):
                section_end = i
                break
        
        # Parse certifications
        for i in range(cert_start + 1, section_end):
            line = self.lines[i].strip()
            if line and not line.startswith(('•', '-', '*')):
                parts = line.split(' - ') if ' - ' in line else line.split(' | ') if ' | ' in line else [line]
                cert = Certification(
                    name=parts[0].strip(),
                    issuer=parts[1].strip() if len(parts) > 1 else None,
                    date=parts[2].strip() if len(parts) > 2 else None
                )
                certifications.append(cert)
        
        return certifications

    def _extract_projects(self) -> list[Project]:
        """Extract projects."""
        projects = []
        
        proj_start = -1
        for i, line in enumerate(self.lines):
            if 'project' in line.lower():
                proj_start = i
                break
        
        if proj_start == -1:
            return projects
        
        # Find section end
        section_end = len(self.lines)
        next_sections = ['experience', 'education', 'skills', 'certification', 'language']
        
        for i in range(proj_start + 1, len(self.lines)):
            if any(section in self.lines[i].lower() for section in next_sections):
                section_end = i
                break
        
        # Parse projects (simple parsing)
        current_project = None
        for i in range(proj_start + 1, section_end):
            line = self.lines[i].strip()
            
            if line and re.match(r'^[A-Z].*', line):
                if current_project:
                    projects.append(current_project)
                current_project = Project(name=line)
            elif line and current_project:
                current_project.description = (current_project.description or '') + ' ' + line
        
        if current_project:
            projects.append(current_project)
        
        return projects

    def _parse_date_range(self, date_str: str) -> tuple[Optional[str], Optional[str]]:
        """Parse date range string."""
        if not date_str:
            return None, None
        
        # Try to extract two dates
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}', date_str)
        
        if len(dates) >= 2:
            return dates[0], dates[1]
        elif len(dates) == 1:
            if 'present' in date_str.lower() or 'current' in date_str.lower():
                return dates[0], 'Present'
            return dates[0], None
        
        return None, None
