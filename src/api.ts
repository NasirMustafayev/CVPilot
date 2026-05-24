/**
 * API client for CVPilot backend
 */

import { authHeaders } from './auth'
import type { AppMode } from './modeCopy'

export interface ContactInfo {
  name?: string
  email?: string
  phone?: string
  location?: string
  linkedin?: string
  website?: string
}

export interface Experience {
  role: string
  company: string
  start_date?: string
  end_date?: string
  description?: string
  duration_months?: number
}

export interface Education {
  degree: string
  institution: string
  field?: string
  graduation_date?: string
  gpa?: string
}

export interface Certification {
  name: string
  issuer?: string
  date?: string
}

export interface Project {
  name: string
  description?: string
  technologies?: string[]
}

export interface CVData {
  contact: ContactInfo
  summary?: string
  experience: Experience[]
  education: Education[]
  skills: {
    technical: string[]
    soft: string[]
    languages: string[]
  }
  certifications: Certification[]
  projects: Project[]
}

export interface FitScore {
  overall_score: number
  skills_match: number
  experience_fit: number
  evidence_quality: number
  strengths: string[]
  gaps: string[]
  decision_notes: string
}

export interface AnalysisSummary {
  id: number
  workspace: AppMode
  cv_filename: string
  candidate_name?: string | null
  role_title: string
  overall_score: number
  created_at: string
}

export interface AnalysisResult {
  id?: number
  cv_filename?: string
  role_title?: string
  job_description?: string
  cv_data: CVData
  fit_score: FitScore
  interview_questions: string[]
  analysis_mode: 'rules' | 'local-ml' | 'llm'
  matched_skills: string[]
  missing_skills: string[]
  semantic_matches?: Array<{
    requirement: string
    evidence: string
    similarity: number
    confidence: 'low' | 'medium' | 'high'
  }>
  semantic_score?: number
}

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

function parseApiError(detail: unknown, fallback: string): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg: string }).msg)
        }
        return JSON.stringify(item)
      })
      .join('; ')
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail)
  }
  return fallback
}

export async function listAnalyses(workspace?: AppMode): Promise<AnalysisSummary[]> {
  const query = workspace ? `?workspace=${workspace}` : ''
  const response = await fetch(`${API_BASE_URL}/analyses${query}`, {
    headers: authHeaders(),
  })
  if (!response.ok) {
    let message = 'Failed to load saved analyses'
    try {
      const error = await response.json()
      message = parseApiError(error.detail, message)
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }
  return response.json()
}

export async function clearAnalyses(workspace?: AppMode): Promise<number> {
  const query = workspace ? `?workspace=${workspace}` : ''
  const response = await fetch(`${API_BASE_URL}/analyses${query}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (!response.ok) {
    let message = 'Failed to clear history'
    try {
      const error = await response.json()
      message = parseApiError(error.detail, message)
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }
  const data = await response.json()
  return data.deleted ?? 0
}

export async function fetchAnalysis(analysisId: number): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/analyses/${analysisId}`, {
    headers: authHeaders(),
  })
  if (!response.ok) {
    let message = 'Failed to load analysis'
    try {
      const error = await response.json()
      message = parseApiError(error.detail, message)
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }
  return response.json()
}

export async function analyzeCv(
  file: File,
  jobDescription: string,
  roleTitle: string = '',
  workspace: AppMode = 'hr',
): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('job_description', jobDescription)
  formData.append('role_title', roleTitle)
  formData.append('workspace', workspace)

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  })

  if (!response.ok) {
    let message = 'Failed to analyze CV'
    try {
      const error = await response.json()
      message = parseApiError(error.detail, message)
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }

  return response.json()
}

export async function extractCv(file: File): Promise<CVData> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/extract-cv`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  })

  if (!response.ok) {
    let message = 'Failed to extract CV data'
    try {
      const error = await response.json()
      message = parseApiError(error.detail, message)
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }

  return response.json()
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.ok
  } catch {
    return false
  }
}
