import { useMemo, useState } from 'react'
import { analyzeCv } from './api'
import type { AnalysisResult } from './api'
import {
  AlertTriangle,
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  FileText,
  LockKeyhole,
  LogOut,
  Mail,
  MessageSquareText,
  Upload,
  UserRound,
  UsersRound,
} from 'lucide-react'
import './App.css'

type Mode = 'hr' | 'candidate'
type Page = 'landing' | 'login' | 'register' | 'dashboard'

const strengths = [
  'React and TypeScript experience is clearly visible',
  'Product work includes customer-facing outcomes',
  'Communication and ownership signals match the role',
]

const gaps = [
  'Analytics tools are not mentioned directly',
  'Cloud deployment ownership needs stronger evidence',
  'Mentoring experience should be validated in interview',
]

const questions = [
  'Which product feature have you owned from discovery to release?',
  'How do you structure a complex React and TypeScript codebase?',
  'Tell me about a time you clarified vague product requirements.',
  'Which responsibility in this role would require the most ramp-up?',
]

const scoreDetails = [
  { label: 'Skills match', value: 82 },
  { label: 'Experience fit', value: 76 },
  { label: 'Evidence quality', value: 69 },
]

function App() {
  const [page, setPage] = useState<Page>('landing')
  const [mode, setMode] = useState<Mode>('hr')

  if (page === 'login') {
    return <AuthScreen type="login" setMode={setMode} setPage={setPage} />
  }

  if (page === 'register') {
    return <AuthScreen type="register" setMode={setMode} setPage={setPage} />
  }

  if (page === 'dashboard') {
    return <Dashboard mode={mode} setMode={setMode} setPage={setPage} />
  }

  return <LandingPage setMode={setMode} setPage={setPage} />
}

function Brand({ onClick }: { onClick?: () => void }) {
  const content = <img className="brand-logo" src="/logo.svg" alt="CVPilot" />

  if (!onClick) {
    return <div className="brand">{content}</div>
  }

  return (
    <button className="brand brand-button" type="button" onClick={onClick}>
      {content}
    </button>
  )
}

function LandingPage({
  setMode,
  setPage,
}: {
  setMode: (mode: Mode) => void
  setPage: (page: Page) => void
}) {
  return (
    <main className="page">
      <Header setPage={setPage} />

      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">For HR teams and candidates</span>
          <h1>CV analysis and interview preparation in one focused workspace.</h1>
          <p>
            Upload a CV, compare it against a job description, identify fit gaps,
            and generate practical interview questions.
          </p>
          <div className="actions">
            <button
              className="primary-button"
              type="button"
              onClick={() => {
                setMode('hr')
                setPage('register')
              }}
            >
              Start as HR
              <ArrowRight size={18} />
            </button>
            <button
              className="secondary-button"
              type="button"
              onClick={() => {
                setMode('candidate')
                setPage('register')
              }}
            >
              Start as candidate
            </button>
          </div>
        </div>

        <div className="analysis-preview" aria-label="CVPilot preview">
          <div className="preview-header">
            <span>Candidate fit</span>
            <strong>76%</strong>
          </div>
          <div className="score-line">
            <span style={{ width: '76%' }} />
          </div>
          <div className="preview-list">
            <p><CheckCircle2 size={17} /> Strong frontend match</p>
            <p><AlertTriangle size={17} /> Validate analytics exposure</p>
            <p><MessageSquareText size={17} /> 4 interview questions ready</p>
          </div>
        </div>
      </section>

      <section className="section" id="features">
        <div className="section-heading">
          <span>Core workflow</span>
          <h2>Simple enough for daily hiring work</h2>
        </div>
        <div className="feature-grid">
          <article>
            <Upload size={22} />
            <h3>Upload CV</h3>
            <p>Use a CV and job description as the source of truth.</p>
          </article>
          <article>
            <FileText size={22} />
            <h3>Analyze fit</h3>
            <p>Get strengths, missing signals, and evidence-based notes.</p>
          </article>
          <article>
            <MessageSquareText size={22} />
            <h3>Prepare interview</h3>
            <p>Generate focused questions for the exact role and candidate.</p>
          </article>
        </div>
      </section>

      <section className="simple-cta">
        <div>
          <span className="eyebrow">Demo ready</span>
          <h2>Open the workspace and test the flow.</h2>
        </div>
        <button className="primary-button" type="button" onClick={() => setPage('dashboard')}>
          View demo
          <ArrowRight size={18} />
        </button>
      </section>
    </main>
  )
}

function Header({ setPage }: { setPage: (page: Page) => void }) {
  return (
    <header className="header">
      <div className="header-inner">
        <Brand onClick={() => setPage('landing')} />
        <nav aria-label="Primary navigation">
          <a href="#features">Features</a>
          <button type="button" onClick={() => setPage('login')}>Log in</button>
          <button className="nav-primary" type="button" onClick={() => setPage('register')}>
            Register
          </button>
        </nav>
      </div>
    </header>
  )
}

function AuthScreen({
  type,
  setMode,
  setPage,
}: {
  type: 'login' | 'register'
  setMode: (mode: Mode) => void
  setPage: (page: Page) => void
}) {
  const isRegister = type === 'register'
  const [accountType, setAccountType] = useState<Mode>('hr')

  return (
    <main className="auth-page">
      <Header setPage={setPage} />

      <section className="auth-layout">
        <div className="auth-copy">
          <span className="eyebrow">{isRegister ? 'Create workspace' : 'Welcome back'}</span>
          <h1>{isRegister ? 'Start using CVPilot' : 'Log in to CVPilot'}</h1>
          <p>
            A focused tool for CV review, job fit analysis, and interview preparation.
          </p>
        </div>

        <form
          className="auth-card"
          onSubmit={(event) => {
            event.preventDefault()
            setMode(accountType)
            setPage('dashboard')
          }}
        >
          <div className="auth-title">
            <h2>{isRegister ? 'Register' : 'Log in'}</h2>
            <p>{isRegister ? 'Create a demo workspace.' : 'Continue to your workspace.'}</p>
          </div>

          {isRegister && (
            <div className="mode-tabs" aria-label="Account type">
              <button
                className={accountType === 'hr' ? 'active' : ''}
                type="button"
                onClick={() => setAccountType('hr')}
              >
                <BriefcaseBusiness size={17} />
                HR
              </button>
              <button
                className={accountType === 'candidate' ? 'active' : ''}
                type="button"
                onClick={() => setAccountType('candidate')}
              >
                <UserRound size={17} />
                Candidate
              </button>
            </div>
          )}

          {isRegister && (
            <label>
              <span>{accountType === 'hr' ? 'Company name' : 'Full name'}</span>
              <div className="field-icon">
                <UsersRound size={18} />
                <input placeholder={accountType === 'hr' ? 'Apex Talent' : 'Aysel Mammadova'} />
              </div>
            </label>
          )}

          <label>
            <span>Email</span>
            <div className="field-icon">
              <Mail size={18} />
              <input placeholder="you@example.com" type="email" />
            </div>
          </label>

          <label>
            <span>Password</span>
            <div className="field-icon">
              <LockKeyhole size={18} />
              <input placeholder="Minimum 8 characters" type="password" />
            </div>
          </label>

          <button className="primary-button" type="submit">
            {isRegister ? 'Create account' : 'Log in'}
            <ArrowRight size={18} />
          </button>

          <button
            className="link-button"
            type="button"
            onClick={() => setPage(isRegister ? 'login' : 'register')}
          >
            {isRegister ? 'Already have an account? Log in' : 'Need an account? Register'}
          </button>
        </form>
      </section>
    </main>
  )
}

function Dashboard({
  mode,
  setMode,
  setPage,
}: {
  mode: Mode
  setMode: (mode: Mode) => void
  setPage: (page: Page) => void
}) {
  const [fileName, setFileName] = useState('Aysel_Mammadova_CV.pdf')
  const [cvFile, setCvFile] = useState<File | null>(null)
  const [quantity, setQuantity] = useState('1')
  const [roleTitle, setRoleTitle] = useState('Frontend Engineer')
  const [jobDesc, setJobDesc] = useState(
    'We need a frontend engineer with React, TypeScript, API integration, testing, product thinking, and clear communication skills.'
  )
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const copy = useMemo(
    () =>
      mode === 'hr'
        ? {
            label: 'HR workspace',
            title: 'Candidate analysis',
            subject: 'Role title',
            countLabel: 'Open seats',
            action: 'Analyze candidate',
            summary:
              'Strong shortlist candidate. Validate analytics exposure, cloud ownership, and mentoring experience during the interview.',
          }
        : {
            label: 'Candidate workspace',
            title: 'Job fit analysis',
            subject: 'Target role',
            countLabel: 'Applications',
            action: 'Check my fit',
            summary:
              'Good role fit. Improve the CV by adding analytics examples, deployment ownership, and clearer product outcomes.',
          },
    [mode],
  )

  const handleAnalyze = async () => {
    setError(null)
    if (!cvFile) {
      setError('Please upload a CV file before analyzing.')
      return
    }

    setLoading(true)
    try {
      const result = await analyzeCv(cvFile, jobDesc, roleTitle)
      setAnalysis(result)
    } catch (err: any) {
      setError(err?.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const displayedScore = analysis ? analysis.fit_score.overall_score : 76
  const displayedDetails = analysis
    ? [
        { label: 'Skills match', value: analysis.fit_score.skills_match },
        { label: 'Experience fit', value: analysis.fit_score.experience_fit },
        { label: 'Evidence quality', value: analysis.fit_score.evidence_quality },
      ]
    : scoreDetails

  const displayedStrengths = analysis ? analysis.fit_score.strengths : strengths
  const displayedGaps = analysis ? analysis.fit_score.gaps : gaps
  const displayedQuestions = analysis ? analysis.interview_questions : questions

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div className="header-inner">
          <Brand onClick={() => setPage('landing')} />
          <div className="dashboard-actions">
            <div className="mode-tabs compact-tabs">
              <button className={mode === 'hr' ? 'active' : ''} type="button" onClick={() => setMode('hr')}>
                <BriefcaseBusiness size={17} />
                HR
              </button>
              <button
                className={mode === 'candidate' ? 'active' : ''}
                type="button"
                onClick={() => setMode('candidate')}
              >
                <UserRound size={17} />
                Candidate
              </button>
            </div>
            <button className="secondary-button" type="button" onClick={() => setPage('landing')}>
              <LogOut size={17} />
              Log out
            </button>
          </div>
        </div>
      </header>

      <section className="dashboard-hero">
        <span className="eyebrow">{copy.label}</span>
        <h1>{copy.title}</h1>
        <p>Upload a CV and job description to produce a fit score, decision notes, and an interview kit.</p>
      </section>

      <section className="dashboard-grid">
        <form className="panel input-panel" onSubmit={(e) => e.preventDefault()}>
          <div className="panel-title">
            <h2>Input</h2>
            <p>Provide the CV and role requirements.</p>
          </div>

          <label className="upload-zone">
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(event) => {
                const file = event.target.files?.[0]
                const selected = file?.name
                if (selected) setFileName(selected)
                if (file) setCvFile(file)
              }}
            />
            <Upload size={22} />
            <strong>{fileName}</strong>
            <span>PDF, DOC, DOCX</span>
          </label>

          <div className="form-grid">
            <label>
              <span>{copy.subject}</span>
              <input value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} />
            </label>
            <label>
              <span>{copy.countLabel}</span>
              <input
                min="1"
                type="number"
                value={quantity}
                onChange={(event) => setQuantity(event.target.value)}
              />
            </label>
          </div>

          <label>
            <span>Job description</span>
            <textarea value={jobDesc} onChange={(e) => setJobDesc(e.target.value)} />
          </label>

          {error && <div className="error">{error}</div>}

          <button className="primary-button" type="button" onClick={handleAnalyze} disabled={loading}>
            {loading ? 'Analyzing...' : copy.action}
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="panel score-panel">
          <div className="panel-title">
            <h2>Fit score</h2>
            <p>Overall match based on current data.</p>
          </div>
          <div className="score-number">{Math.round(displayedScore)}%</div>
          <div className="score-list">
            {displayedDetails.map((item) => (
              <div key={item.label}>
                <span>{item.label}</span>
                <strong>{Math.round(item.value)}%</strong>
                <progress max="100" value={Math.round(item.value)} />
              </div>
            ))}
          </div>
        </div>

        <section className="panel wide-panel">
          <div className="panel-title">
            <h2>Decision notes</h2>
            <p>{analysis ? analysis.fit_score.decision_notes : copy.summary}</p>
          </div>
        </section>

        <section className="panel half-panel">
          <div className="panel-title">
            <h2>Strengths</h2>
          </div>
          <ul className="clean-list positive">
            {displayedStrengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>

        <section className="panel half-panel">
          <div className="panel-title">
            <h2>Gaps to validate</h2>
          </div>
          <ul className="clean-list caution">
            {displayedGaps.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>

        <section className="panel wide-panel">
          <div className="panel-title">
            <h2>Interview questions</h2>
            <p>Questions are tailored to the role and the candidate gaps.</p>
          </div>
          <div className="question-grid">
            {displayedQuestions.map((question, index) => (
              <article key={question}>
                <span>{index + 1}</span>
                <p>{question}</p>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  )
}

export default App
