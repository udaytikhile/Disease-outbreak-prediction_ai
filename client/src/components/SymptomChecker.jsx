import { useState } from 'react'

const SymptomChecker = ({ onClose, onStartAssessment }) => {
    const [step, setStep] = useState(0)
    const [answers, setAnswers] = useState({})

    const questions = [
        {
            id: 'general',
            question: 'What best describes your primary concern?',
            icon: '🤔',
            options: [
                { label: 'Chest pain or heart-related', value: 'heart', icon: '❤️' },
                { label: 'Blood sugar or metabolism concerns', value: 'diabetes', icon: '🩺' },
                { label: 'Movement or neurological issues', value: 'parkinsons', icon: '🧠' },
                { label: 'Not sure, help me decide', value: 'unsure', icon: '❓' }
            ]
        },
        {
            id: 'heart_symptoms',
            question: 'Are you experiencing any of these heart-related symptoms?',
            icon: '❤️',
            showIf: (ans) => ans.general === 'heart' || ans.general === 'unsure',
            options: [
                { label: 'Chest pain or tightness', value: 'chest_pain', icon: '😰' },
                { label: 'Shortness of breath', value: 'breath', icon: '😮‍💨' },
                { label: 'Irregular heartbeat', value: 'irregular', icon: '💓' },
                { label: 'None of these', value: 'none', icon: '✅' }
            ],
            multi: true
        },
        {
            id: 'diabetes_symptoms',
            question: 'Are you experiencing any of these diabetes-related symptoms?',
            icon: '🩺',
            showIf: (ans) => ans.general === 'diabetes' || ans.general === 'unsure',
            options: [
                { label: 'Frequent urination', value: 'urination', icon: '🚿' },
                { label: 'Excessive thirst', value: 'thirst', icon: '💧' },
                { label: 'Blurred vision', value: 'vision', icon: '👁️' },
                { label: 'Unexplained weight changes', value: 'weight', icon: '⚖️' },
                { label: 'None of these', value: 'none', icon: '✅' }
            ],
            multi: true
        },
        {
            id: 'parkinsons_symptoms',
            question: "Are you experiencing any of these neurological symptoms?",
            icon: '🧠',
            showIf: (ans) => ans.general === 'parkinsons' || ans.general === 'unsure',
            options: [
                { label: 'Tremor or shaking', value: 'tremor', icon: '🫨' },
                { label: 'Muscle stiffness', value: 'stiff', icon: '💪' },
                { label: 'Balance/coordination issues', value: 'balance', icon: '🚶' },
                { label: 'Speech or writing changes', value: 'speech', icon: '🗣️' },
                { label: 'None of these', value: 'none', icon: '✅' }
            ],
            multi: true
        },
        {
            id: 'lifestyle',
            question: 'Tell us about your lifestyle:',
            icon: '🏃',
            options: [
                { label: 'I exercise regularly', value: 'active', icon: '🏋️' },
                { label: 'Mostly sedentary', value: 'sedentary', icon: '🛋️' },
                { label: 'I smoke or drink regularly', value: 'habits', icon: '🚬' },
                { label: 'Healthy diet, active lifestyle', value: 'healthy', icon: '🥗' }
            ],
            multi: true
        },
        {
            id: 'age_group',
            question: 'What is your age group?',
            icon: '📅',
            options: [
                { label: 'Under 30', value: 'young', icon: '🧑' },
                { label: '30-45', value: 'middle', icon: '👨' },
                { label: '45-60', value: 'senior', icon: '👴' },
                { label: 'Over 60', value: 'elderly', icon: '🧓' }
            ]
        }
    ]

    // Filter questions based on answers
    const visibleQuestions = questions.filter(q => !q.showIf || q.showIf(answers))

    const currentQ = visibleQuestions[step]
    const isLast = step >= visibleQuestions.length - 1

    const handleAnswer = (questionId, value, multi) => {
        if (multi) {
            const current = answers[questionId] || []
            const updated = current.includes(value)
                ? current.filter(v => v !== value)
                : [...current.filter(v => v !== 'none'), ...(value === 'none' ? [] : [value])]

            if (value === 'none') {
                setAnswers(prev => ({ ...prev, [questionId]: ['none'] }))
            } else {
                setAnswers(prev => ({ ...prev, [questionId]: updated }))
            }
        } else {
            const updatedAnswers = { ...answers, [questionId]: value }
            setAnswers(updatedAnswers)
            // Recompute visible questions with the NEW answers to get correct isLast
            const updatedVisible = questions.filter(q => !q.showIf || q.showIf(updatedAnswers))
            const willBeAtLast = step >= updatedVisible.length - 1
            if (!willBeAtLast) {
                setTimeout(() => setStep(s => s + 1), 300)
            }
        }
    }

    const getRecommendation = () => {
        const general = answers.general
        if (general && general !== 'unsure') return general

        // Score based on symptoms
        let scores = { heart: 0, diabetes: 0, parkinsons: 0 }

        const hs = answers.heart_symptoms || []
        if (!hs.includes('none')) scores.heart += hs.length * 2

        const ds = answers.diabetes_symptoms || []
        if (!ds.includes('none')) scores.diabetes += ds.length * 2

        const ps = answers.parkinsons_symptoms || []
        if (!ps.includes('none')) scores.parkinsons += ps.length * 2

        // Age factor
        if (answers.age_group === 'elderly') { scores.parkinsons += 2; scores.heart += 1 }
        if (answers.age_group === 'senior') { scores.heart += 2; scores.diabetes += 1 }

        const highest = Object.entries(scores).sort((a, b) => b[1] - a[1])[0]
        if (highest[1] === 0) return 'heart' // Default
        return highest[0]
    }

    const diseaseNames = {
        heart: 'Heart Disease',
        diabetes: 'Diabetes',
        parkinsons: "Parkinson's Disease"
    }

    const diseaseIcons = {
        heart: '❤️',
        diabetes: '🩺',
        parkinsons: '🧠'
    }

    const progress = ((step + 1) / visibleQuestions.length) * 100

    return (
        <div className="checker-container">
            <div className="checker-header">
                <div>
                    <h2 className="checker-title">🔍 Symptom Quick Check</h2>
                    <p className="checker-subtitle">Answer a few questions to find the right assessment</p>
                </div>
                <button className="btn btn-secondary" onClick={onClose} style={{ width: 'auto' }}>
                    ← Back
                </button>
            </div>

            {/* Progress Bar */}
            <div className="checker-progress">
                <div className="checker-progress-bar" style={{ width: `${progress}%` }}></div>
            </div>
            <p className="checker-step-label">Question {step + 1} of {visibleQuestions.length}</p>

            {/* Question */}
            {currentQ && !isLast ? (
                <div className="checker-question animate-in">
                    <div className="question-icon">{currentQ.icon}</div>
                    <h3 className="question-text">{currentQ.question}</h3>
                    <div className="question-options">
                        {currentQ.options.map((opt, i) => {
                            const isSelected = currentQ.multi
                                ? (answers[currentQ.id] || []).includes(opt.value)
                                : answers[currentQ.id] === opt.value
                            return (
                                <button
                                    key={i}
                                    className={`question-option ${isSelected ? 'selected' : ''}`}
                                    onClick={() => handleAnswer(currentQ.id, opt.value, currentQ.multi)}
                                    style={{ animationDelay: `${i * 0.08}s` }}
                                >
                                    <span className="option-icon">{opt.icon}</span>
                                    <span className="option-label">{opt.label}</span>
                                    {currentQ.multi && (
                                        <span className="option-check">{isSelected ? '☑' : '☐'}</span>
                                    )}
                                </button>
                            )
                        })}
                    </div>
                    {currentQ.multi && (
                        <button
                            className="btn btn-primary"
                            onClick={() => setStep(s => s + 1)}
                            disabled={!(answers[currentQ.id]?.length > 0)}
                            style={{ marginTop: '1.5rem' }}
                        >
                            Continue →
                        </button>
                    )}
                </div>
            ) : currentQ ? (
                /* Last question — show it then result */
                <div className="checker-question animate-in">
                    <div className="question-icon">{currentQ.icon}</div>
                    <h3 className="question-text">{currentQ.question}</h3>
                    <div className="question-options">
                        {currentQ.options.map((opt, i) => {
                            const isSelected = answers[currentQ.id] === opt.value
                            return (
                                <button
                                    key={i}
                                    className={`question-option ${isSelected ? 'selected' : ''}`}
                                    onClick={() => handleAnswer(currentQ.id, opt.value, currentQ.multi)}
                                    style={{ animationDelay: `${i * 0.08}s` }}
                                >
                                    <span className="option-icon">{opt.icon}</span>
                                    <span className="option-label">{opt.label}</span>
                                </button>
                            )
                        })}
                    </div>
                    {answers[currentQ.id] && (
                        <div className="checker-result animate-in" style={{ marginTop: '2rem' }}>
                            <div className="result-recommendation">
                                <span className="rec-icon">{diseaseIcons[getRecommendation()]}</span>
                                <div>
                                    <h3>Recommended Assessment</h3>
                                    <p className="rec-disease">{diseaseNames[getRecommendation()]}</p>
                                    <p className="rec-note">Based on your responses, we suggest starting with this assessment.</p>
                                </div>
                            </div>
                            <button
                                className="btn btn-primary btn-large"
                                onClick={() => onStartAssessment(getRecommendation())}
                                style={{ marginTop: '1.5rem', width: '100%' }}
                            >
                                🚀 Start {diseaseNames[getRecommendation()]} Assessment
                            </button>
                            <div className="other-options">
                                <p>Or choose another assessment:</p>
                                <div className="other-buttons">
                                    {Object.entries(diseaseNames)
                                        .filter(([key]) => key !== getRecommendation())
                                        .map(([key, name]) => (
                                            <button
                                                key={key}
                                                className="btn btn-secondary"
                                                onClick={() => onStartAssessment(key)}
                                                style={{ width: 'auto', fontSize: '0.95rem' }}
                                            >
                                                {diseaseIcons[key]} {name}
                                            </button>
                                        ))}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            ) : null}

            {/* Navigation */}
            {step > 0 && (
                <button
                    className="btn btn-secondary checker-back"
                    onClick={() => setStep(s => s - 1)}
                    style={{ width: 'auto', marginTop: '1rem' }}
                >
                    ← Previous Question
                </button>
            )}
        </div>
    )
}

export default SymptomChecker
