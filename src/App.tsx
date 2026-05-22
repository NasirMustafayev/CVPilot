import { useCallback, useEffect, useState } from 'react'
import {
  analyzeCv,
  checkApiHealth,
  clearAnalyses,
  fetchAnalysis,
  listAnalyses,
} from './api'
import type { AnalysisResult, AnalysisSummary } from './api'
import {
  fetchCurrentUser,
  getToken,
  loginAccount,
  logout as clearAuthSession,
  registerAccount,
  type AuthUser,
} from './auth'
import type { AppMode } from './modeCopy'
import {
  MODE_COPY,
  buildCvImprovementTips,
  candidateVerdict,
  hiringVerdict,
} from './modeCopy'
import {
  AlertTriangle,
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  ClipboardList,
  Clock,
  FileText,
  Lightbulb,
  LockKeyhole,
  LogOut,
  Mail,
  Target,
  Trash2,
  Upload,
  UserRound,
  UsersRound,
} from 'lucide-react'
import './App.css'

type Page = 'landing' | 'login' | 'register' | 'dashboard'

function App() {
  const [page, setPage] = useState<Page>('landing')
  const [mode, setMode] = useState<AppMode>('hr')
  const [user, setUser] = useState<AuthUser | null>(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [authIntentMode, setAuthIntentMode] = useState<AppMode>('hr')

  useEffect(() => {
    if (!getToken()) {
      setAuthLoading(false)
      return
    }
    fetchCurrentUser()
      .then((current) => {
        setUser(current)
        setMode(current.role)
      })
      .catch(() => clearAuthSession())
      .finally(() => setAuthLoading(false))
  }, [])

  useEffect(() => {
    if (!authLoading && page === 'dashboard' && !user) {
      setPage('login')
    }
  }, [authLoading, page, user])

  const openAuth = (nextPage: 'login' | 'register', intent: AppMode) => {
    setAuthIntentMode(intent)
    setPage(nextPage)
  }

  const handleAuthSuccess = (authUser: AuthUser) => {
    setUser(authUser)
    setMode(authUser.role)
    setPage('dashboard')
  }

  const handleLogout = () => {
    clearAuthSession()
    setUser(null)
    setPage('landing')
  }

  if (authLoading) {
    return (
      <main className="auth-loading-screen">
        <p>Loading session…</p>
      </main>
    )
  }

  if (page === 'login') {
    return (
      <AuthScreen
        type="login"
        setPage={setPage}
        initialMode={authIntentMode}
        onSuccess={handleAuthSuccess}
      />
    )
  }

  if (page === 'register') {
    return (
      <AuthScreen
        type="register"
        setPage={setPage}
        initialMode={authIntentMode}
        onSuccess={handleAuthSuccess}
      />
    )
  }

  if (page === 'dashboard' && user) {
    return (
      <Dashboard
        user={user}
        mode={mode}
        setMode={setMode}
        setPage={setPage}
        onLogout={handleLogout}
      />
    )
  }

  const openDashboard = () => {
    if (user) {
      setMode(user.role)
      setPage('dashboard')
    }
  }

  return (
    <LandingPage user={user} openAuth={openAuth} setPage={setPage} onOpenDashboard={openDashboard} />
  )
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
  user,
  openAuth,
  setPage,
  onOpenDashboard,
}: {
  user: AuthUser | null
  openAuth: (page: 'login' | 'register', intent: AppMode) => void
  setPage: (page: Page) => void
  onOpenDashboard: () => void
}) {
  return (
    <main className="page">
      <Header setPage={setPage} user={user} onOpenDashboard={onOpenDashboard} />

      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">Two workspaces, one engine</span>
          <h1>Hire with confidence. Apply with clarity.</h1>
          <p>
            HR teams evaluate applicants against a role. Candidates test their own CV
            before sending an application.
          </p>
          <div className="actions">
            <button
              className="primary-button"
              type="button"
              onClick={() => (user ? onOpenDashboard() : openAuth('register', 'hr'))}
            >
              {user ? 'Go to HR workspace' : 'HR — get started'}
              <ArrowRight size={18} />
            </button>
            <button
              className="secondary-button"
              type="button"
              onClick={() =>
                user ? onOpenDashboard() : openAuth('register', 'candidate')
              }
            >
              {user ? 'Go to candidate workspace' : 'Candidate — get started'}
            </button>
          </div>
        </div>

        <div className="analysis-preview dual-preview" aria-label="CVPilot preview">
          <div className="preview-card preview-hr">
            <span className="preview-tag">HR view</span>
            <div className="preview-header">
              <span>Hiring fit</span>
              <strong>82%</strong>
            </div>
            <div className="score-line">
              <span style={{ width: '82%' }} />
            </div>
            <p><CheckCircle2 size={17} /> Recommend interview</p>
            <p><AlertTriangle size={17} /> Validate cloud ownership</p>
          </div>
          <div className="preview-card preview-candidate">
            <span className="preview-tag">Candidate view</span>
            <div className="preview-header">
              <span>Your fit</span>
              <strong>71%</strong>
            </div>
            <div className="score-line">
              <span style={{ width: '71%' }} />
            </div>
            <p><Target size={17} /> Competitive with gaps</p>
            <p><Lightbulb size={17} /> Add API project examples</p>
          </div>
        </div>
      </section>

      <section className="section" id="features">
        <div className="section-heading">
          <span>Who it is for</span>
          <h2>Different goals, tailored workflows</h2>
        </div>
        <div className="feature-grid role-feature-grid">
          <article className="role-feature hr-feature">
            <BriefcaseBusiness size={22} />
            <h3>For HR & recruiters</h3>
            <p>Upload applicant CVs, score fit, get hiring recommendations, and interview kits.</p>
            <button
              className="text-cta"
              type="button"
              onClick={() => (user ? onOpenDashboard() : openAuth('register', 'hr'))}
            >
              {user ? 'Open workspace' : 'Register as HR'}
            </button>
          </article>
          <article className="role-feature candidate-feature">
            <UserRound size={22} />
            <h3>For job seekers</h3>
            <p>Test your CV against a job post, see gaps, and get a concrete improvement plan.</p>
            <button
              className="text-cta"
              type="button"
              onClick={() =>
                user ? onOpenDashboard() : openAuth('register', 'candidate')
              }
            >
              {user ? 'Open workspace' : 'Register as candidate'}
            </button>
          </article>
        </div>
      </section>
    </main>
  )
}

function Header({
  setPage,
  user,
  onOpenDashboard,
}: {
  setPage: (page: Page) => void
  user?: AuthUser | null
  onOpenDashboard?: () => void
}) {
  return (
    <header className="header">
      <div className="header-inner">
        <Brand onClick={() => setPage('landing')} />
        <nav className="site-nav" aria-label="Primary navigation">
          {user ? (
            <>
              <span className="nav-user-pill">{user.display_name}</span>
              <button className="nav-btn nav-btn-primary" type="button" onClick={onOpenDashboard}>
                Dashboard
              </button>
            </>
          ) : (
            <>
              <button className="nav-btn nav-btn-ghost" type="button" onClick={() => setPage('login')}>
                Log in
              </button>
              <button className="nav-btn nav-btn-primary" type="button" onClick={() => setPage('register')}>
                Get started
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

function AuthScreen({
  type,
  setPage,
  initialMode,
  onSuccess,
}: {
  type: 'login' | 'register'
  setPage: (page: Page) => void
  initialMode: AppMode
  onSuccess: (user: AuthUser) => void
}) {
  const isRegister = type === 'register'
  const [accountType, setAccountType] = useState<AppMode>(initialMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const authBlurb =
    accountType === 'hr'
      ? 'Screen applicants faster: fit scores, hiring notes, and interview questions.'
      : 'Check if your CV matches a role before you apply, and what to fix first.'

  return (
    <main className="auth-page">
      <Header setPage={setPage} />

      <section className="auth-layout">
        <div className="auth-copy">
          <span className="eyebrow">{isRegister ? 'Create workspace' : 'Welcome back'}</span>
          <h1>
            {accountType === 'hr'
              ? 'CVPilot for hiring teams'
              : 'CVPilot for your job search'}
          </h1>
          <p>{authBlurb}</p>
        </div>

        <form
          className="auth-card"
          onSubmit={async (event) => {
            event.preventDefault()
            setError(null)
            setLoading(true)
            try {
              if (isRegister) {
                const { user } = await registerAccount({
                  email,
                  password,
                  role: accountType,
                  display_name: displayName,
                })
                onSuccess(user)
              } else {
                const { user } = await loginAccount(email, password)
                onSuccess(user)
              }
            } catch (err: unknown) {
              setError(err instanceof Error ? err.message : 'Authentication failed')
            } finally {
              setLoading(false)
            }
          }}
        >
          <div className="auth-title">
            <h2>{isRegister ? 'Register' : 'Log in'}</h2>
            <p>{isRegister ? 'Choose how you will use CVPilot.' : 'Continue to your workspace.'}</p>
          </div>

          {isRegister && (
            <div className="mode-tabs" aria-label="Workspace type">
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
                <input
                  required
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder={accountType === 'hr' ? 'Apex Talent' : 'Aysel Mammadova'}
                />
              </div>
            </label>
          )}

          <label>
            <span>Email</span>
            <div className="field-icon">
              <Mail size={18} />
              <input
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                type="email"
                autoComplete="email"
              />
            </div>
          </label>

          <label>
            <span>Password</span>
            <div className="field-icon">
              <LockKeyhole size={18} />
              <input
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 8 characters"
                type="password"
                autoComplete={isRegister ? 'new-password' : 'current-password'}
              />
            </div>
          </label>

          {error && <div className="error">{error}</div>}

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? 'Please wait…' : isRegister ? 'Create account' : 'Log in'}
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
  user,
  mode,
  setMode,
  setPage,
  onLogout,
}: {
  user: AuthUser
  mode: AppMode
  setMode: (mode: AppMode) => void
  setPage: (page: Page) => void
  onLogout: () => void
}) {
  const [fileName, setFileName] = useState('No file selected')
  const [cvFile, setCvFile] = useState<File | null>(null)
  const [roleTitle, setRoleTitle] = useState('Frontend Engineer')
  const [jobDesc, setJobDesc] = useState(
    'We need a frontend engineer with React, TypeScript, API integration, testing, product thinking, and clear communication skills.',
  )
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [history, setHistory] = useState<AnalysisSummary[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)

  const copy = MODE_COPY[mode]

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true)
    try {
      const items = await listAnalyses(mode)
      setHistory(items)
    } catch {
      setHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }, [mode])

  useEffect(() => {
    checkApiHealth().then(setApiOnline)
  }, [])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  const switchMode = (next: AppMode) => {
    if (next !== mode) {
      setAnalysis(null)
      setSelectedId(null)
      setError(null)
      setFileName('No file selected')
      setCvFile(null)
    }
    setMode(next)
  }

  const handleClearHistory = async () => {
    if (!window.confirm(copy.clearHistoryConfirm)) return
    setError(null)
    try {
      await clearAnalyses(mode)
      setHistory([])
      setSelectedId(null)
      setAnalysis(null)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to clear history')
    }
  }

  const openSavedAnalysis = async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchAnalysis(id)
      setAnalysis(result)
      setSelectedId(id)
      if (result.role_title) setRoleTitle(result.role_title)
      if (result.job_description) setJobDesc(result.job_description)
      if (result.cv_filename) setFileName(result.cv_filename)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Could not load saved analysis')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    setError(null)
    if (!cvFile) {
      setError(
        mode === 'hr'
          ? 'Upload the candidate CV before evaluating.'
          : 'Upload your CV before running a fit check.',
      )
      return
    }

    setLoading(true)
    try {
      const result = await analyzeCv(cvFile, jobDesc, roleTitle, mode)
      setAnalysis(result)
      setSelectedId(result.id ?? null)
      if (result.cv_filename) setFileName(result.cv_filename)
      await loadHistory()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Analysis failed'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const scoreLabels = [
    { label: 'Skills match', value: analysis?.fit_score.skills_match },
    { label: 'Experience fit', value: analysis?.fit_score.experience_fit },
    { label: 'Evidence quality', value: analysis?.fit_score.evidence_quality },
  ]

  const verdict = analysis
    ? mode === 'hr'
      ? hiringVerdict(analysis.fit_score.overall_score)
      : candidateVerdict(analysis.fit_score.overall_score)
    : null

  const improvementTips = analysis && mode === 'candidate' ? buildCvImprovementTips(analysis) : []
  const showHistory = !historyLoading && history.length > 0

  return (
    <main className={`dashboard-page dashboard-${mode}`}>
      <header className="dashboard-header">
        <div className="header-inner">
          <Brand onClick={() => setPage('landing')} />
          <div className="dashboard-actions">
            <div className="mode-tabs compact-tabs" role="tablist" aria-label="Workspace type">
              <button
                className={mode === 'hr' ? 'active' : ''}
                type="button"
                role="tab"
                aria-selected={mode === 'hr'}
                onClick={() => switchMode('hr')}
              >
                <BriefcaseBusiness size={17} />
                HR
              </button>
              <button
                className={mode === 'candidate' ? 'active' : ''}
                type="button"
                role="tab"
                aria-selected={mode === 'candidate'}
                onClick={() => switchMode('candidate')}
              >
                <UserRound size={17} />
                Candidate
              </button>
            </div>
            <span className="nav-user dashboard-user">{user.display_name}</span>
            <button className="secondary-button" type="button" onClick={onLogout}>
              <LogOut size={17} />
              Log out
            </button>
          </div>
        </div>
      </header>

      <section className="dashboard-hero">
        <span className={`eyebrow mode-eyebrow mode-eyebrow-${mode}`}>{copy.label}</span>
        <h1>{copy.title}</h1>
        <p>{copy.subtitle}</p>
        {apiOnline === false && (
          <p className="api-warning">
            Analysis API is offline. Start the backend:{' '}
            <code>cd backend && python -m uvicorn main:app --reload --port 8000</code>
          </p>
        )}
        {analysis && (
          <p className="analysis-meta">
            {mode === 'hr' ? 'Candidate evaluation' : 'Personal fit check'} ·{' '}
            {analysis.analysis_mode === 'llm' ? 'AI-enhanced' : 'Requirement-based'}
            {analysis.matched_skills.length > 0 && (
              <> · {analysis.matched_skills.length} skills matched</>
            )}
          </p>
        )}
      </section>

      <section className="dashboard-grid">
        <form className="panel input-panel" onSubmit={(e) => e.preventDefault()}>
          <div className="panel-title">
            <h2>{copy.inputTitle}</h2>
            <p>{copy.inputHint}</p>
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
            <span>{cvFile ? copy.uploadHint : `${copy.uploadHint} — required`}</span>
          </label>

          <label>
            <span>{copy.roleLabel}</span>
            <input value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} />
          </label>

          <label>
            <span>{copy.jobLabel}</span>
            <textarea
              value={jobDesc}
              onChange={(e) => setJobDesc(e.target.value)}
              placeholder={copy.jobPlaceholder}
            />
          </label>

          {error && <div className="error">{error}</div>}

          <button className="primary-button" type="button" onClick={handleAnalyze} disabled={loading}>
            {loading ? copy.actionLoading : copy.action}
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="panel score-panel">
          <div className="panel-title">
            <h2>{copy.scoreTitle}</h2>
            <p>{analysis ? copy.scoreHint : copy.scoreEmpty}</p>
          </div>
          {analysis && verdict ? (
            <>
              <div className={`verdict-badge verdict-${verdict.tone}`}>
                <span>{verdict.label}</span>
                <p>
                  {mode === 'hr'
                    ? (verdict as ReturnType<typeof hiringVerdict>).recommendation
                    : (verdict as ReturnType<typeof candidateVerdict>).advice}
                </p>
              </div>
              <div className="score-number">{Math.round(analysis.fit_score.overall_score)}%</div>
              <div className="score-list">
                {scoreLabels.map((item) => (
                  <div key={item.label}>
                    <span>{item.label}</span>
                    <strong>{Math.round(item.value ?? 0)}%</strong>
                    <progress max="100" value={Math.round(item.value ?? 0)} />
                  </div>
                ))}
              </div>
              {mode === 'hr' ? (
                <>
                  {analysis.missing_skills.length > 0 && (
                    <div className="skill-tags missing">
                      <span>Not evidenced in CV:</span>
                      {analysis.missing_skills.map((s) => (
                        <em key={s}>{s}</em>
                      ))}
                    </div>
                  )}
                  {analysis.matched_skills.length > 0 && (
                    <div className="skill-tags matched">
                      <span>Confirmed skills:</span>
                      {analysis.matched_skills.map((s) => (
                        <em key={s}>{s}</em>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <>
                  {analysis.matched_skills.length > 0 && (
                    <div className="skill-tags matched">
                      <span>You already show:</span>
                      {analysis.matched_skills.map((s) => (
                        <em key={s}>{s}</em>
                      ))}
                    </div>
                  )}
                  {analysis.missing_skills.length > 0 && (
                    <div className="skill-tags missing">
                      <span>Add evidence for:</span>
                      {analysis.missing_skills.map((s) => (
                        <em key={s}>{s}</em>
                      ))}
                    </div>
                  )}
                </>
              )}
            </>
          ) : (
            <div className="empty-state">
              <p>{copy.scoreEmpty}</p>
            </div>
          )}
        </div>

        {showHistory && (
          <section className="panel history-bar">
            <div className="history-bar-header">
              <div className="panel-title">
                <h2>{copy.historyTitle}</h2>
                <p>{copy.historyHint}</p>
              </div>
              <button
                className="secondary-button history-clear-btn"
                type="button"
                onClick={handleClearHistory}
                disabled={loading}
              >
                <Trash2 size={16} />
                {copy.clearHistory}
              </button>
            </div>
            <ul className="history-list history-list-horizontal">
              {history.map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    className={selectedId === item.id ? 'history-item active' : 'history-item'}
                    onClick={() => openSavedAnalysis(item.id)}
                    disabled={loading}
                  >
                    <div className="history-item-top">
                      <strong>{Math.round(item.overall_score)}%</strong>
                      <span className="history-date">
                        <Clock size={14} />
                        {formatHistoryDate(item.created_at)}
                      </span>
                    </div>
                    <span className="history-role">{item.role_title}</span>
                    <span className="history-file">
                      {mode === 'hr' && item.candidate_name
                        ? `${item.candidate_name} · `
                        : ''}
                      {item.cv_filename}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        {analysis && (
          <section className="panel wide-panel extracted-panel">
            <div className="panel-title">
              <h2>{copy.extractedTitle}</h2>
              <p>{copy.extractedHint}</p>
            </div>
            <ExtractedCvSummary analysis={analysis} mode={mode} />
          </section>
        )}

        <section className="panel wide-panel decision-panel">
          <div className="panel-title">
            <h2>{copy.decisionTitle}</h2>
            <p>
              {analysis ? analysis.fit_score.decision_notes : copy.decisionEmpty}
            </p>
          </div>
          {mode === 'hr' && analysis && verdict && (
            <div className={`hiring-action hiring-action-${verdict.tone}`}>
              <ClipboardList size={20} />
              <strong>{(verdict as ReturnType<typeof hiringVerdict>).recommendation}</strong>
            </div>
          )}
        </section>

        <section className="panel half-panel">
          <div className="panel-title">
            <h2>{copy.strengthsTitle}</h2>
          </div>
          {analysis ? (
            <ul className="clean-list positive">
              {analysis.fit_score.strengths.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-inline">{copy.strengthsEmpty}</p>
          )}
        </section>

        <section className="panel half-panel">
          <div className="panel-title">
            <h2>{copy.gapsTitle}</h2>
          </div>
          {analysis ? (
            <ul className={`clean-list ${mode === 'hr' ? 'caution' : 'improve'}`}>
              {analysis.fit_score.gaps.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="empty-inline">{copy.gapsEmpty}</p>
          )}
        </section>

        {mode === 'candidate' && (
          <section className="panel wide-panel tips-panel">
            <div className="panel-title">
              <h2>{MODE_COPY.candidate.tipsTitle}</h2>
              <p>
                {analysis
                  ? MODE_COPY.candidate.tipsHint
                  : MODE_COPY.candidate.tipsEmpty}
              </p>
            </div>
            {analysis && improvementTips.length > 0 ? (
              <ul className="tips-list">
                {improvementTips.map((tip) => (
                  <li key={tip}>
                    <Lightbulb size={18} />
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-inline">{MODE_COPY.candidate.tipsEmpty}</p>
            )}
          </section>
        )}

        <section className="panel wide-panel questions-panel">
          <div className="panel-title">
            <h2>{copy.questionsTitle}</h2>
            <p>{analysis ? copy.questionsHint : copy.questionsEmpty}</p>
          </div>
          {analysis ? (
            <div className="question-grid">
              {analysis.interview_questions.map((question, index) => (
                <article key={question}>
                  <span>{index + 1}</span>
                  <p>{question}</p>
                </article>
              ))}
            </div>
          ) : (
            <p className="empty-inline">{copy.questionsEmpty}</p>
          )}
        </section>

        {mode === 'hr' && !analysis && (
          <section className="panel wide-panel workflow-hint">
            <FileText size={22} />
            <div>
              <h3>Typical HR workflow</h3>
              <p>
                Paste the job description, upload the applicant CV, then use the hiring
                score, recommendation, and interview kit to shortlist or reject.
              </p>
            </div>
          </section>
        )}

        {mode === 'candidate' && !analysis && (
          <section className="panel wide-panel workflow-hint candidate-hint">
            <Target size={22} />
            <div>
              <h3>How candidates use CVPilot</h3>
              <p>
                Paste a job you want, upload your CV, and see fit %, missing skills, CV
                edits, and interview prep — before you hit apply.
              </p>
            </div>
          </section>
        )}
      </section>
    </main>
  )
}

function ExtractedCvSummary({
  analysis,
  mode,
}: {
  analysis: AnalysisResult
  mode: AppMode
}) {
  const { cv_data } = analysis

  return (
    <div className="extracted-grid">
      {mode === 'hr' && (
        <div>
          <h3>Candidate contact</h3>
          <ul className="meta-list">
            {cv_data.contact.name && <li>{cv_data.contact.name}</li>}
            {cv_data.contact.email && <li>{cv_data.contact.email}</li>}
            {cv_data.contact.phone && <li>{cv_data.contact.phone}</li>}
            {!cv_data.contact.name && !cv_data.contact.email && (
              <li className="muted">Limited contact info detected</li>
            )}
          </ul>
        </div>
      )}
      <div className={mode === 'candidate' ? 'extracted-span' : ''}>
        <h3>{mode === 'hr' ? 'Technical skills detected' : 'Skills on your CV'}</h3>
        <p className="tag-row">
          {cv_data.skills.technical.length > 0
            ? cv_data.skills.technical.join(', ')
            : 'None detected — improve formatting or add a Skills section'}
        </p>
      </div>
      <div className="extracted-span">
        <h3>Experience ({cv_data.experience.length} roles)</h3>
        {cv_data.experience.length === 0 ? (
          <p className="muted">
            {mode === 'hr'
              ? 'No roles parsed — verify CV layout before trusting the score.'
              : 'No roles parsed — add a clear Experience section with dates.'}
          </p>
        ) : (
          <ul className="experience-list">
            {cv_data.experience.slice(0, 4).map((exp) => (
              <li key={`${exp.role}-${exp.company}`}>
                <strong>{exp.role}</strong>
                {exp.company ? ` · ${exp.company}` : ''}
                {exp.description && (
                  <span>
                    {exp.description.length > 120
                      ? `${exp.description.slice(0, 120)}…`
                      : exp.description}
                  </span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function formatHistoryDate(iso: string): string {
  try {
    const date = new Date(iso)
    return date.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso.slice(0, 10)
  }
}

export default App
