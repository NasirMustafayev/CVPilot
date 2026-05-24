"""
Shared skill vocabulary and text-matching helpers for CV extraction and job fit analysis.
"""

from __future__ import annotations

import re
from typing import Iterable

# Canonical technical skills (longer phrases first for boundary matching)
TECHNICAL_SKILLS: tuple[str, ...] = (
    "machine learning",
    "deep learning",
    "natural language processing",
    "computer vision",
    "github actions",
    "gitlab ci",
    "rest api",
    "unit testing",
    "integration testing",
    "testing library",
    "react native",
    "next.js",
    "node.js",
    "express.js",
    "ci/cd",
    "html",
    "css",
    "tailwind",
    "c++",
    "c#",
    "typescript",
    "javascript",
    "postgresql",
    "sql server",
    "mongodb",
    "elasticsearch",
    "kubernetes",
    "microservices",
    "tensorflow",
    "pytorch",
    "fastapi",
    "graphql",
    "angular",
    "express",
    "nestjs",
    "django",
    "flask",
    "spring",
    "jenkins",
    "gitlab",
    "playwright",
    "cypress",
    "selenium",
    "vitest",
    "jest",
    "python",
    "react",
    "redux",
    "vue",
    "java",
    "rust",
    "csharp",
    "docker",
    "terraform",
    "azure",
    "mysql",
    "sqlite",
    "redis",
    "kafka",
    "rabbitmq",
    "numpy",
    "pandas",
    "power bi",
    "tableau",
    "excel",
    "figma",
    "scrum",
    "agile",
    "nosql",
    "openapi",
    "rest",
    "api",
    "aws",
    "gcp",
    "git",
    "sql",
    "linux",
    "bash",
    "qa",
    "go",
)

SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "node.js": ("nodejs", "node js", "node"),
    "express.js": ("expressjs", "express js"),
    "next.js": ("nextjs", "next js"),
    "react": ("react.js", "reactjs"),
    "vue": ("vue.js", "vuejs"),
    "typescript": ("type script",),
    "javascript": ("java script", "ecmascript"),
    "postgresql": ("postgres", "postgre sql"),
    "mongodb": ("mongo db", "mongo"),
    "c#": ("c sharp",),
    "c++": ("cpp",),
    "github actions": ("github ci",),
    "gitlab ci": ("gitlab-ci",),
    "ci/cd": ("cicd", "ci cd"),
    "rest api": ("restful api", "restful apis", "rest apis"),
    "power bi": ("powerbi",),
    "machine learning": ("ml",),
    "natural language processing": ("nlp",),
    "computer vision": (),
}

SOFT_SKILLS: frozenset[str] = frozenset(
    {
        "communication",
        "leadership",
        "teamwork",
        "problem solving",
        "problem-solving",
        "critical thinking",
        "time management",
        "collaboration",
        "adaptability",
        "creativity",
        "interpersonal",
        "attention to detail",
        "project management",
        "analytical",
        "negotiation",
        "presentation",
        "customer service",
        "mentoring",
        "stakeholder management",
        "product thinking",
    }
)

ROLE_TOKENS: frozenset[str] = frozenset(
    {
        "frontend",
        "backend",
        "fullstack",
        "full-stack",
        "full stack",
        "software",
        "engineer",
        "developer",
        "devops",
        "data",
        "scientist",
        "analyst",
        "manager",
        "director",
        "architect",
        "lead",
        "consultant",
        "designer",
        "product",
        "mobile",
        "ios",
        "android",
        "qa",
        "test",
        "security",
        "cloud",
        "ml",
        "ai",
    }
)

JOB_STOP_WORDS: frozenset[str] = frozenset(
    {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "we",
        "you",
        "i",
        "they",
        "he",
        "she",
        "it",
        "that",
        "this",
        "which",
        "will",
        "should",
        "could",
        "would",
        "can",
        "must",
        "may",
        "might",
        "need",
        "needs",
        "required",
        "requirements",
        "responsibilities",
        "qualifications",
        "experience",
        "years",
        "year",
        "role",
        "position",
        "team",
        "work",
        "working",
        "using",
        "use",
        "able",
        "ability",
        "skills",
        "skill",
        "including",
        "such",
        "as",
        "our",
        "your",
        "have",
        "has",
        "had",
    }
)


def skill_pattern(skill: str) -> re.Pattern[str]:
    """Word-boundary pattern; allows . and + inside tokens (e.g. node.js, c++)."""
    escaped = re.escape(skill.lower())
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"(?<![a-z0-9.+#-]){escaped}(?![a-z0-9.+#-])", re.IGNORECASE)


def find_technical_skills(text: str) -> list[str]:
    """Return matched technical skills from text, preserving canonical names."""
    if not text:
        return []
    found: list[str] = []
    seen: set[str] = set()
    lower = text.lower()
    for skill in TECHNICAL_SKILLS:
        key = skill.lower()
        if key in seen:
            continue
        candidates = (skill, *SKILL_ALIASES.get(skill, ()))
        if any(skill_pattern(candidate).search(lower) for candidate in candidates):
            found.append(skill)
            seen.add(key)
    return sorted(_remove_redundant_skills(found), key=str.lower)


def _remove_redundant_skills(skills: Iterable[str]) -> list[str]:
    values = set(skills)
    if "rest api" in values:
        values.discard("rest")
        values.discard("api")
    if "openapi" in values:
        values.discard("api")
    if "postgresql" in values or "mysql" in values or "sql server" in values:
        values.discard("sql")
    if "github actions" in values or "gitlab ci" in values:
        values.discard("ci/cd")
    return list(values)


def find_soft_skills(text: str) -> list[str]:
    lower = text.lower()
    found = []
    for skill in sorted(SOFT_SKILLS, key=len, reverse=True):
        if skill in lower and skill not in found:
            found.append(skill)
    return sorted(found)


def extract_role_keywords(role_title: str) -> set[str]:
    if not role_title:
        return set()
    words = re.findall(r"[a-z][a-z0-9+\-]*", role_title.lower())
    return {w for w in words if len(w) > 2 and w not in JOB_STOP_WORDS}


def job_required_technical(job_text: str) -> list[str]:
    return find_technical_skills(job_text)


def normalize_skill_token(skill: str) -> str:
    return skill.lower().strip()
