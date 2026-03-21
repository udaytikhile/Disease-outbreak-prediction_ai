// IMPROVED: Added simple list virtualization for large histories and staggered card entrance motion.
import { usePredictionHistory } from '../hooks/usePredictionHistory'
import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'

const VIRTUAL_ROW_HEIGHT = 248
const VIRTUAL_WINDOW_HEIGHT = 760

const HistoryPage = ({ onClose }) => {
  const { history, deletePrediction, clearHistory, statistics, exportAsCSV, exportAsJSON } = usePredictionHistory()
  const stats = statistics
  const [scrollTop, setScrollTop] = useState(0)
  const shouldVirtualize = history.length > 50

  const { startIndex, visibleItems, offsetY, totalHeight } = useMemo(() => {
    if (!shouldVirtualize) {
      return { startIndex: 0, endIndex: history.length, visibleItems: history, offsetY: 0, totalHeight: history.length * VIRTUAL_ROW_HEIGHT }
    }
    const start = Math.max(0, Math.floor(scrollTop / VIRTUAL_ROW_HEIGHT) - 4)
    const end = Math.min(history.length, Math.ceil((scrollTop + VIRTUAL_WINDOW_HEIGHT) / VIRTUAL_ROW_HEIGHT) + 4)
    return {
      startIndex: start,
      endIndex: end,
      visibleItems: history.slice(start, end),
      offsetY: start * VIRTUAL_ROW_HEIGHT,
      totalHeight: history.length * VIRTUAL_ROW_HEIGHT,
    }
  }, [history, scrollTop, shouldVirtualize])

  return (
    <div className="history-container">
      <div className="history-header">
        <div>
          <h1 className="history-title"><span aria-hidden="true">📋</span> Prediction History & Analytics</h1>
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
          <div className="predictions-cards" style={shouldVirtualize ? { maxHeight: `${VIRTUAL_WINDOW_HEIGHT}px`, overflowY: 'auto' } : undefined} onScroll={shouldVirtualize ? (e) => setScrollTop(e.currentTarget.scrollTop) : undefined}>
            <div style={shouldVirtualize ? { height: `${totalHeight}px`, position: 'relative' } : undefined}>
            <div style={shouldVirtualize ? { transform: `translateY(${offsetY}px)` } : undefined}>
            {visibleItems.map((prediction, index) => (
              <motion.div key={prediction.id} className="prediction-card" style={{ '--i': startIndex + index }} initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.04 }}>
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
                  <div className={`prediction-badge ${prediction.risk_level === 'High' ? 'prediction-badge-high' : 'prediction-badge-low'}`}>
                    {prediction.risk_level === 'High' ? '⚠️ High Risk' : '✅ Low Risk'}
                  </div>
                </div>

                <div className="prediction-body">
                  {prediction.confidence && (
                    <div className="confidence-bar-small">
                      <p>Confidence: {prediction.confidence.toFixed(1)}%</p>
                      <div className="confidence-bar-track">
                        <div
                          className={`confidence-bar-fill ${prediction.risk_level === 'High' ? 'confidence-fill-high' : 'confidence-fill-low'}`}
                          style={{ width: `${prediction.confidence}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  <p className="prediction-advice">
                    {prediction.advice}
                  </p>
                </div>

                <div className="prediction-footer">
                  <button
                    className="btn btn-secondary prediction-delete-btn"
                    onClick={() => {
                      if (window.confirm('Delete this prediction?')) {
                        deletePrediction(prediction.id)
                      }
                    }}
                    aria-label={`Delete ${prediction.disease} prediction from ${new Date(prediction.timestamp).toLocaleDateString()}`}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </motion.div>
            ))}
            </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default HistoryPage
