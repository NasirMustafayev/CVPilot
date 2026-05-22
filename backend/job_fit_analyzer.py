"""
Job fit analysis — requirement-focused scoring with evidence from CV text.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from skills_vocab import (
    ROLE_TOKENS,
    extract_role_keywords,
    find_soft_skills,
    find_technical_skills,
    job_required_technical,
    normalize_skill_token,
)


@dataclass
class FitScore:
    overall_score: float
    skills_match: float
    experience_fit: float
    evidence_quality: float
    strengths: list[str]
    gaps: list[str]
    decision_notes: str
    matched_skills: list[str]
    missing_skills: list[str]
    analysis_mode: str = "rules"


class JobFitAnalyzer:
    WEIGHT_SKILLS = 0.45
    WEIGHT_EXPERIENCE = 0.35
    WEIGHT_EVIDENCE = 0.20

    def __init__(self, cv_data, job_description: str, role_title: str = ""):
        self.cv_data = cv_data
        self.job_description = job_description.strip()
        self.role_title = role_title.strip()
        self.job_text = f"{self.role_title}\n{self.job_description}".strip()
        self.job_text_lower = self.job_text.lower()

        self.required_technical = job_required_technical(self.job_text)
        self.role_keywords = extract_role_keywords(self.role_title)
        self.experience_blob = self._experience_blob()
        self.cv_technical = self._collect_cv_technical_skills()
        self.cv_soft = set(
            normalize_skill_token(s)
            for s in (cv_data.skills or {}).get("soft", [])
        )

    def _collect_cv_technical_skills(self) -> set[str]:
        skills: set[str] = set()
        for s in (self.cv_data.skills or {}).get("technical", []):
            skills.add(normalize_skill_token(s))
        for s in find_technical_skills(self.experience_blob):
            skills.add(normalize_skill_token(s))
        for s in find_technical_skills(self.cv_data.raw_text or ""):
            skills.add(normalize_skill_token(s))
        for proj in self.cv_data.projects or []:
            blob = f"{proj.name} {proj.description or ''}"
            for s in find_technical_skills(blob):
                skills.add(normalize_skill_token(s))
        return skills

    def _experience_blob(self) -> str:
        parts = []
        for exp in self.cv_data.experience or []:
            parts.append(
                f"{exp.role} {exp.company} {exp.description or ''}"
            )
        return " ".join(parts)

    def analyze(self) -> FitScore:
        matched, missing = self._skill_alignment()
        skills_match = self._calculate_skills_match(matched, missing)
        experience_fit = self._calculate_experience_fit()
        evidence_quality = self._calculate_evidence_quality()
        overall = (
            skills_match * self.WEIGHT_SKILLS
            + experience_fit * self.WEIGHT_EXPERIENCE
            + evidence_quality * self.WEIGHT_EVIDENCE
        )

        strengths = self._identify_strengths(skills_match, experience_fit, matched)
        gaps = self._identify_gaps(skills_match, experience_fit, missing)
        decision_notes = self._generate_decision_notes(overall, strengths, gaps, missing)

        return FitScore(
            overall_score=round(overall, 1),
            skills_match=round(skills_match, 1),
            experience_fit=round(experience_fit, 1),
            evidence_quality=round(evidence_quality, 1),
            strengths=strengths,
            gaps=gaps,
            decision_notes=decision_notes,
            matched_skills=matched,
            missing_skills=missing,
            analysis_mode="rules",
        )

    def _skill_alignment(self) -> tuple[list[str], list[str]]:
        required = [normalize_skill_token(s) for s in self.required_technical]
        if not required:
            required = [
                normalize_skill_token(s)
                for s in find_technical_skills(self.job_text_lower)
            ][:8]

        matched: list[str] = []
        missing: list[str] = []
        for skill in required:
            if self._cv_has_skill(skill):
                matched.append(skill)
            else:
                missing.append(skill)
        return matched, missing

    def _cv_has_skill(self, skill: str) -> bool:
        if skill in self.cv_technical:
            return True
        for cv_skill in self.cv_technical:
            if skill in cv_skill or cv_skill in skill:
                if len(skill) > 2 and len(cv_skill) > 2:
                    return True
        blob = f"{self.experience_blob} {(self.cv_data.raw_text or '').lower()}"
        return skill in blob

    def _calculate_skills_match(
        self, matched: list[str], missing: list[str]
    ) -> float:
        total = len(matched) + len(missing)
        if total == 0:
            overlap = len(self.cv_technical & set(self.role_keywords))
            if overlap:
                return min(100.0, 55.0 + overlap * 12)
            return 55.0

        ratio = len(matched) / total
        score = ratio * 100

        job_soft = set(find_soft_skills(self.job_text_lower))
        if job_soft:
            soft_overlap = len(job_soft & self.cv_soft) / len(job_soft)
            score = score * 0.85 + soft_overlap * 100 * 0.15

        return min(100.0, max(0.0, score))

    def _calculate_experience_fit(self) -> float:
        if not self.cv_data.experience:
            return 15.0

        role_score = 0.0
        title_lower = self.role_title.lower()
        title_tokens = self.role_keywords or set(
            w for w in re.findall(r"[a-z]+", title_lower) if len(w) > 2
        )

        relevant_roles = 0
        for exp in self.cv_data.experience:
            exp_lower = f"{exp.role} {exp.company}".lower()
            if title_tokens and any(t in exp_lower for t in title_tokens):
                relevant_roles += 1
                role_score += 28.0
            elif any(t in exp_lower for t in ROLE_TOKENS) and any(
                t in title_lower for t in ROLE_TOKENS
            ):
                role_score += 12.0

        role_score = min(55.0, role_score)
        if relevant_roles == 0 and self.cv_data.experience:
            role_score = max(role_score, 20.0)

        exp_skills = find_technical_skills(self.experience_blob)
        required = self.required_technical or find_technical_skills(self.job_text_lower)
        if required:
            exp_matched = sum(
                1 for s in required if normalize_skill_token(s) in self.cv_technical
                or normalize_skill_token(s) in {normalize_skill_token(x) for x in exp_skills}
            )
            keyword_score = (exp_matched / len(required)) * 45.0
        else:
            keyword_score = 25.0

        depth_score = 0.0
        detailed = sum(
            1
            for e in self.cv_data.experience
            if e.description and len(e.description) > 80
        )
        depth_score = min(20.0, detailed * 5.0)

        return min(100.0, role_score + keyword_score + depth_score)

    def _calculate_evidence_quality(self) -> float:
        score = 35.0
        if self.cv_data.summary:
            score += 10.0
        if self.cv_data.projects:
            score += min(20.0, len(self.cv_data.projects) * 6)
        if self.cv_data.certifications:
            score += min(15.0, len(self.cv_data.certifications) * 5)
        if self.cv_data.education:
            score += min(10.0, len(self.cv_data.education) * 4)
        detailed = sum(
            1
            for e in self.cv_data.experience or []
            if e.description and len(e.description) > 120
        )
        score += min(20.0, detailed * 5)
        if self.cv_data.contact and self.cv_data.contact.email:
            score += 5.0
        return min(100.0, score)

    def _identify_strengths(
        self, skills_match: float, experience_fit: float, matched: list[str]
    ) -> list[str]:
        strengths: list[str] = []

        if matched:
            top = ", ".join(matched[:4])
            strengths.append(f"CV demonstrates required stack: {top}")

        if self.role_title:
            for exp in self.cv_data.experience or []:
                if any(
                    kw in exp.role.lower() for kw in self.role_keywords
                ):
                    strengths.append(
                        f"Relevant title history: {exp.role} at {exp.company or 'previous employer'}"
                    )
                    break

        if skills_match >= 75:
            strengths.append("Strong overlap between job requirements and CV skills")
        elif skills_match >= 55:
            strengths.append("Core technical requirements largely covered")

        if experience_fit >= 70:
            strengths.append("Work history aligns with the target role level and domain")

        if len(self.cv_data.projects or []) >= 2:
            strengths.append("Project work adds concrete evidence beyond job titles")

        if not strengths:
            strengths.append("Profile provides baseline material for structured interview")

        seen: set[str] = set()
        unique: list[str] = []
        for s in strengths:
            if s not in seen:
                unique.append(s)
                seen.add(s)
        return unique[:3]

    def _identify_gaps(
        self, skills_match: float, experience_fit: float, missing: list[str]
    ) -> list[str]:
        gaps: list[str] = []

        if missing:
            gaps.append(
                "Confirm hands-on experience with: "
                + ", ".join(missing[:3])
            )

        if skills_match < 60 and not missing:
            gaps.append("Job keywords are weakly reflected in the CV — probe depth in interview")

        if experience_fit < 55:
            gaps.append(
                f"Validate career trajectory and scope for {self.role_title or 'this role'}"
            )

        job_soft = set(find_soft_skills(self.job_text_lower))
        missing_soft = job_soft - self.cv_soft
        if missing_soft:
            gaps.append(
                "Discuss soft skills: " + ", ".join(sorted(missing_soft)[:2])
            )

        if "lead" in self.role_title.lower() and "leadership" not in self.cv_soft:
            gaps.append("Leadership and people-management impact need concrete examples")

        if not self.cv_data.projects:
            gaps.append("No projects listed — ask for work samples or portfolio evidence")

        if not gaps:
            gaps.append("Focus interview on depth, ownership, and recent outcomes")

        seen: set[str] = set()
        unique: list[str] = []
        for g in gaps:
            if g not in seen:
                unique.append(g)
                seen.add(g)
        return unique[:3]

    def _generate_decision_notes(
        self,
        score: float,
        strengths: list[str],
        gaps: list[str],
        missing: list[str],
    ) -> str:
        if score >= 82:
            level = "Strong fit"
            action = "Recommend advancing to interview."
        elif score >= 68:
            level = "Good fit"
            action = "Worth interviewing with targeted validation."
        elif score >= 50:
            level = "Moderate fit"
            action = "Proceed only if pipeline is thin or role allows ramp-up."
        else:
            level = "Weak fit on paper"
            action = "Consider pass unless exceptional context applies."

        parts = [f"{level} ({score:.0f}% overall). {action}"]
        if missing:
            parts.append(
                "Priority checks: " + ", ".join(missing[:3]) + "."
            )
        elif gaps:
            parts.append(gaps[0] + ".")
        return " ".join(parts)

    def generate_interview_questions(self, missing: list[str] | None = None) -> list[str]:
        missing = missing or []
        questions: list[str] = []

        if self.role_title:
            questions.append(
                f"For this {self.role_title} role, which accomplishment from your CV best predicts success here?"
            )

        if missing:
            skill = missing[0]
            questions.append(
                f"Walk me through a recent project where you used {skill} end-to-end — what did you own?"
            )
        elif self.cv_technical:
            top = sorted(self.cv_technical)[0]
            questions.append(
                f"Describe the most complex problem you solved using {top} and how you measured impact."
            )

        if self.cv_data.experience:
            latest = self.cv_data.experience[0]
            questions.append(
                f"At {latest.company or 'your last role'} as {latest.role}, what was the hardest trade-off you made?"
            )

        job_soft = find_soft_skills(self.job_text_lower)
        if job_soft:
            questions.append(
                f"This role emphasizes {job_soft[0]}. Tell me about a situation where that skill changed an outcome."
            )
        else:
            questions.append(
                "What part of this job description is outside your comfort zone, and how would you close that gap?"
            )

        seen: set[str] = set()
        unique: list[str] = []
        for q in questions:
            if q not in seen:
                unique.append(q)
                seen.add(q)
        return unique[:4]

    def apply_insights(self, fit_score: FitScore, insights: dict) -> FitScore:
        fit_score.strengths = insights.get("strengths", fit_score.strengths)
        fit_score.gaps = insights.get("gaps", fit_score.gaps)
        fit_score.decision_notes = insights.get(
            "decision_notes", fit_score.decision_notes
        )
        fit_score.analysis_mode = insights.get("analysis_mode", "llm")
        return fit_score
