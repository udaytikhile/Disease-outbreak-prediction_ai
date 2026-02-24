/**
 * PredictionLayout — Shared layout wrapper for all prediction form pages.
 *
 * Provides consistent structure: back button, title, form slot, error banner,
 * and result card. Extracted from App.jsx to prevent re-mounting on renders.
 *
 * @module components/prediction/PredictionLayout
 */
import { useNavigate } from 'react-router-dom'
import ResultCard from './ResultCard'

const PredictionLayout = ({ children, title, error, result }) => {
    const nav = useNavigate()
    return (
        <div className="prediction-page">
            <div className="prediction-card-wrapper">
                <button className="prediction-back-btn" onClick={() => nav('/')} aria-label="Back to Home">
                    ← Back to Home
                </button>
                <h2 className="prediction-page-title">{title}</h2>
                {children}

                {error && (
                    <div className="error-banner" role="alert">
                        <span className="error-banner-icon" aria-hidden="true">⚠️</span>
                        <div>
                            <strong>Error</strong>
                            <p>{error}</p>
                        </div>
                    </div>
                )}

                {result && <ResultCard result={result} />}
            </div>
        </div>
    )
}

export default PredictionLayout
