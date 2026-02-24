import { Link } from 'react-router-dom'
import heartDiseaseImg from '../../assets/heart-disease.png'
import diabetesImg from '../../assets/diabetes.png'
import kidneyDiseaseImg from '../../assets/kidney-disease.png'
import depressionImg from '../../assets/depression.png'
import featureAiImg from '../../assets/feature-ai.png'
import featureScreeningImg from '../../assets/feature-screening.png'
import featurePrivacyImg from '../../assets/feature-privacy.png'
import featureReportsImg from '../../assets/feature-reports.png'

const HomePage = ({ onSelectDisease, onViewChecker }) => {
    const diseases = [
        {
            id: 'heart',
            name: 'Heart Disease',
            description: 'Comprehensive cardiovascular risk assessment using clinical biomarkers and patient history data.',
            image: heartDiseaseImg,
            color: '#ef4444',
            params: '13',
            accuracy: '85%',
            patients: '10K+',
        },
        {
            id: 'diabetes',
            name: 'Diabetes',
            description: 'Metabolic disorder screening through lifestyle factors, BMI analysis, and health survey data.',
            image: diabetesImg,
            color: '#3b82f6',
            params: '21',
            accuracy: '75%',
            patients: '70K+',
        },
        {
            id: 'kidney',
            name: 'Kidney Disease',
            description: 'Chronic kidney disease detection using blood tests, urine analysis, and clinical indicators.',
            image: kidneyDiseaseImg,
            color: '#10b981',
            params: '24',
            accuracy: '100%',
            patients: '400+',
        },
        {
            id: 'depression',
            name: 'Depression',
            description: 'Mental health screening based on lifestyle, academic pressure, sleep patterns, and well-being indicators.',
            image: depressionImg,
            color: '#8b5cf6',
            params: '15',
            accuracy: '84%',
            patients: '28K+',
        },
    ]

    const features = [
        {
            icon: '🤖',
            image: featureAiImg,
            title: 'AI-Powered Analysis',
            description: 'Clinical-grade machine learning models trained on validated medical datasets',
            metric: '4 ML Models',
            metricColor: '#dbeafe',
            metricText: '#1e40af',
        },
        {
            icon: '⚡',
            image: featureScreeningImg,
            title: 'Instant Screening',
            description: 'Real-time risk assessment with results delivered in under 2 seconds',
            metric: '<2s Response',
            metricColor: '#dcfce7',
            metricText: '#166534',
        },
        {
            icon: '🔒',
            image: featurePrivacyImg,
            title: 'Data Privacy',
            description: 'Zero-retention policy — your health data is processed locally and never stored',
            metric: 'HIPAA Ready',
            metricColor: '#fae8ff',
            metricText: '#86198f',
        },
        {
            icon: '📊',
            image: featureReportsImg,
            title: 'Clinical Reports',
            description: 'Detailed risk stratification with confidence intervals and actionable insights',
            metric: '98% Uptime',
            metricColor: '#fef3c7',
            metricText: '#92400e',
        },
    ]

    return (
        <div className="clinical-homepage">
            {/* Hero Section */}
            <header className="clinical-hero">
                <div className="clinical-hero-decoration" />
                <div className="clinical-container">
                    <div className="clinical-hero-content">
                        <div className="clinical-trust-badge">
                            <span className="clinical-trust-check">✓</span>
                            Trusted by 7K+ Users Worldwide
                        </div>
                        <h1 className="clinical-headline">
                            <span className="clinical-headline-line1">Clinical-Grade</span>
                            <span className="clinical-headline-line2">AI Health Screening</span>
                        </h1>
                        <p className="clinical-hero-subtitle">
                            Leverage advanced machine learning algorithms for early disease detection.
                            Professional-grade health risk assessments powered by validated clinical data.
                        </p>
                        <div className="clinical-hero-cta">
                            <a href="#diseases" className="clinical-btn-primary">
                                Start Health Screening
                            </a>
                            <button onClick={onViewChecker} className="clinical-btn-secondary">
                                🔍 Symptom Checker
                            </button>
                        </div>
                        <div className="clinical-certifications">
                            <div className="clinical-cert">
                                <span className="clinical-cert-icon">🛡️</span>
                                <span>ISO 27001</span>
                            </div>
                            <div className="clinical-cert">
                                <span className="clinical-cert-icon">✅</span>
                                <span>SOC 2 Type II</span>
                            </div>
                            <div className="clinical-cert">
                                <span className="clinical-cert-icon">🔐</span>
                                <span>GDPR Ready</span>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* How It Works Section */}
            <section className="clinical-how-it-works">
                <div className="clinical-container">
                    <h2 className="clinical-section-title">How It Works</h2>
                    <p className="clinical-section-subtitle">
                        Get your AI-powered health screening in three simple steps
                    </p>
                    <div className="hiw-steps">
                        <div className="hiw-step">
                            <div className="hiw-step-number">1</div>
                            <div className="hiw-step-icon">📝</div>
                            <h3 className="hiw-step-title">Enter Your Data</h3>
                            <p className="hiw-step-desc">Fill in your clinical parameters, vitals, and health indicators in our guided medical forms</p>
                        </div>
                        <div className="hiw-connector">
                            <svg width="40" height="20" viewBox="0 0 40 20" fill="none">
                                <path d="M0 10H35M35 10L28 3M35 10L28 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </div>
                        <div className="hiw-step">
                            <div className="hiw-step-number">2</div>
                            <div className="hiw-step-icon">🤖</div>
                            <h3 className="hiw-step-title">AI Analysis</h3>
                            <p className="hiw-step-desc">Our ML models analyze your data against validated clinical datasets for accurate risk assessment</p>
                        </div>
                        <div className="hiw-connector">
                            <svg width="40" height="20" viewBox="0 0 40 20" fill="none">
                                <path d="M0 10H35M35 10L28 3M35 10L28 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </div>
                        <div className="hiw-step">
                            <div className="hiw-step-number">3</div>
                            <div className="hiw-step-icon">📊</div>
                            <h3 className="hiw-step-title">Get Results</h3>
                            <p className="hiw-step-desc">Receive detailed risk assessment with confidence scores, SHAP explanations, and personalized advice</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="clinical-features-section">
                <div className="clinical-container">
                    <h2 className="clinical-section-title">Why Choose Medixa AI?</h2>
                    <div className="clinical-features-grid">
                        {features.map((feature, index) => (
                            <div key={index} className="clinical-feature-card" style={{ animationDelay: `${index * 0.1}s` }}>
                                <div className="clinical-feature-img-wrap">
                                    <img src={feature.image} alt={feature.title} className="clinical-feature-img" />
                                    <div className="clinical-feature-img-overlay" />
                                    <span className="clinical-feature-icon-badge">{feature.icon}</span>
                                </div>
                                <div className="clinical-feature-body">
                                    <h3 className="clinical-feature-title">{feature.title}</h3>
                                    <p className="clinical-feature-desc">{feature.description}</p>
                                    <span
                                        className="clinical-feature-metric"
                                        style={{ background: feature.metricColor, color: feature.metricText }}
                                    >
                                        {feature.metric}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Disease Assessment Cards */}
            <section id="diseases" className="clinical-diseases-section">
                <div className="clinical-container">
                    <div className="clinical-section-header">
                        <h2 className="clinical-section-title">Disease Assessments</h2>
                        <p className="clinical-section-subtitle">
                            Select a screening module to begin your AI-powered health risk evaluation
                        </p>
                    </div>
                    <div className="clinical-disease-grid">
                        {diseases.map((disease) => (
                            <button
                                key={disease.id}
                                className="clinical-disease-card"
                                onClick={() => onSelectDisease(disease.id)}
                                style={{ '--card-color': disease.color }}
                                aria-label={`Start ${disease.name} screening`}
                            >
                                <div className="clinical-disease-accent" />
                                <div className="clinical-disease-body">
                                    {disease.image ? (
                                        <div className="clinical-disease-img-wrap">
                                            <img src={disease.image} alt={disease.name} className="clinical-disease-img" />
                                        </div>
                                    ) : (
                                        <div className="clinical-disease-icon">{disease.icon}</div>
                                    )}
                                    <h3 className="clinical-disease-name">{disease.name}</h3>
                                    <p className="clinical-disease-desc">{disease.description}</p>
                                </div>
                                <div className="clinical-disease-metrics">
                                    <div className="clinical-metric">
                                        <div className="clinical-metric-value">{disease.params}</div>
                                        <div className="clinical-metric-label">Parameters</div>
                                    </div>
                                    <div className="clinical-metric">
                                        <div className="clinical-metric-value">{disease.accuracy}</div>
                                        <div className="clinical-metric-label">Accuracy</div>
                                    </div>
                                    <div className="clinical-metric">
                                        <div className="clinical-metric-value">{disease.patients}</div>
                                        <div className="clinical-metric-label">Patients</div>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            </section>

            {/* Disclaimer Section */}
            <section className="clinical-disclaimer-section">
                <div className="clinical-container">
                    <div className="clinical-disclaimer-card">
                        <div className="clinical-disclaimer-icon">⚠️</div>
                        <div className="clinical-disclaimer-content">
                            <h3 className="clinical-disclaimer-title">Important Medical Disclaimer</h3>
                            <p className="clinical-disclaimer-text">
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
            <footer className="clinical-footer">
                <div className="clinical-container">
                    <div className="clinical-footer-grid">
                        <div className="clinical-footer-brand">
                            <img src="/logo.png" alt="Medixa AI" className="footer-logo-img" style={{ height: '40px', width: 'auto', objectFit: 'contain' }} />
                            <h3>Medixa AI</h3>
                            <p>AI-Powered Clinical Health Screening Platform. Empowering early detection through intelligent risk assessment.</p>
                        </div>
                        <div className="clinical-footer-col">
                            <h4>Product</h4>
                            <a href="#features">Features</a>
                            <a href="#diseases">Assessments</a>
                            <Link to="/checker">Symptom Check</Link>
                        </div>
                        <div className="clinical-footer-col">
                            <h4>Resources</h4>
                            <Link to="/dashboard">Dashboard</Link>
                            <Link to="/history">History</Link>
                            <Link to="/tips">Health Info</Link>
                        </div>
                        <div className="clinical-footer-col">
                            <h4>Connect</h4>
                            <a href="mailto:udaytikhile@gmail.com" className="footer-social-link">
                                <span className="footer-social-icon">
                                    <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z" /></svg>
                                </span>
                                udaytikhile@gmail.com
                            </a>
                            <a href="https://github.com/udaytikhile" target="_blank" rel="noopener noreferrer" className="footer-social-link">
                                <span className="footer-social-icon">
                                    <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" /></svg>
                                </span>
                                GitHub
                            </a>
                            <a href="https://www.linkedin.com/in/uday-tikhile-b63159374" target="_blank" rel="noopener noreferrer" className="footer-social-link">
                                <span className="footer-social-icon linkedin">
                                    <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" /></svg>
                                </span>
                                LinkedIn
                            </a>
                            <a href="https://www.instagram.com/uday_tikhile_21?igsh=ZmNmaXRlZjF2aXhl" target="_blank" rel="noopener noreferrer" className="footer-social-link">
                                <span className="footer-social-icon instagram">
                                    <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z" /></svg>
                                </span>
                                Instagram
                            </a>
                        </div>
                    </div>
                    <div className="clinical-footer-bottom">
                        <p>© 2026 Medixa AI. Made with ❤️ for better health awareness.</p>
                        <p>Developed by Uday Tikhile</p>
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default HomePage
