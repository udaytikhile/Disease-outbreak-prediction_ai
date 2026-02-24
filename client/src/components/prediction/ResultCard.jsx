import ReportButton from '../common/ReportButton'

const ResultCard = ({ result }) => {
    const isHighRisk = result.risk_level === 'High'
    const cardClass = isHighRisk ? 'result-card danger' : 'result-card success'

    return (
        <div className={cardClass} role="region" aria-label={`${result.disease} prediction result`}>
            <div className="result-header">
                <span className="result-icon" aria-hidden="true">{isHighRisk ? '⚠️' : '✅'}</span>
                <div>
                    <h3 className="result-title">
                        {isHighRisk ? 'Risk Detected' : 'Low Risk'}
                    </h3>
                    <p className="result-subtitle">{result.disease}</p>
                </div>
            </div>

            <div className="result-body">
                <p style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
                    <strong>Risk Level:</strong> <span aria-live="polite">{result.risk_level}</span>
                </p>

                {result.confidence && (
                    <div className="confidence-bar" role="progressbar"
                        aria-valuenow={result.confidence.toFixed(1)}
                        aria-valuemin="0" aria-valuemax="100"
                        aria-label={`Confidence: ${result.confidence.toFixed(1)}%`}>
                        <div className="confidence-label">
                            <span>Confidence</span>
                            <span>{result.confidence.toFixed(1)}%</span>
                        </div>
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{ width: `${result.confidence}%` }}
                            ></div>
                        </div>
                    </div>
                )}

                {/* SHAP Contributions UI */}
                {result.shap_contributions && result.shap_contributions.length > 0 && (
                    <div className="shap-container" style={{ marginTop: '1.5rem' }}>
                        <h4 style={{ marginBottom: '0.75rem', fontSize: '1.05rem' }}>📊 What drove this result?</h4>
                        <div className="shap-bars">
                            {result.shap_contributions.map((item, idx) => (
                                <div key={idx} className="shap-item">
                                    <div className="shap-label">
                                        <span className="shap-feature">{item.feature}</span>
                                        <span className={`shap-direction ${item.direction}`}>
                                            {item.direction === 'risk' ? '↑ Risk' : '↓ Protective'} ({item.pct}%)
                                        </span>
                                    </div>
                                    <div className="shap-track">
                                        <div
                                            className={`shap-fill ${item.direction}`}
                                            style={{ width: `${item.pct}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="result-advice-box">
                    <h4>💡 Medical Advice</h4>
                    <p>{result.advice}</p>
                </div>

                <ReportButton result={result} />

                <div className="result-disclaimer">
                    <strong>⚠️ Disclaimer:</strong> This prediction is for educational purposes only.
                    Always consult with a qualified healthcare professional for proper medical diagnosis and treatment.
                </div>
            </div>
        </div>
    )
}

export default ResultCard
