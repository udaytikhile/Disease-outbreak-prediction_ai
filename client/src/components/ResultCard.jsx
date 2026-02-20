const ResultCard = ({ result }) => {
    const isHighRisk = result.prediction === 1
    const cardClass = isHighRisk ? 'result-card danger' : 'result-card success'

    return (
        <div className={cardClass}>
            <div className="result-header">
                <span className="result-icon">{isHighRisk ? '⚠️' : '✅'}</span>
                <div>
                    <h3 className="result-title">
                        {isHighRisk ? 'Risk Detected' : 'Low Risk'}
                    </h3>
                    <p className="result-subtitle">{result.disease}</p>
                </div>
            </div>

            <div className="result-body">
                <p style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
                    <strong>Risk Level:</strong> {result.risk_level}
                </p>

                {result.confidence && (
                    <div className="confidence-bar">
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

                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '8px' }}>
                    <h4 style={{ marginBottom: '0.5rem', fontSize: '1.1rem' }}>💡 Medical Advice</h4>
                    <p style={{ lineHeight: '1.6' }}>{result.advice}</p>
                </div>

                <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(255, 255, 255, 0.15)', borderRadius: '8px', fontSize: '0.9rem' }}>
                    <strong>⚠️ Disclaimer:</strong> This prediction is for educational purposes only.
                    Always consult with a qualified healthcare professional for proper medical diagnosis and treatment.
                </div>
            </div>
        </div>
    )
}

export default ResultCard
