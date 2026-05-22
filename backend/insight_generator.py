"""
Optional LLM-backed narrative insights. Falls back to rule-based copy when no API key is set.
Uses stdlib HTTP only (avoids httpx/httpcore issues on Python 3.14+).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Optional

from skills_vocab import job_required_technical

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"


def _cv_summary(cv_data: Any) -> dict:
    contact = cv_data.contact
    return {
        "name": contact.name,
        "email": contact.email,
        "summary": cv_data.summary,
        "experience": [
            {
                "role": e.role,
                "company": e.company,
                "description": (e.description or "")[:400],
            }
            for e in (cv_data.experience or [])[:6]
        ],
        "education": [
            {"degree": e.degree, "institution": e.institution}
            for e in (cv_data.education or [])[:4]
        ],
        "technical_skills": cv_data.skills.get("technical", []) if cv_data.skills else [],
        "soft_skills": cv_data.skills.get("soft", []) if cv_data.skills else [],
        "projects": [p.name for p in (cv_data.projects or [])[:5]],
        "certifications": [c.name for c in (cv_data.certifications or [])[:5]],
    }


def _openai_chat(api_key: str, model: str, system: str, user: str) -> dict:
    body = json.dumps(
        {
            "model": model,
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        OPENAI_CHAT_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))

    return payload


def generate_insights(
    cv_data: Any,
    job_description: str,
    role_title: str,
    fit_score: Any,
    matched_skills: list[str],
    missing_skills: list[str],
) -> Optional[dict[str, Any]]:
    """
    Return dict with strengths, gaps, decision_notes, interview_questions
    or None to use rule-based output from JobFitAnalyzer.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    required = job_required_technical(f"{role_title}\n{job_description}")

    system = (
        "You are an expert technical recruiter. Analyze CV fit against a job. "
        "Be specific, evidence-based, and concise. Output valid JSON only."
    )
    user_payload = {
        "role_title": role_title,
        "job_description": job_description[:4000],
        "cv": _cv_summary(cv_data),
        "scores": {
            "overall": round(fit_score.overall_score, 1),
            "skills_match": round(fit_score.skills_match, 1),
            "experience_fit": round(fit_score.experience_fit, 1),
            "evidence_quality": round(fit_score.evidence_quality, 1),
        },
        "matched_required_skills": matched_skills,
        "missing_required_skills": missing_skills,
        "job_required_skills_detected": required,
    }
    user = (
        "Given the CV and job, write hiring insights.\n"
        f"{json.dumps(user_payload, indent=2)}\n\n"
        "Return JSON with exactly these keys:\n"
        '- "strengths": array of 3 strings (cite CV evidence)\n'
        '- "gaps": array of 3 strings (actionable validation points)\n'
        '- "decision_notes": one paragraph string for HR\n'
        '- "interview_questions": array of 4 specific interview questions\n'
    )

    try:
        payload = _openai_chat(api_key, model, system, user)
        content = payload["choices"][0]["message"]["content"]
        data = json.loads(content)
        for key in ("strengths", "gaps", "decision_notes", "interview_questions"):
            if key not in data:
                return None
        return {
            "strengths": list(data["strengths"])[:3],
            "gaps": list(data["gaps"])[:3],
            "decision_notes": str(data["decision_notes"]),
            "interview_questions": list(data["interview_questions"])[:4],
            "analysis_mode": "llm",
        }
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        print(f"[WARN] LLM insights HTTP {exc.code}: {detail}")
        return None
    except Exception as exc:
        print(f"[WARN] LLM insights unavailable: {exc}")
        return None
