import { useState, useRef, useEffect, useCallback } from 'react'
import config from '../../config'

const QUICK_SYMPTOMS = [
  'Chest Pain', 'Shortness of Breath', 'Fatigue', 'Frequent Urination',
  'Excessive Thirst', 'Blurred Vision', 'Tremor', 'Muscle Stiffness',
  'Persistent Sadness', 'Insomnia', 'Swollen Ankles', 'Dizziness',
  'Nausea', 'Back Pain', 'Heart Palpitations', 'Weight Loss',
  'Difficulty Concentrating', 'Blood in Urine', 'Anxiety',
  'Numbness', 'Headaches', 'High Blood Pressure',
  'Loss of Appetite', 'Sleep Problems', 'Cold Sweats',
  'Jaw Pain', 'Left Arm Pain', 'Vomiting', 'Tingling',
  'Mood Swings', 'Memory Problems', 'Loss of Interest',
  'Hand Tremor', 'Balance Problems', 'Foamy Urine',
  'Itchy Skin', 'Slow Healing Wounds', 'Difficulty Walking',
]

const URGENCY_CONFIG = {
  high: { label: 'High Urgency', color: '#ef4444', bg: 'rgba(239,68,68,0.1)' },
  moderate: { label: 'Moderate', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
  low: { label: 'Low', color: '#22c55e', bg: 'rgba(34,197,94,0.1)' },
}

const TRIAGE_CONFIG = {
  urgent: { label: '🔴 Urgent', color: '#dc2626', bg: 'rgba(220,38,38,0.08)' },
  prompt: { label: '🟠 Prompt', color: '#ea580c', bg: 'rgba(234,88,12,0.08)' },
  standard: { label: '🟡 Standard', color: '#ca8a04', bg: 'rgba(202,138,4,0.08)' },
  informational: { label: '🟢 Informational', color: '#16a34a', bg: 'rgba(22,163,74,0.08)' },
}

const SymptomChecker = ({ onClose, onStartAssessment }) => {
  // ── State ──────────────────────────────
  const [step, setStep] = useState('demographics') // demographics → symptoms → results
  const [demographics, setDemographics] = useState({ age: '', sex: '' })
  const [messages, setMessages] = useState([])
  const [symptoms, setSymptoms] = useState([])
  const [severityMap, setSeverityMap] = useState({})
  const [durationMap, setDurationMap] = useState({})
  const [inputValue, setInputValue] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [showSuggestions, setShowSuggestions] = useState(true)
  const [showDisclaimer, setShowDisclaimer] = useState(true)
  const [autocompleteResults, setAutocompleteResults] = useState([])
  const [showAutocomplete, setShowAutocomplete] = useState(false)
  const [activeSeveritySymptom, setActiveSeveritySymptom] = useState(null)
  const [followUpAnswers, setFollowUpAnswers] = useState({})
  const [isFollowingUp, setIsFollowingUp] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const autocompleteRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => { scrollToBottom() }, [messages, isAnalyzing])

  // Close autocomplete on outside click
  useEffect(() => {
    const handler = (e) => {
      if (autocompleteRef.current && !autocompleteRef.current.contains(e.target)) {
        setShowAutocomplete(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  // ── Demographics Step ──────────────────
  const handleDemographicsSubmit = () => {
    setStep('symptoms')
    setMessages([{
      type: 'ai',
      content: demographics.age || demographics.sex
        ? `Thanks! I've noted your details${demographics.age ? ` (age: ${demographics.age})` : ''}${demographics.sex ? ` (sex: ${demographics.sex})` : ''}. 👋`
        : "Hello! I'm your AI Health Assistant. 👋",
      subtext: "Now tell me about your symptoms. You can type them, use the suggestions below, or describe how you feel in everyday language — I understand natural phrasing!",
      timestamp: new Date(),
    }])
  }

  const handleSkipDemographics = () => {
    setDemographics({ age: '', sex: '' })
    handleDemographicsSubmit()
  }

  // ── Autocomplete ───────────────────────
  const handleInputChange = useCallback((value) => {
    setInputValue(value)
    if (value.trim().length >= 2) {
      const lower = value.toLowerCase()
      const filtered = QUICK_SYMPTOMS.filter(s =>
        s.toLowerCase().includes(lower) &&
        !symptoms.find(ex => ex.toLowerCase() === s.toLowerCase())
      ).slice(0, 6)
      setAutocompleteResults(filtered)
      setShowAutocomplete(filtered.length > 0)
    } else {
      setShowAutocomplete(false)
    }
  }, [symptoms])

  // ── Add Symptom ────────────────────────
  const addSymptom = (symptom) => {
    const trimmed = symptom.trim()
    if (!trimmed) return
    if (symptoms.find(s => s.toLowerCase() === trimmed.toLowerCase())) return

    const updated = [...symptoms, trimmed]
    setSymptoms(updated)
    setActiveSeveritySymptom(trimmed)
    setShowAutocomplete(false)

    setMessages(prev => [...prev, {
      type: 'user', content: trimmed, timestamp: new Date(),
    }])

    const ackMessages = [
      `Noted — "${trimmed}". You can set severity/duration below, or add more symptoms.`,
      `Got it — "${trimmed}". How severe is this symptom? Set it below or keep going.`,
      `"${trimmed}" recorded ✓. Set severity if you'd like, or add more.`,
      `Added "${trimmed}". Any other symptoms you're experiencing?`,
      `Understood — "${trimmed}". I'll factor this into the analysis.`,
    ]
    setTimeout(() => {
      setMessages(prev => [...prev, {
        type: 'ai',
        content: ackMessages[updated.length % ackMessages.length],
        subtext: `${updated.length} symptom${updated.length > 1 ? 's' : ''} recorded so far.`,
        timestamp: new Date(),
      }])
    }, 400)

    setInputValue('')
    setShowSuggestions(false)
    inputRef.current?.focus()
  }

  // ── Severity / Duration ────────────────
  const setSeverity = (symptom, level) => {
    setSeverityMap(prev => ({ ...prev, [symptom]: level }))
  }
  const setDuration = (symptom, dur) => {
    setDurationMap(prev => ({ ...prev, [symptom]: dur }))
  }
  const dismissSeverity = () => setActiveSeveritySymptom(null)

  const removeSymptom = (symptomToRemove) => {
    setSymptoms(prev => prev.filter(s => s !== symptomToRemove))
    setSeverityMap(prev => { const n = { ...prev }; delete n[symptomToRemove]; return n })
    setDurationMap(prev => { const n = { ...prev }; delete n[symptomToRemove]; return n })
    if (activeSeveritySymptom === symptomToRemove) setActiveSeveritySymptom(null)
    setMessages(prev => [...prev, {
      type: 'ai',
      content: `Removed "${symptomToRemove}" from the analysis.`,
      timestamp: new Date(),
    }])
  }

  const handleInputSubmit = (e) => {
    e.preventDefault()
    if (inputValue.trim()) addSymptom(inputValue)
  }

  // ── Analyze ────────────────────────────
  const handleAnalyze = async () => {
    if (symptoms.length === 0) return
    setIsAnalyzing(true)
    setActiveSeveritySymptom(null)
    setMessages(prev => [...prev, {
      type: 'user', content: '🔬 Analyze my symptoms', isAction: true, timestamp: new Date(),
    }])

    try {
      const response = await fetch(`${config.API_URL}/symptom-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symptoms,
          age: demographics.age || undefined,
          sex: demographics.sex || undefined,
          severity_map: severityMap,
        }),
      })
      const data = await response.json()

      if (data.success) {
        setAnalysisResult(data.analysis)
        setStep('results')
        setMessages(prev => [...prev, {
          type: 'ai', content: 'Analysis complete! Here are my findings:',
          isAnalysis: true, analysis: data.analysis, timestamp: new Date(),
        }])
      } else {
        setMessages(prev => [...prev, {
          type: 'ai', content: `Sorry, something went wrong: ${data.error}`,
          isError: true, timestamp: new Date(),
        }])
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        type: 'ai',
        content: `Connection error. Make sure the backend server is running at ${config.API_URL}`,
        isError: true, timestamp: new Date(),
      }])
    } finally {
      setIsAnalyzing(false)
    }
  }

  // ── Follow-up Answers ──────────────────
  const handleFollowUpAnswer = (questionId, answer) => {
    setFollowUpAnswers(prev => ({ ...prev, [questionId]: answer }))
    setMessages(prev => [...prev, {
      type: 'user', content: answer, timestamp: new Date(),
    }])
  }

  const submitFollowUp = async () => {
    setIsFollowingUp(true)
    setMessages(prev => [...prev, {
      type: 'ai', content: 'Refining analysis with your additional answers…',
      subtext: 'Please wait a moment.', timestamp: new Date(),
    }])

    try {
      const response = await fetch(`${config.API_URL}/symptom-followup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symptoms,
          answers: followUpAnswers,
          age: demographics.age || undefined,
          sex: demographics.sex || undefined,
          severity_map: severityMap,
        }),
      })
      const data = await response.json()
      if (data.success) {
        setAnalysisResult(data.analysis)
        setMessages(prev => [...prev, {
          type: 'ai', content: '✅ Updated analysis with your follow-up answers:',
          isAnalysis: true, analysis: data.analysis, timestamp: new Date(),
        }])
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        type: 'ai', content: 'Could not refine analysis. Please try again.',
        isError: true, timestamp: new Date(),
      }])
    } finally {
      setIsFollowingUp(false)
    }
  }

  // ── Follow-up Conversation ─────────────
  const handleAskFollowUp = () => {
    setStep('symptoms')
    setAnalysisResult(null)
    setShowSuggestions(true)
    setMessages(prev => [...prev, {
      type: 'ai',
      content: "Sure! You can add more symptoms or ask me anything. I'll re-analyze with the new information.",
      timestamp: new Date(),
    }])
  }

  // ── Reset ──────────────────────────────
  const handleReset = () => {
    setSymptoms([])
    setSeverityMap({})
    setDurationMap({})
    setAnalysisResult(null)
    setShowSuggestions(true)
    setStep('demographics')
    setDemographics({ age: '', sex: '' })
    setFollowUpAnswers({})
    setActiveSeveritySymptom(null)
    setMessages([])
  }

  const filteredSuggestions = QUICK_SYMPTOMS.filter(
    s => !symptoms.find(existing => existing.toLowerCase() === s.toLowerCase())
  )

  // ══════════════════════════════════════════════════════════════════════
  //  RENDER
  // ══════════════════════════════════════════════════════════════════════
  return (
    <div className="symptom-chat-page">
      {/* ── HIPAA / AI Disclaimer Banner ── */}
      {showDisclaimer && (
        <div className="disclaimer-banner">
          <div className="disclaimer-banner-content">
            <span className="disclaimer-icon">⚕️</span>
            <p>This AI tool is for <strong>informational purposes only</strong> — it does not provide medical advice, diagnosis, or treatment. No data is stored. Always consult a healthcare professional.</p>
            <button className="disclaimer-close" onClick={() => setShowDisclaimer(false)}>✕</button>
          </div>
        </div>
      )}

      {/* ── Header ── */}
      <div className="symptom-chat-header">
        <div className="symptom-chat-header-left">
          <button className="symptom-back-btn" onClick={onClose}>←</button>
          <div className="symptom-chat-avatar">
            <span>🤖</span>
            <span className="avatar-pulse"></span>
          </div>
          <div>
            <h2 className="symptom-chat-title">AI Health Assistant</h2>
            <span className="symptom-chat-status">
              <span className="status-dot"></span>
              {isAnalyzing ? 'Analyzing...' : isFollowingUp ? 'Refining...' : 'Online'}
            </span>
          </div>
        </div>
        <div className="symptom-chat-header-right">
          {(symptoms.length > 0 || step !== 'demographics') && (
            <button className="symptom-reset-btn" onClick={handleReset}>🔄 New Chat</button>
          )}
        </div>
      </div>

      {/* ══════════════ DEMOGRAPHICS STEP ══════════════ */}
      {step === 'demographics' && (
        <div className="symptom-chat-messages">
          <div className="demographic-step">
            <div className="demo-header">
              <span className="demo-icon">👤</span>
              <h3>Before we start</h3>
              <p>Providing your age and sex helps me give more accurate results. You can also skip this step.</p>
            </div>
            <div className="demo-fields">
              <div className="demo-field">
                <label>Age</label>
                <input
                  type="number"
                  min="0" max="120"
                  placeholder="e.g. 35"
                  value={demographics.age}
                  onChange={e => setDemographics(d => ({ ...d, age: e.target.value }))}
                  className="demo-input"
                />
              </div>
              <div className="demo-field">
                <label>Sex</label>
                <div className="demo-radio-group">
                  {['male', 'female', 'other'].map(s => (
                    <button
                      key={s}
                      className={`demo-radio-btn ${demographics.sex === s ? 'active' : ''}`}
                      onClick={() => setDemographics(d => ({ ...d, sex: s }))}
                    >
                      {s === 'male' ? '♂ Male' : s === 'female' ? '♀ Female' : '⚧ Other'}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="demo-actions">
              <button className="demo-continue-btn" onClick={handleDemographicsSubmit}>
                Continue →
              </button>
              <button className="demo-skip-btn" onClick={handleSkipDemographics}>
                Skip this step
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ══════════════ SYMPTOMS & RESULTS ══════════════ */}
      {step !== 'demographics' && (
        <>
          {/* Symptom Tags Bar */}
          {symptoms.length > 0 && (
            <div className="symptom-tags-bar">
              <span className="tags-label">Your symptoms:</span>
              <div className="symptom-tags-list">
                {symptoms.map((s, i) => (
                  <span key={i} className="symptom-tag">
                    {s}
                    {severityMap[s] && severityMap[s] !== 'moderate' && (
                      <span className={`tag-severity tag-severity-${severityMap[s]}`}>
                        {severityMap[s] === 'severe' ? '!!!' : '!'}
                      </span>
                    )}
                    <button className="tag-remove" onClick={() => removeSymptom(s)}>×</button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Messages Area */}
          <div className="symptom-chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-msg ${msg.type === 'ai' ? 'chat-msg-ai' : 'chat-msg-user'}`}>
                {msg.type === 'ai' && <div className="chat-msg-avatar">🤖</div>}
                <div className={`chat-bubble ${msg.type === 'ai' ? 'bubble-ai' : 'bubble-user'} ${msg.isError ? 'bubble-error' : ''} ${msg.isAction ? 'bubble-action' : ''}`}>
                  <p className="bubble-text">{msg.content}</p>
                  {msg.subtext && <p className="bubble-subtext">{msg.subtext}</p>}

                  {/* ── Analysis Result ── */}
                  {msg.isAnalysis && msg.analysis && (
                    <div className="analysis-results">
                      {/* Emergency Banner */}
                      {msg.analysis.emergency && msg.analysis.emergency_alerts?.length > 0 && (
                        <div className="emergency-banner">
                          {msg.analysis.emergency_alerts.map((alert, ai) => (
                            <div key={ai} className="emergency-alert-item">
                              <div className="emergency-alert-header">
                                <span className="emergency-alert-icon">🚨</span>
                                <strong>{alert.name}</strong>
                              </div>
                              <p className="emergency-alert-message">{alert.message}</p>
                              <a href="tel:911" className="emergency-call-btn">{alert.action}</a>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Advice */}
                      <div className={`analysis-advice advice-${msg.analysis.advice?.level || 'informational'}`}>
                        <span className="advice-icon">{msg.analysis.advice?.icon || 'ℹ️'}</span>
                        <div>
                          <p>{msg.analysis.advice?.text || msg.analysis.advice}</p>
                          {msg.analysis.advice?.self_care?.length > 0 && (
                            <ul className="self-care-list">
                              {msg.analysis.advice.self_care.map((tip, ti) => (
                                <li key={ti}>{tip}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </div>

                      {/* Expansion Log */}
                      {msg.analysis.expansion_log?.length > 0 && (
                        <div className="expansion-log">
                          <p className="expansion-title">🔍 NLP Interpretation:</p>
                          {msg.analysis.expansion_log.map((e, ei) => (
                            <span key={ei} className="expansion-item">
                              "{e.original}" → <strong>{e.resolved_to}</strong>
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Body System Grouped Results */}
                      {msg.analysis.body_system_groups?.length > 0 ? (
                        msg.analysis.body_system_groups.map((group, gi) => (
                          <div key={gi} className="body-system-group">
                            <div className="system-header">
                              <span className="system-icon">{group.icon}</span>
                              <h4>{group.system}</h4>
                            </div>
                            {group.diseases.map((disease, di) => (
                              <div key={di} className={`disease-result-card ${di === 0 && gi === 0 ? 'disease-card-top' : ''}`} style={{ animationDelay: `${(gi * 2 + di) * 0.12}s` }}>
                                <div className="disease-card-header">
                                  <div className="disease-card-info">
                                    <span className="disease-card-icon">{disease.icon}</span>
                                    <div>
                                      <h4 className="disease-card-name">{disease.name}</h4>
                                      <p className="disease-card-matched">
                                        {disease.symptom_count} of {disease.total_symptoms_checked} symptoms matched
                                      </p>
                                    </div>
                                  </div>
                                  <div className="disease-card-badges">
                                    <span className="urgency-badge" style={{
                                      color: URGENCY_CONFIG[disease.urgency]?.color,
                                      background: URGENCY_CONFIG[disease.urgency]?.bg,
                                      borderColor: URGENCY_CONFIG[disease.urgency]?.color,
                                    }}>
                                      {URGENCY_CONFIG[disease.urgency]?.label}
                                    </span>
                                    {disease.triage && TRIAGE_CONFIG[disease.triage] && (
                                      <span className="triage-badge" style={{
                                        color: TRIAGE_CONFIG[disease.triage].color,
                                        background: TRIAGE_CONFIG[disease.triage].bg,
                                      }}>
                                        {TRIAGE_CONFIG[disease.triage].label}
                                      </span>
                                    )}
                                  </div>
                                </div>

                                {/* Demographic Notes */}
                                {disease.demographic_notes?.length > 0 && (
                                  <div className="demographic-notes">
                                    {disease.demographic_notes.map((note, ni) => (
                                      <span key={ni} className="demo-note">📊 {note}</span>
                                    ))}
                                  </div>
                                )}

                                {/* Confidence Bar */}
                                <div className="confidence-section">
                                  <div className="confidence-header">
                                    <span className="confidence-label">Match Confidence</span>
                                    <span className="confidence-pct">{Math.round(disease.confidence * 100)}%</span>
                                  </div>
                                  <div className="confidence-bar-track">
                                    <div className="confidence-bar-fill" style={{
                                      width: `${disease.confidence * 100}%`,
                                      background: disease.confidence > 0.6
                                        ? 'linear-gradient(90deg, #ef4444, #f97316)'
                                        : disease.confidence > 0.3
                                          ? 'linear-gradient(90deg, #f59e0b, #eab308)'
                                          : 'linear-gradient(90deg, #22c55e, #4ade80)',
                                    }} />
                                  </div>
                                </div>

                                {/* Matched Symptoms */}
                                <div className="matched-symptoms">
                                  {disease.matched_symptoms.map((ms, mi) => (
                                    <span key={mi} className={`matched-chip ${ms.severity === 'severe' ? 'chip-severe' : ms.severity === 'mild' ? 'chip-mild' : ''}`}>
                                      ✓ {ms.user_input}
                                      {ms.severity !== 'moderate' && <em className="chip-sev">({ms.severity})</em>}
                                    </span>
                                  ))}
                                </div>

                                <p className="disease-card-desc">{disease.description}</p>
                                <button className="disease-assess-btn" onClick={() => onStartAssessment(disease.id)}>
                                  🚀 Start {disease.name} Assessment
                                </button>
                              </div>
                            ))}
                          </div>
                        ))
                      ) : (
                        <div className="no-match-card">
                          <span className="no-match-icon">🔍</span>
                          <p>No strong matches found. Try adding more specific symptoms or consult a healthcare professional.</p>
                        </div>
                      )}

                      {/* Follow-Up Questions */}
                      {msg.analysis.followup_questions?.length > 0 && (
                        <div className="followup-section">
                          <h4 className="followup-title">🔄 Help me refine the analysis</h4>
                          <p className="followup-subtitle">Answer these questions to get more accurate results:</p>
                          {msg.analysis.followup_questions.map((fq, fqi) => (
                            <div key={fqi} className="followup-disease-group">
                              <span className="followup-disease-label">About {fq.disease_name}:</span>
                              {fq.questions.map((q, qi) => (
                                <div key={qi} className="followup-card">
                                  <p className="followup-question">{q.question}</p>
                                  {q.type === 'yesno' ? (
                                    <div className="followup-btn-group">
                                      <button
                                        className={`followup-btn ${followUpAnswers[q.id] === 'yes' ? 'active-yes' : ''}`}
                                        onClick={() => handleFollowUpAnswer(q.id, 'yes')}
                                      >Yes</button>
                                      <button
                                        className={`followup-btn ${followUpAnswers[q.id] === 'no' ? 'active-no' : ''}`}
                                        onClick={() => handleFollowUpAnswer(q.id, 'no')}
                                      >No</button>
                                    </div>
                                  ) : q.type === 'select' ? (
                                    <div className="followup-select-group">
                                      {q.options.map((opt, oi) => (
                                        <button
                                          key={oi}
                                          className={`followup-select-btn ${followUpAnswers[q.id] === opt ? 'active' : ''}`}
                                          onClick={() => handleFollowUpAnswer(q.id, opt)}
                                        >{opt}</button>
                                      ))}
                                    </div>
                                  ) : null}
                                </div>
                              ))}
                            </div>
                          ))}
                          {Object.keys(followUpAnswers).length > 0 && (
                            <button className="followup-submit-btn" onClick={submitFollowUp} disabled={isFollowingUp}>
                              {isFollowingUp ? '⏳ Refining...' : '🔬 Refine Analysis'}
                            </button>
                          )}
                        </div>
                      )}

                      {/* Disclaimer */}
                      <div className="analysis-disclaimer">
                        <span>⚕️</span>
                        <p>{msg.analysis.disclaimer}</p>
                      </div>
                    </div>
                  )}
                </div>
                {msg.type === 'user' && <div className="chat-msg-avatar user-avatar">You</div>}
              </div>
            ))}

            {/* Severity/Duration Picker */}
            {activeSeveritySymptom && step === 'symptoms' && (
              <div className="chat-msg chat-msg-ai">
                <div className="chat-msg-avatar">🤖</div>
                <div className="bubble-ai severity-picker-bubble">
                  <p className="bubble-text">How severe is <strong>"{activeSeveritySymptom}"</strong>?</p>
                  <div className="severity-picker">
                    {['mild', 'moderate', 'severe'].map(lv => (
                      <button key={lv}
                        className={`severity-btn severity-${lv} ${(severityMap[activeSeveritySymptom] || 'moderate') === lv ? 'active' : ''}`}
                        onClick={() => setSeverity(activeSeveritySymptom, lv)}
                      >
                        {lv === 'mild' ? '😐 Mild' : lv === 'moderate' ? '😣 Moderate' : '🔥 Severe'}
                      </button>
                    ))}
                  </div>
                  <p className="bubble-text" style={{ marginTop: '0.5rem' }}>How long have you had it?</p>
                  <div className="duration-picker">
                    {['days', 'weeks', 'months', 'years'].map(d => (
                      <button key={d}
                        className={`duration-btn ${durationMap[activeSeveritySymptom] === d ? 'active' : ''}`}
                        onClick={() => setDuration(activeSeveritySymptom, d)}
                      >
                        {d}
                      </button>
                    ))}
                  </div>
                  <button className="severity-done-btn" onClick={dismissSeverity}>
                    ✓ Done
                  </button>
                </div>
              </div>
            )}

            {/* Typing Indicator */}
            {(isAnalyzing || isFollowingUp) && (
              <div className="chat-msg chat-msg-ai">
                <div className="chat-msg-avatar">🤖</div>
                <div className="bubble-ai typing-bubble">
                  <div className="typing-indicator"><span /><span /><span /></div>
                  <p className="typing-text">{isFollowingUp ? 'Refining analysis...' : 'Analyzing your symptoms...'}</p>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          {showSuggestions && !analysisResult && step === 'symptoms' && (
            <div className="symptom-suggestions">
              <p className="suggestions-label">💡 Common symptoms — click to add:</p>
              <div className="suggestions-grid">
                {filteredSuggestions.slice(0, 18).map((s, i) => (
                  <button key={i} className="suggestion-chip"
                    onClick={() => addSymptom(s)}
                    style={{ animationDelay: `${i * 0.03}s` }}
                  >{s}</button>
                ))}
              </div>
              {filteredSuggestions.length > 18 && (
                <button className="show-more-btn"
                  onClick={() => setShowSuggestions(true)}>
                  +{filteredSuggestions.length - 18} more
                </button>
              )}
            </div>
          )}

          {/* Input Bar */}
          {!analysisResult && step === 'symptoms' && (
            <div className="symptom-input-section">
              <form onSubmit={handleInputSubmit} className="symptom-input-form" ref={autocompleteRef}>
                <div className="autocomplete-wrapper">
                  <input
                    ref={inputRef}
                    type="text"
                    className="symptom-input"
                    placeholder={symptoms.length === 0
                      ? "Describe a symptom… (e.g., chest pain, can't breathe)"
                      : "Add another symptom…"}
                    value={inputValue}
                    onChange={(e) => handleInputChange(e.target.value)}
                    onFocus={() => inputValue.trim().length >= 2 && setShowAutocomplete(autocompleteResults.length > 0)}
                    disabled={isAnalyzing}
                  />
                  {showAutocomplete && (
                    <div className="autocomplete-dropdown">
                      {autocompleteResults.map((r, i) => (
                        <button key={i} type="button" className="autocomplete-item"
                          onClick={() => { addSymptom(r); setShowAutocomplete(false) }}>
                          <span className="autocomplete-match">🔍</span> {r}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <button type="submit" className="symptom-send-btn"
                  disabled={!inputValue.trim() || isAnalyzing}>➕</button>
                <button type="button" className="symptom-analyze-btn"
                  onClick={handleAnalyze}
                  disabled={symptoms.length === 0 || isAnalyzing}>
                  {isAnalyzing ? <span className="analyze-spinner" /> : <>🔬 Analyze ({symptoms.length})</>}
                </button>
              </form>
            </div>
          )}

          {/* Post-Analysis Actions */}
          {analysisResult && (
            <div className="symptom-input-section">
              <div className="post-analysis-actions">
                <button className="symptom-analyze-btn" onClick={handleAskFollowUp}>
                  💬 Ask a Follow-up
                </button>
                <button className="symptom-analyze-btn" onClick={handleReset}>
                  🔄 Start New Analysis
                </button>
                <button className="symptom-send-btn wide" onClick={onClose}>
                  ← Back to Home
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default SymptomChecker
