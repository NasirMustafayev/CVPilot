import type { AnalysisResult } from './api'

export type AppMode = 'hr' | 'candidate'

export function hiringVerdict(score: number) {
  if (score >= 82) {
    return {
      label: 'Strong match',
      tone: 'positive' as const,
      recommendation: 'Recommend interview',
    }
  }
  if (score >= 68) {
    return {
      label: 'Good match',
      tone: 'positive' as const,
      recommendation: 'Proceed to interview',
    }
  }
  if (score >= 50) {
    return {
      label: 'Moderate match',
      tone: 'caution' as const,
      recommendation: 'Interview only if pipeline is thin',
    }
  }
  return {
    label: 'Weak match',
    tone: 'negative' as const,
    recommendation: 'Likely pass unless strong context',
  }
}

export function candidateVerdict(score: number) {
  if (score >= 75) {
    return {
      label: 'Strong fit',
      tone: 'positive' as const,
      advice: 'Your CV aligns well — worth applying and preparing for interviews.',
    }
  }
  if (score >= 58) {
    return {
      label: 'Competitive with gaps',
      tone: 'caution' as const,
      advice: 'You are in range for many roles, but tighten evidence for missing skills.',
    }
  }
  return {
    label: 'Stretch for this role',
    tone: 'negative' as const,
    advice: 'Consider upskilling or targeting roles closer to your current profile.',
  }
}

export function buildCvImprovementTips(analysis: AnalysisResult): string[] {
  const tips: string[] = []

  for (const skill of analysis.missing_skills.slice(0, 3)) {
    tips.push(`Add a bullet showing hands-on ${skill} work (project, metric, or ownership).`)
  }

  for (const gap of analysis.fit_score.gaps) {
    if (gap.toLowerCase().includes('project')) {
      tips.push('Include 1–2 projects with tech stack and measurable outcomes.')
    }
    if (gap.toLowerCase().includes('soft skill')) {
      tips.push('Mirror job soft skills with short STAR-style examples in experience bullets.')
    }
  }

  if (analysis.cv_data.experience.length === 0) {
    tips.push('Use an "Experience" section with role, company, dates, and impact bullets.')
  } else if (
    analysis.cv_data.experience.every(
      (e) => !e.description || e.description.length < 60,
    )
  ) {
    tips.push('Expand role bullets with outcomes (%, revenue, users, latency, team size).')
  }

  if (analysis.cv_data.skills.technical.length < 4) {
    tips.push('List technical skills explicitly — parsers may miss skills buried in prose.')
  }

  if (tips.length === 0) {
    tips.push('Tailor your summary to the role title and repeat top keywords from the job post.')
    tips.push('Quantify impact in your two most recent roles.')
  }

  const unique: string[] = []
  const seen = new Set<string>()
  for (const t of tips) {
    if (!seen.has(t)) {
      unique.push(t)
      seen.add(t)
    }
  }
  return unique.slice(0, 4)
}

export const MODE_COPY = {
  hr: {
    label: 'HR workspace',
    title: 'Evaluate candidate fit',
    subtitle:
      'Upload a candidate CV and the role requirements to decide if they are worth interviewing.',
    uploadTitle: 'Candidate CV',
    uploadHint: 'PDF, DOC, or DOCX from the applicant',
    roleLabel: 'Role you are hiring for',
    jobLabel: 'Job description',
    jobPlaceholder:
      'Paste the full job post — requirements drive the fit score.',
    action: 'Evaluate candidate',
    actionLoading: 'Evaluating…',
    scoreTitle: 'Hiring fit score',
    scoreHint: 'Weighted: skills 45%, experience 35%, evidence 20%.',
    scoreEmpty: 'Upload a candidate CV and evaluate against the role.',
    decisionTitle: 'Hiring recommendation',
    decisionEmpty: 'Recommendation appears after you evaluate the candidate.',
    strengthsTitle: 'Why this candidate fits',
    strengthsEmpty: 'Strengths appear after evaluation.',
    gapsTitle: 'Risks to validate in interview',
    gapsEmpty: 'Interview focus areas appear after evaluation.',
    questionsTitle: 'Interview kit',
    questionsHint: 'Questions for your panel to probe gaps and verify claims.',
    questionsEmpty: 'Interview questions generate after evaluation.',
    extractedTitle: 'Parsed candidate profile',
    extractedHint: 'Confirm the CV was read correctly before trusting the score.',
    inputTitle: 'Role & candidate',
    inputHint: 'Everything needed to score this applicant.',
    historyTitle: 'Saved evaluations',
    historyHint: 'Candidates you have already analyzed.',
    historyEmpty: 'No saved evaluations yet. Run your first analysis.',
    clearHistory: 'Clear evaluations',
    clearHistoryConfirm: 'Delete all saved candidate evaluations for this workspace?',
  },
  candidate: {
    label: 'Candidate workspace',
    title: 'Test your CV against a role',
    subtitle:
      'See if your skills and experience match a job before you apply — and what to improve first.',
    uploadTitle: 'Your CV',
    uploadHint: 'Upload the CV you plan to send for this application',
    roleLabel: 'Role you are targeting',
    jobLabel: 'Job description',
    jobPlaceholder:
      'Paste the job you want to apply for — we compare it to your CV.',
    action: 'Check my fit',
    actionLoading: 'Checking fit…',
    scoreTitle: 'Your fit for this role',
    scoreHint: 'How closely your CV matches this job today.',
    scoreEmpty: 'Upload your CV and run a fit check for this role.',
    decisionTitle: 'Should you apply?',
    decisionEmpty: 'A clear apply / improve / stretch readout appears after the check.',
    strengthsTitle: 'What already works',
    strengthsEmpty: 'Your strengths for this role show up after the check.',
    gapsTitle: 'What to improve on your CV',
    gapsEmpty: 'Improvement areas appear after the check.',
    questionsTitle: 'Questions to prepare for',
    questionsHint: 'Likely interview topics based on gaps in your CV vs this job.',
    questionsEmpty: 'Prep questions appear after your fit check.',
    extractedTitle: 'What we read from your CV',
    extractedHint: 'If something is wrong here, fix your CV file and run again.',
    inputTitle: 'Target role',
    inputHint: 'The job you want to compare yourself against.',
    tipsTitle: 'CV improvement plan',
    tipsHint: 'Actionable edits before you submit an application.',
    tipsEmpty: 'Personalized tips appear after your fit check.',
    historyTitle: 'Saved fit checks',
    historyHint: 'Roles you have already compared against your CV.',
    historyEmpty: 'No saved checks yet. Run your first fit check.',
    clearHistory: 'Clear history',
    clearHistoryConfirm: 'Delete all saved fit checks for this workspace?',
  },
} as const
