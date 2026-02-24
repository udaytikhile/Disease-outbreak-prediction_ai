const LoadingAnalysis = ({ disease }) => {
    const diseaseInfo = {
        heart: { icon: '❤️', name: 'Heart Disease', color: '#ef4444' },
        diabetes: { icon: '🩺', name: 'Diabetes', color: '#3b82f6' },
        kidney: { icon: '🫘', name: 'Kidney Disease', color: '#10b981' },
        depression: { icon: '🧠', name: 'Depression', color: '#8b5cf6' },
    }

    const info = diseaseInfo[disease] || { icon: '🔬', name: 'Health', color: '#6366f1' }

    const steps = [
        { label: 'Validating input data', delay: 0 },
        { label: 'Loading ML model', delay: 0.4 },
        { label: 'Running prediction analysis', delay: 0.8 },
        { label: 'Computing confidence scores', delay: 1.2 },
        { label: 'Generating results', delay: 1.6 },
    ]

    return (
        <div className="ai-loading-overlay">
            <div className="ai-loading-card">
                {/* Animated rings */}
                <div className="ai-loading-rings">
                    <div className="ai-ring ai-ring-1" style={{ borderColor: `${info.color}33`, borderTopColor: info.color }} />
                    <div className="ai-ring ai-ring-2" style={{ borderColor: `${info.color}22`, borderTopColor: `${info.color}88` }} />
                    <div className="ai-ring ai-ring-3" style={{ borderColor: `${info.color}11`, borderTopColor: `${info.color}44` }} />
                    <div className="ai-loading-center">
                        <span className="ai-loading-emoji">{info.icon}</span>
                    </div>
                </div>

                {/* Title */}
                <h3 className="ai-loading-title">Analyzing Your Data</h3>
                <p className="ai-loading-subtitle">{info.name} Risk Assessment</p>

                {/* Animated pulse line */}
                <div className="ai-pulse-container">
                    <svg className="ai-pulse-svg" viewBox="0 0 300 60" preserveAspectRatio="none">
                        <path
                            className="ai-pulse-line"
                            d="M0,30 L40,30 L50,10 L60,50 L70,20 L80,40 L90,30 L130,30 L140,10 L150,50 L160,20 L170,40 L180,30 L220,30 L230,10 L240,50 L250,20 L260,40 L270,30 L300,30"
                            fill="none"
                            stroke={info.color}
                            strokeWidth="2"
                        />
                    </svg>
                </div>

                {/* Step indicators */}
                <div className="ai-loading-steps">
                    {steps.map((step, i) => (
                        <div
                            key={i}
                            className="ai-loading-step"
                            style={{ animationDelay: `${step.delay}s` }}
                        >
                            <div className="ai-step-dot" style={{ background: info.color }} />
                            <span className="ai-step-label">{step.label}</span>
                        </div>
                    ))}
                </div>

                <p className="ai-loading-note">This usually takes 1-2 seconds</p>
            </div>
        </div>
    )
}

export default LoadingAnalysis
