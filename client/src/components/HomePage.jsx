const HomePage = ({ onSelectDisease, onViewHistory, onViewProfile, onViewTips, onViewDashboard, onViewChecker, userName }) => {
    const diseases = [
        {
            id: 'heart',
            name: 'Heart Disease',
            description: 'Predict cardiovascular disease risk based on clinical parameters',
            icon: '❤️',
            color: '#eb3349',
            stats: '13 Parameters',
            accuracy: '~79%',
        },
        {
            id: 'diabetes',
            name: 'Diabetes',
            description: 'Predict diabetes risk using health metrics and lifestyle factors',
            icon: '🩺',
            color: '#667eea',
            stats: '8 Parameters',
            accuracy: '~78%',
        },
        {
            id: 'parkinsons',
            name: "Parkinson's Disease",
            description: 'Predict Parkinson\'s disease using advanced voice measurements',
            icon: '🧠',
            color: '#f093fb',
            stats: '22 Parameters',
            accuracy: '~87%',
        },
    ]

    const features = [
        {
            icon: '🤖',
            title: 'AI-Powered',
            description: 'Advanced machine learning algorithms for accurate predictions',
        },
        {
            icon: '⚡',
            title: 'Instant Results',
            description: 'Get your health risk assessment in seconds',
        },
        {
            icon: '🔒',
            title: 'Secure & Private',
            description: 'Your data is processed locally and never stored on servers',
        },
        {
            icon: '📊',
            title: 'Detailed Analysis',
            description: 'Comprehensive reports with confidence scores',
        },
    ]

    const stats = [
        { value: '3', label: 'Disease Models', icon: '🧬' },
        { value: '~81%', label: 'Avg Accuracy', icon: '🎯' },
        { value: '43', label: 'Health Metrics', icon: '📈' },
        { value: '100%', label: 'Free to Use', icon: '✨' },
    ]

    const quickActions = [
        { icon: '🔍', label: 'Symptom Check', onClick: onViewChecker, color: '#6366f1' },
        { icon: '📊', label: 'Dashboard', onClick: onViewDashboard, color: '#22c55e' },
        { icon: '📋', label: 'History', onClick: onViewHistory, color: '#f59e0b' },
        { icon: '🏥', label: 'Health Info', onClick: onViewTips, color: '#ef4444' },
        { icon: '👤', label: 'My Profile', onClick: onViewProfile, color: '#a855f7' },
    ]

    return (
        <div className="homepage">
            {/* Hero Section */}
            <header className="hero-section">
                <div className="container">
                    <div className="hero-content">
                        <div className="logo-large">🧫</div>
                        <h1 className="hero-title">
                            {userName ? `Welcome back, ${userName}!` : 'Checkup Buddy'}
                        </h1>
                        <p className="hero-subtitle">AI-Powered Health Prediction System</p>
                        <p className="hero-description">
                            Leverage cutting-edge machine learning to assess your health risks.
                            Early detection can save lives. Get instant, AI-powered health predictions.
                        </p>
                        <div className="hero-cta">
                            <a href="#diseases" className="btn btn-primary btn-large">
                                Start Health Check 🚀
                            </a>
                            <button onClick={onViewChecker} className="btn btn-secondary btn-large" style={{ cursor: 'pointer' }}>
                                🔍 Symptom Check
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Quick Actions Bar */}
            <section className="quick-actions-section">
                <div className="container">
                    <div className="quick-actions-grid">
                        {quickActions.map((action, i) => (
                            <button
                                key={i}
                                className="quick-action-btn"
                                onClick={action.onClick}
                                style={{ '--action-color': action.color, animationDelay: `${i * 0.08}s` }}
                            >
                                <span className="qa-icon">{action.icon}</span>
                                <span className="qa-label">{action.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="stats-section">
                <div className="container">
                    <div className="stats-grid">
                        {stats.map((stat, index) => (
                            <div key={index} className="stat-card">
                                <div className="stat-icon">{stat.icon}</div>
                                <div className="stat-value">{stat.value}</div>
                                <div className="stat-label">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="features-section">
                <div className="container">
                    <div className="section-header">
                        <h2 className="section-title">Why Choose Checkup Buddy?</h2>
                        <p className="section-subtitle">
                            Advanced technology meets healthcare accessibility
                        </p>
                    </div>
                    <div className="features-grid">
                        {features.map((feature, index) => (
                            <div key={index} className="feature-card">
                                <div className="feature-icon">{feature.icon}</div>
                                <h3 className="feature-title">{feature.title}</h3>
                                <p className="feature-description">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Diseases Section */}
            <section id="diseases" className="diseases-section">
                <div className="container">
                    <div className="section-header">
                        <h2 className="section-title">Select a Health Assessment</h2>
                        <p className="section-subtitle">
                            Choose the disease you want to predict and get instant AI-powered results
                        </p>
                    </div>
                    <div className="disease-grid-home">
                        {diseases.map((disease) => (
                            <div
                                key={disease.id}
                                className="disease-card-home"
                                onClick={() => onSelectDisease(disease.id)}
                                style={{ '--disease-color': disease.color }}
                            >
                                <div className="disease-card-header">
                                    <span className="disease-icon-large">{disease.icon}</span>
                                </div>
                                <div className="disease-card-body">
                                    <h3 className="disease-name">{disease.name}</h3>
                                    <p className="disease-description">{disease.description}</p>
                                    <div className="disease-meta">
                                        <span className="disease-stat">
                                            <span className="meta-icon">📊</span>
                                            {disease.stats}
                                        </span>
                                        <span className="disease-stat">
                                            <span className="meta-icon">🎯</span>
                                            {disease.accuracy} Accuracy
                                        </span>
                                    </div>
                                </div>
                                <div className="disease-card-footer">
                                    <button className="btn-disease">
                                        Start Assessment →
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Disclaimer Section */}
            <section className="disclaimer-section">
                <div className="container">
                    <div className="disclaimer-card">
                        <div className="disclaimer-icon">⚠️</div>
                        <div className="disclaimer-content">
                            <h3 className="disclaimer-title">Important Medical Disclaimer</h3>
                            <p className="disclaimer-text">
                                This tool is designed for <strong>educational and preventive awareness purposes only</strong>.
                                It is not a substitute for professional medical advice, diagnosis, or treatment.
                                Always seek the advice of your physician or other qualified health provider with any
                                questions you may have regarding a medical condition.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="footer-section">
                <div className="container">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <div className="footer-logo">🧫</div>
                            <h3>Checkup Buddy</h3>
                            <p>AI-Powered Health Prediction</p>
                        </div>
                        <div className="footer-links">
                            <div className="footer-column">
                                <h4>Product</h4>
                                <a href="#features">Features</a>
                                <a href="#diseases">Assessments</a>
                                <a href="#" onClick={(e) => { e.preventDefault(); onViewChecker?.() }}>Symptom Check</a>
                            </div>
                            <div className="footer-column">
                                <h4>Tools</h4>
                                <a href="#" onClick={(e) => { e.preventDefault(); onViewDashboard?.() }}>Dashboard</a>
                                <a href="#" onClick={(e) => { e.preventDefault(); onViewHistory?.() }}>History</a>
                                <a href="#" onClick={(e) => { e.preventDefault(); onViewTips?.() }}>Health Info</a>
                            </div>
                            <div className="footer-column">
                                <h4>Contact</h4>
                                <a href="mailto:udaytikhile@gmail.com">Email Us</a>
                                <a href="#github">GitHub</a>
                                <a href="#linkedin">LinkedIn</a>
                            </div>
                        </div>
                    </div>
                    <div className="footer-bottom">
                        <p>© 2026 Checkup Buddy. Made with ❤️ for better health awareness.</p>
                        <p>Developed by Uday Tikhile</p>
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default HomePage
