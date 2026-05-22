/**
 * API client for CVPilot backend
 */

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

export interface AnalysisResult {
  cv_data: CVData
  fit_score: FitScore
  interview_questions: string[]
}

const API_BASE_URL = 'http://localhost:8000'

export async function analyzeCv(
  file: File,
  jobDescription: string,
  roleTitle: string = '',
): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('job_description', jobDescription)
  formData.append('role_title', roleTitle)

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze CV')
  }

  return response.json()
}

export async function extractCv(file: File): Promise<CVData> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/extract-cv`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to extract CV data')
  }

  return response.json()
}
