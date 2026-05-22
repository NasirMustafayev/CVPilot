"""
CV data extraction module — structured parsing from plain text with improved heuristics.
"""

import re
from typing import Optional
from dataclasses import dataclass

from skills_vocab import find_soft_skills, find_technical_skills

LANGUAGE_KEYWORDS = (
    "english",
    "spanish",
    "french",
    "german",
    "chinese",
    "japanese",
    "arabic",
    "portuguese",
    "russian",
    "korean",
    "azerbaijani",
    "turkish",
)

DATE_RANGE_RE = re.compile(
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{2,4}"
    r"|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
    r"|\d{4}\s*[-–—]\s*(?:\d{4}|present|current|now)"
    r"|present|current",
    re.IGNORECASE,
)

JOB_TITLE_HINTS = (
    "engineer",
    "developer",
    "manager",
    "designer",
    "analyst",
    "lead",
    "architect",
    "director",
    "consultant",
    "specialist",
    "coordinator",
    "administrator",
    "intern",
    "associate",
    "scientist",
    "researcher",
)


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
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    PHONE_PATTERN = (
        r"(?:\+?\d{1,3}[\s\-.]?)?"
        r"(?:\(?\d{2,4}\)?[\s\-.]?)?"
        r"\d{2,4}[\s\-.]?\d{2,4}[\s\-.]?\d{2,9}\b"
    )
    LINKEDIN_PATTERN = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?"
    WEBSITE_PATTERN = r"https?://[^\s]+|www\.[^\s]+"

    def __init__(self, text: str):
        self.text = text.replace("\r\n", "\n").replace("\r", "\n")
        self.lines = [ln.strip() for ln in self.text.split("\n")]
        self.lower_text = self.text.lower()

    def extract(self) -> CVData:
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
            raw_text=self.text,
        )

    def _extract_contact(self) -> ContactInfo:
        contact = ContactInfo()

        email_match = re.search(self.EMAIL_PATTERN, self.text)
        if email_match:
            contact.email = email_match.group(0)

        phone_match = re.search(self.PHONE_PATTERN, self.text)
        if phone_match:
            contact.phone = phone_match.group(0).strip()

        linkedin_match = re.search(self.LINKEDIN_PATTERN, self.text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = linkedin_match.group(0)

        website_match = re.search(self.WEBSITE_PATTERN, self.text)
        if website_match and "linkedin" not in website_match.group(0).lower():
            contact.website = website_match.group(0)

        for line in self.lines[:15]:
            if not line or len(line) > 80:
                continue
            if contact.email and contact.email in line:
                continue
            if re.search(self.EMAIL_PATTERN, line):
                continue
            if re.search(self.PHONE_PATTERN, line):
                continue
            if "linkedin" in line.lower() or line.lower().startswith("http"):
                continue
            if re.match(r"^[A-Z][\w\-'.]+(?:\s+[A-Z][\w\-'.]+){0,4}$", line):
                contact.name = line
                break
            if not contact.name and 2 <= len(line.split()) <= 5:
                contact.name = line
                break

        for line in self.lines[:20]:
            if re.search(r"\b(?:city|remote|hybrid)\b", line, re.I):
                contact.location = line
                break
            if re.search(
                r"[A-Z][a-z]+,\s*[A-Z]{2}\b|[A-Z][a-z]+,\s*[A-Z][a-z]+",
                line,
            ):
                contact.location = line
                break

        return contact

    def _extract_summary(self) -> Optional[str]:
        summary_keywords = (
            "summary",
            "objective",
            "professional summary",
            "profile",
            "about me",
            "about",
        )

        for i, line in enumerate(self.lines):
            lower = line.lower()
            if any(kw == lower or kw in lower for kw in summary_keywords):
                summary_lines = []
                for j in range(i + 1, min(i + 8, len(self.lines))):
                    line_text = self.lines[j]
                    if not line_text:
                        if summary_lines:
                            break
                        continue
                    if self._is_section_header(line_text):
                        break
                    summary_lines.append(line_text)
                if summary_lines:
                    return " ".join(summary_lines)
        return None

    def _is_section_header(self, line: str) -> bool:
        lower = line.lower().strip()
        headers = (
            "experience",
            "work experience",
            "employment",
            "education",
            "skills",
            "certification",
            "projects",
            "languages",
        )
        return any(h == lower or lower.startswith(h + " ") for h in headers)

    def _section_bounds(self, start_keywords: tuple[str, ...], stop_keywords: tuple[str, ...]) -> tuple[int, int]:
        start = -1
        for i, line in enumerate(self.lines):
            lower = line.lower()
            if any(kw in lower for kw in start_keywords):
                start = i
                break
        if start == -1:
            return -1, -1

        end = len(self.lines)
        for i in range(start + 1, len(self.lines)):
            lower = self.lines[i].lower()
            if any(kw in lower for kw in stop_keywords) and self._is_section_header(self.lines[i]):
                end = i
                break
        return start, end

    def _extract_experience(self) -> list[Experience]:
        experiences = []
        start, end = self._section_bounds(
            ("experience", "work experience", "employment history", "professional experience"),
            ("education", "skills", "certification", "project", "language", "reference"),
        )

        if start >= 0:
            experiences = self._parse_experience_block(start + 1, end)

        if not experiences:
            experiences = self._parse_experience_by_dates()

        return experiences

    def _parse_experience_block(self, start: int, end: int) -> list[Experience]:
        experiences: list[Experience] = []
        current_role: Optional[str] = None
        current_company: Optional[str] = None
        current_dates: Optional[str] = None
        current_desc: list[str] = []

        def flush():
            nonlocal current_role, current_company, current_dates, current_desc
            if current_role:
                s, e = self._parse_date_range(current_dates)
                experiences.append(
                    Experience(
                        role=current_role,
                        company=current_company or "",
                        start_date=s,
                        end_date=e,
                        description=" ".join(current_desc) if current_desc else None,
                    )
                )
            current_role = None
            current_company = None
            current_dates = None
            current_desc = []

        for i in range(start, end):
            line = self.lines[i]
            if not line:
                continue

            is_date_line = bool(DATE_RANGE_RE.search(line))
            is_job_line = (
                any(hint in line.lower() for hint in JOB_TITLE_HINTS)
                or " at " in line.lower()
                or " | " in line
                or " — " in line
            ) and len(line) < 160 and not is_date_line

            if is_job_line:
                flush()
                if " at " in line:
                    parts = re.split(r"\s+at\s+", line, maxsplit=1, flags=re.I)
                    current_role = parts[0].strip()
                    current_company = parts[1].strip() if len(parts) > 1 else ""
                elif " | " in line:
                    parts = line.split(" | ", 1)
                    current_role = parts[0].strip()
                    current_company = parts[1].strip()
                elif " — " in line or " – " in line:
                    parts = re.split(r"\s+[—–]\s+", line, maxsplit=1)
                    current_role = parts[0].strip()
                    current_company = parts[1].strip() if len(parts) > 1 else ""
                else:
                    current_role = line
                    current_company = ""
            elif is_date_line and current_role:
                current_dates = line
            elif current_role:
                if line.startswith(("•", "-", "*", "·")):
                    current_desc.append(line.lstrip("•-*· ").strip())
                elif not is_date_line:
                    current_desc.append(line)

        flush()
        return experiences

    def _parse_experience_by_dates(self) -> list[Experience]:
        """Fallback: anchor entries on date-range lines."""
        experiences: list[Experience] = []
        for i, line in enumerate(self.lines):
            if not DATE_RANGE_RE.search(line):
                continue
            role_line = ""
            company_line = ""
            desc_parts: list[str] = []
            if i > 0:
                role_line = self.lines[i - 1]
            if i > 1 and len(self.lines[i - 2]) < 120:
                prev = self.lines[i - 2]
                if any(h in prev.lower() for h in JOB_TITLE_HINTS):
                    role_line = prev
                    company_line = self.lines[i - 1]
            for j in range(i + 1, min(i + 6, len(self.lines))):
                nxt = self.lines[j]
                if not nxt or DATE_RANGE_RE.search(nxt) or self._is_section_header(nxt):
                    break
                desc_parts.append(nxt)
            if role_line:
                role, company = role_line, company_line
                if " at " in role_line.lower():
                    parts = re.split(r"\s+at\s+", role_line, maxsplit=1, flags=re.I)
                    role, company = parts[0].strip(), parts[1].strip()
                s, e = self._parse_date_range(line)
                experiences.append(
                    Experience(
                        role=role,
                        company=company or "",
                        start_date=s,
                        end_date=e,
                        description=" ".join(desc_parts) if desc_parts else None,
                    )
                )
        return experiences[:12]

    def _extract_education(self) -> list[Education]:
        education: list[Education] = []
        start, end = self._section_bounds(
            ("education", "academic"),
            ("experience", "skills", "certification", "project", "language"),
        )
        if start < 0:
            return education

        degree_keywords = (
            "bachelor",
            "master",
            "phd",
            "doctorate",
            "associate",
            "b.s.",
            "b.a.",
            "m.s.",
            "m.a.",
            "mba",
            "b.sc",
            "m.sc",
        )

        for i in range(start + 1, end):
            line = self.lines[i]
            if not line:
                continue
            if any(deg in line.lower() for deg in degree_keywords):
                parts = re.split(r"\s+in\s+|\s+-\s+|\s+at\s+|\s+from\s+", line, maxsplit=2, flags=re.I)
                degree = parts[0].strip()
                field = parts[1].strip() if len(parts) > 1 else None
                institution = ""
                grad_date = None
                if i + 1 < end:
                    nxt = self.lines[i + 1]
                    if not any(d in nxt.lower() for d in degree_keywords):
                        institution = nxt
                        if i + 2 < end and re.search(r"\d{4}", self.lines[i + 2]):
                            grad_date = self.lines[i + 2]
                education.append(
                    Education(
                        degree=degree,
                        institution=institution,
                        field=field,
                        graduation_date=grad_date,
                    )
                )
        return education

    def _extract_skills(self) -> dict:
        skills = {"technical": [], "soft": [], "languages": []}

        start, end = self._section_bounds(
            ("skills", "technical skills", "core competencies", "technologies"),
            ("experience", "education", "certification", "project", "language"),
        )

        section_text = (
            "\n".join(self.lines[start:end]) if start >= 0 else self.text
        )
        full_text = self.text

        technical = find_technical_skills(section_text)
        if len(technical) < 3:
            technical = find_technical_skills(full_text)

        soft = find_soft_skills(section_text)
        if not soft:
            soft = find_soft_skills(full_text)

        lang_text = section_text.lower()
        if start < 0:
            lang_start, lang_end = self._section_bounds(
                ("languages", "language"),
                ("experience", "education", "skills", "certification", "project"),
            )
            if lang_start >= 0:
                lang_text = "\n".join(self.lines[lang_start:lang_end]).lower()

        languages = []
        for lang in LANGUAGE_KEYWORDS:
            if re.search(rf"\b{lang}\b", lang_text):
                languages.append(lang.capitalize())

        skills["technical"] = technical
        skills["soft"] = soft
        skills["languages"] = sorted(set(languages))
        return skills

    def _extract_certifications(self) -> list[Certification]:
        certifications: list[Certification] = []
        start, end = self._section_bounds(
            ("certification", "certificate", "licenses"),
            ("experience", "education", "skills", "project", "language"),
        )
        if start < 0:
            return certifications

        for i in range(start + 1, end):
            line = self.lines[i]
            if line and not line.startswith(("•", "-", "*")):
                parts = (
                    line.split(" - ")
                    if " - " in line
                    else line.split(" | ")
                    if " | " in line
                    else [line]
                )
                certifications.append(
                    Certification(
                        name=parts[0].strip(),
                        issuer=parts[1].strip() if len(parts) > 1 else None,
                        date=parts[2].strip() if len(parts) > 2 else None,
                    )
                )
        return certifications

    def _extract_projects(self) -> list[Project]:
        projects: list[Project] = []
        start, end = self._section_bounds(
            ("projects", "personal projects", "selected projects"),
            ("experience", "education", "skills", "certification", "language"),
        )
        if start < 0:
            return projects

        current: Optional[Project] = None
        for i in range(start + 1, end):
            line = self.lines[i]
            if not line:
                continue
            if line.startswith(("•", "-", "*")) and current:
                current.description = (
                    (current.description or "") + " " + line.lstrip("•-* ").strip()
                ).strip()
            elif re.match(r"^[A-Z0-9]", line) and len(line) < 120:
                if current:
                    projects.append(current)
                current = Project(name=line)
            elif current:
                current.description = (
                    (current.description or "") + " " + line
                ).strip()
        if current:
            projects.append(current)
        return projects

    def _parse_date_range(self, date_str: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        if not date_str:
            return None, None
        dates = re.findall(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}", date_str)
        if len(dates) >= 2:
            return dates[0], dates[1]
        if len(dates) == 1:
            if re.search(r"present|current|now", date_str, re.I):
                return dates[0], "Present"
            return dates[0], None
        return None, None
