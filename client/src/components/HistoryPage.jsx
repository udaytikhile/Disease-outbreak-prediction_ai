import { usePredictionHistory } from '../hooks/usePredictionHistory'

const HistoryPage = ({ onClose }) => {
  const { history, deletePrediction, clearHistory, getStatistics, exportAsCSV, exportAsJSON } = usePredictionHistory()
  const stats = getStatistics()

  return (
    <div className="history-container">
      <div className="history-header">
        <div>
          <h2 className="history-title">📊 Prediction History & Analytics</h2>
          <p className="history-subtitle">View your past predictions and insights</p>
        </div>
        <button className="btn btn-secondary" onClick={onClose} style={{ width: 'auto' }}>
          ← Back to Home
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid-history">
        <div className="stat-card">
          <div className="stat-number">{stats.totalPredictions}</div>
          <div className="stat-label">Total Predictions</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.avgConfidence.toFixed(1)}%</div>
          <div className="stat-label">Average Confidence</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.riskDistribution.high}</div>
          <div className="stat-label">High Risk</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.riskDistribution.low}</div>
          <div className="stat-label">Low Risk</div>
        </div>
      </div>

      {/* Disease Breakdown */}
      {Object.keys(stats.byDisease).length > 0 && (
        <div className="disease-stats">
          <h3>📋 Predictions by Disease</h3>
          <div className="disease-list">
            {Object.entries(stats.byDisease).map(([disease, count]) => (
              <div key={disease} className="disease-item">
                <span className="disease-name">{disease}</span>
                <div className="disease-bar">
                  <div
                    className="disease-bar-fill"
                    style={{ width: `${(count / stats.totalPredictions) * 100}%` }}
                  ></div>
                </div>
                <span className="disease-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Export Options */}
      <div className="export-section">
        <h3>💾 Export Data</h3>
        <div className="export-buttons">
          <button className="btn btn-primary" onClick={exportAsCSV} disabled={stats.totalPredictions === 0}>
            📥 Export as CSV
          </button>
          <button className="btn btn-primary" onClick={exportAsJSON} disabled={stats.totalPredictions === 0}>
            📥 Export as JSON
          </button>
        </div>
      </div>

      {/* History List */}
      <div className="history-list-section">
        <div className="history-list-header">
          <h3>📝 Recent Predictions</h3>
          {history.length > 0 && (
            <button
              className="btn btn-secondary"
              onClick={() => {
                if (window.confirm('Are you sure? This will clear all prediction history.')) {
                  clearHistory()
                }
              }}
              style={{ width: 'auto' }}
            >
              🗑️ Clear All
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <div className="empty-state">
            <p>No predictions yet. Make a prediction to get started!</p>
          </div>
        ) : (
          <div className="predictions-cards">
            {history.map(prediction => (
              <div key={prediction.id} className="prediction-card">
                <div className="prediction-header">
                  <div className="prediction-info">
                    <h4>{prediction.disease}</h4>
                    <p className="prediction-date">
                      {new Date(prediction.timestamp).toLocaleDateString()} at{' '}
                      {new Date(prediction.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                  <div className="prediction-badge" style={{
                    background: prediction.risk_level === 'High' ? '#f45c43' : '#38ef7d',
                    color: 'white',
                    padding: '0.5rem 1rem',
                    borderRadius: '20px',
                    fontSize: '0.9rem',
                    fontWeight: '600'
                  }}>
                    {prediction.risk_level === 'High' ? '⚠️ High Risk' : '✅ Low Risk'}
                  </div>
                </div>

                <div className="prediction-body">
                  {prediction.confidence && (
                    <div className="confidence-bar-small">
                      <p>Confidence: {prediction.confidence.toFixed(1)}%</p>
                      <div style={{
                        height: '8px',
                        background: 'rgba(0, 0, 0, 0.1)',
                        borderRadius: '4px',
                        marginTop: '0.5rem',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${prediction.confidence}%`,
                          background: prediction.risk_level === 'High' ? '#f45c43' : '#38ef7d',
                          borderRadius: '4px'
                        }}></div>
                      </div>
                    </div>
                  )}

                  <p className="prediction-advice" style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666', fontStyle: 'italic' }}>
                    {prediction.advice}
                  </p>
                </div>

                <div className="prediction-footer">
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      if (window.confirm('Delete this prediction?')) {
                        deletePrediction(prediction.id)
                      }
                    }}
                    style={{ width: 'auto', fontSize: '0.9rem', padding: '0.5rem 1rem' }}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default HistoryPage
