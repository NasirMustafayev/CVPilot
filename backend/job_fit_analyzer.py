"""
Job fit analysis — requirement-focused scoring with evidence from CV text.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re

from skills_vocab import (
    ROLE_TOKENS,
    extract_role_keywords,
    find_soft_skills,
    find_technical_skills,
    job_required_technical,
    normalize_skill_token,
)
from semantic_matcher import SemanticMatch, semantic_requirement_matches, semantic_score


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
    semantic_matches: list[dict]
    semantic_score: float
    analysis_mode: str = "local-ml"


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
        self.required_years = self._extract_required_years()
        self.cv_years = self._estimate_cv_years()
        self.required_seniority = self._detect_seniority(self.job_text)
        self.cv_seniority = self._detect_seniority(self.experience_blob)
        self.semantic_matches = semantic_requirement_matches(
            cv_data.raw_text or self.experience_blob,
            self.job_description,
            self.role_title,
        )
        self.semantic_score = semantic_score(self.semantic_matches)

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

    def _extract_required_years(self) -> float | None:
        patterns = (
            r"(\d+)\+?\s*(?:years|yrs)\s+(?:of\s+)?(?:professional\s+)?experience",
            r"(?:minimum|min\.?|at least)\s+(\d+)\+?\s*(?:years|yrs)",
            r"(\d+)\+?\s*(?:years|yrs)\s+(?:with|in|using)",
        )
        values: list[int] = []
        for pattern in patterns:
            for match in re.finditer(pattern, self.job_text_lower):
                values.append(int(match.group(1)))
        if not values:
            return None
        return float(max(values))

    def _estimate_cv_years(self) -> float:
        ranges: list[tuple[int, int]] = []
        current_year = datetime.now().year

        for exp in self.cv_data.experience or []:
            start = self._year_from_text(exp.start_date or "")
            end = self._year_from_text(exp.end_date or "")
            if start:
                if exp.end_date and re.search(r"present|current|now", exp.end_date, re.I):
                    end = current_year
                if not end:
                    end = min(current_year, start + 1)
                if end >= start:
                    ranges.append((start, min(end, current_year)))

        if ranges:
            # Merge overlapping ranges to avoid double counting concurrent roles.
            ranges.sort()
            merged: list[list[int]] = []
            for start, end in ranges:
                if not merged or start > merged[-1][1]:
                    merged.append([start, end])
                else:
                    merged[-1][1] = max(merged[-1][1], end)
            return round(sum(end - start + 1 for start, end in merged), 1)

        text = f"{self.cv_data.summary or ''} {self.experience_blob} {self.cv_data.raw_text or ''}".lower()
        year_mentions = [
            int(m.group(1))
            for m in re.finditer(r"(\d+)\+?\s*(?:years|yrs)\s+(?:of\s+)?experience", text)
        ]
        return float(max(year_mentions)) if year_mentions else 0.0

    def _year_from_text(self, value: str) -> int | None:
        match = re.search(r"(19|20)\d{2}", value or "")
        return int(match.group(0)) if match else None

    def _detect_seniority(self, text: str) -> int:
        lower = (text or "").lower()
        if re.search(r"\b(?:vp|vice president|head of|director|principal|staff)\b", lower):
            return 5
        if re.search(r"\b(?:lead|manager|senior|sr\.?)\b", lower):
            return 4
        if re.search(r"\b(?:mid|intermediate)\b", lower):
            return 3
        if re.search(r"\b(?:junior|jr\.?|entry[-\s]?level|graduate)\b", lower):
            return 2
        if re.search(r"\b(?:intern|internship|trainee)\b", lower):
            return 1
        return 0

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
            semantic_matches=[match.to_dict() for match in self.semantic_matches],
            semantic_score=round(self.semantic_score, 1),
            analysis_mode="local-ml",
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

        if self.semantic_score:
            score = score * 0.78 + self.semantic_score * 0.22

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
                role_score += 10.0
            elif any(t in exp_lower for t in ROLE_TOKENS) and any(
                t in title_lower for t in ROLE_TOKENS
            ):
                role_score += 5.0

        role_score = min(25.0, role_score)
        if relevant_roles == 0 and self.cv_data.experience:
            role_score = max(role_score, 10.0)

        exp_skills = find_technical_skills(self.experience_blob)
        required = self.required_technical or find_technical_skills(self.job_text_lower)
        if required:
            exp_matched = sum(
                1 for s in required if normalize_skill_token(s) in self.cv_technical
                or normalize_skill_token(s) in {normalize_skill_token(x) for x in exp_skills}
            )
            keyword_score = (exp_matched / len(required)) * 25.0
        else:
            keyword_score = 15.0

        detailed = sum(
            1
            for e in self.cv_data.experience
            if e.description and len(e.description) > 80
        )
        depth_score = min(15.0, detailed * 4.0)

        years_score = 20.0
        if self.required_years:
            if self.cv_years <= 0:
                years_score = 5.0
            else:
                years_score = min(20.0, (self.cv_years / self.required_years) * 20.0)

        seniority_score = 15.0
        if self.required_seniority:
            if self.cv_seniority <= 0:
                seniority_score = 8.0
            elif self.cv_seniority >= self.required_seniority:
                seniority_score = 15.0
            else:
                seniority_score = max(4.0, (self.cv_seniority / self.required_seniority) * 15.0)

        semantic_experience_score = min(15.0, self.semantic_score * 0.15)

        return min(
            100.0,
            role_score
            + keyword_score
            + depth_score
            + years_score
            + seniority_score
            + semantic_experience_score,
        )

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
        quantified = len(
            re.findall(
                r"\b(?:\d+%|\d+x|\$[\d,.]+|\d+\+?\s*(?:users|customers|people|engineers|projects|features))\b",
                self.cv_data.raw_text or "",
                re.I,
            )
        )
        score += min(15.0, quantified * 4)
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

        strong_semantic = [
            match
            for match in self.semantic_matches
            if isinstance(match, SemanticMatch) and match.confidence in ("high", "medium")
        ]
        if strong_semantic:
            strengths.append(
                "CV evidence semantically matches role requirement: "
                + strong_semantic[0].requirement[:120]
            )

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

        if self.required_years and self.cv_years >= self.required_years:
            strengths.append(
                f"Experience duration appears to meet the {self.required_years:.0f}+ year requirement"
            )

        if self.required_seniority and self.cv_seniority >= self.required_seniority:
            strengths.append("Seniority signals in the CV match the role expectation")

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

        low_semantic = [
            match for match in self.semantic_matches if match.confidence == "low"
        ]
        if self.semantic_matches and len(low_semantic) >= max(2, len(self.semantic_matches) // 2):
            gaps.append("Some job requirements have weak supporting evidence in the CV")

        if skills_match < 60 and not missing:
            gaps.append("Job keywords are weakly reflected in the CV — probe depth in interview")

        if experience_fit < 55:
            gaps.append(
                f"Validate career trajectory and scope for {self.role_title or 'this role'}"
            )

        if self.required_years and self.cv_years and self.cv_years < self.required_years:
            gaps.append(
                f"Job asks for {self.required_years:.0f}+ years; CV evidence suggests about {self.cv_years:.0f}"
            )
        elif self.required_years and not self.cv_years:
            gaps.append(
                f"Job asks for {self.required_years:.0f}+ years; CV dates are not clear enough to verify"
            )

        if self.required_seniority and self.cv_seniority and self.cv_seniority < self.required_seniority:
            gaps.append("Seniority level appears below the role; validate ownership and scope")
        elif self.required_seniority and not self.cv_seniority:
            gaps.append("Role seniority is clear, but CV seniority signals are weak")

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

        if self.semantic_matches:
            match = self.semantic_matches[0]
            questions.append(
                f"The job requires: {match.requirement[:110]}. Which CV example best proves this?"
            )

        if self.required_years and self.cv_years < self.required_years:
            questions.append(
                f"This role expects {self.required_years:.0f}+ years of experience. Which projects show you can operate at that level?"
            )
        elif self.required_seniority and self.cv_seniority < self.required_seniority:
            questions.append(
                "Give an example of ownership or leadership that proves you can handle the seniority of this role."
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
