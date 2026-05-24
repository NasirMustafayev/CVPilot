"""
Local semantic matching for job requirements vs CV evidence.

This intentionally avoids API calls and heavyweight model downloads. It uses a
small TF-IDF style vectorizer and cosine similarity so CVPilot can run fully
offline while still matching meaning better than exact keyword rules.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
import math
import re


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "this",
    "to",
    "we",
    "with",
    "you",
    "your",
}

REQUIREMENT_HINTS = (
    "must",
    "required",
    "requirement",
    "responsible",
    "responsibilities",
    "experience",
    "knowledge",
    "proficient",
    "familiar",
    "ability",
    "skill",
    "build",
    "design",
    "develop",
    "manage",
    "lead",
    "own",
)


@dataclass
class SemanticMatch:
    requirement: str
    evidence: str
    similarity: float
    confidence: str

    def to_dict(self) -> dict:
        return asdict(self)


def semantic_requirement_matches(
    cv_text: str,
    job_text: str,
    role_title: str = "",
    limit: int = 8,
) -> list[SemanticMatch]:
    requirements = extract_requirements(job_text, role_title)
    evidence_chunks = chunk_cv_evidence(cv_text)
    if not requirements or not evidence_chunks:
        return []

    documents = requirements + evidence_chunks
    vectors = _tfidf_vectors(documents)
    requirement_vectors = vectors[: len(requirements)]
    evidence_vectors = vectors[len(requirements) :]

    matches: list[SemanticMatch] = []
    for requirement, req_vector in zip(requirements, requirement_vectors):
        best_text = ""
        best_score = 0.0
        for evidence, evidence_vector in zip(evidence_chunks, evidence_vectors):
            score = _cosine(req_vector, evidence_vector)
            if score > best_score:
                best_score = score
                best_text = evidence

        if best_score >= 0.18:
            matches.append(
                SemanticMatch(
                    requirement=requirement,
                    evidence=best_text,
                    similarity=round(best_score, 3),
                    confidence=_confidence(best_score),
                )
            )

    matches.sort(key=lambda item: item.similarity, reverse=True)
    return matches[:limit]


def extract_requirements(job_text: str, role_title: str = "") -> list[str]:
    text = (job_text or "").replace("\r", "\n")
    candidates = _split_units(text)

    requirements: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        phrase = candidate.strip(" -:\t")
        if len(phrase) < 18 or len(phrase) > 220:
            continue
        lower = phrase.lower()
        if not any(hint in lower for hint in REQUIREMENT_HINTS):
            continue
        normalized = re.sub(r"\s+", " ", lower)
        if normalized in seen:
            continue
        seen.add(normalized)
        requirements.append(phrase)

    if role_title and role_title.strip():
        requirements.insert(0, f"Experience relevant to {role_title.strip()}")

    return requirements[:12]


def chunk_cv_evidence(cv_text: str) -> list[str]:
    text = (cv_text or "").replace("\r", "\n")
    raw_chunks = _split_units(text)
    chunks: list[str] = []
    seen: set[str] = set()

    for raw in raw_chunks:
        chunk = raw.strip(" -:\t")
        if len(chunk) < 24 or len(chunk) > 260:
            continue
        lower = chunk.lower()
        if lower in seen:
            continue
        seen.add(lower)
        chunks.append(chunk)

    if len(chunks) < 4:
        words = text.split()
        for i in range(0, len(words), 28):
            chunk = " ".join(words[i : i + 42]).strip()
            if len(chunk) >= 24:
                chunks.append(chunk)

    return chunks[:80]


def _split_units(text: str) -> list[str]:
    rough = re.split(r"(?:\n+|[.;•])", text)
    units: list[str] = []
    for item in rough:
        clean = _clean_text(item)
        if not clean:
            continue
        clauses = re.split(r"\s*,\s+|\s+;\s+", clean)
        for clause in clauses:
            clause = _clean_text(clause)
            if clause:
                units.append(clause)
    return units


def semantic_score(matches: list[SemanticMatch]) -> float:
    if not matches:
        return 0.0
    top = matches[:6]
    average = sum(match.similarity for match in top) / len(top)
    return min(100.0, average * 140.0)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\r", "\n")).strip()


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z][a-z0-9+#.-]{1,}", text.lower())
    tokens = [word for word in words if word not in STOP_WORDS]
    bigrams = [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
    return tokens + bigrams


def _tfidf_vectors(documents: list[str]) -> list[dict[str, float]]:
    tokenized = [_tokens(document) for document in documents]
    doc_count = len(tokenized)
    doc_frequency: Counter[str] = Counter()
    for tokens in tokenized:
        doc_frequency.update(set(tokens))

    vectors: list[dict[str, float]] = []
    for tokens in tokenized:
        counts = Counter(tokens)
        total = sum(counts.values()) or 1
        vector: dict[str, float] = {}
        for token, count in counts.items():
            tf = count / total
            idf = math.log((doc_count + 1) / (doc_frequency[token] + 1)) + 1
            vector[token] = tf * idf
        vectors.append(vector)
    return vectors


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    overlap = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in overlap)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def _confidence(score: float) -> str:
    if score >= 0.42:
        return "high"
    if score >= 0.27:
        return "medium"
    return "low"
