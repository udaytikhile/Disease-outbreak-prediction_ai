// IMPROVED: Delegates persistence/reconciliation to useSyncedHistory and documents localStorage-first architecture.
import { useCallback, useMemo } from 'react'
import { useSyncedHistory } from './useSyncedHistory'

/**
 * IMPROVED: History architecture now uses a unified sync layer.
 * localStorage remains the immediate source for instant UX/offline continuity,
 * while API-backed history can later hydrate/merge through this same hook
 * without changing downstream UI consumers.
 */
const MAX_HISTORY = 100 // Store max 100 predictions

export const usePredictionHistory = () => {
  const { history, setHistory, persistHistory, clearSyncedHistory } = useSyncedHistory()

  // Save prediction to history
  const addPrediction = useCallback((prediction) => {
    const newPrediction = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      ...prediction
    }

    setHistory(prev => {
      const updated = [newPrediction, ...prev].slice(0, MAX_HISTORY)
      persistHistory(updated)
      return updated
    })
  }, [persistHistory, setHistory])

  // Delete prediction from history
  const deletePrediction = useCallback((id) => {
    setHistory(prev => {
      const updated = prev.filter(p => p.id !== id)
      persistHistory(updated)
      return updated
    })
  }, [persistHistory, setHistory])

  // Clear all history
  const clearHistory = useCallback(() => {
    clearSyncedHistory()
  }, [clearSyncedHistory])

  // Pre-computed statistics (referentially stable when history hasn't changed)
  const statistics = useMemo(() => {
    const stats = {
      totalPredictions: history.length,
      byDisease: {},
      riskDistribution: { high: 0, low: 0 },
      avgConfidence: 0
    }

    if (history.length === 0) return stats

    let totalConfidence = 0
    let validConfidenceCount = 0
    for (const pred of history) {
      stats.byDisease[pred.disease] = (stats.byDisease[pred.disease] || 0) + 1

      const riskKey = (pred.risk_level || '').toLowerCase()
      if (riskKey === 'high') stats.riskDistribution.high += 1
      else if (riskKey === 'low') stats.riskDistribution.low += 1

      if (pred.confidence != null) {
        totalConfidence += pred.confidence
        validConfidenceCount += 1
      }
    }

    stats.avgConfidence = validConfidenceCount > 0 ? totalConfidence / validConfidenceCount : 0

    return stats
  }, [history])

  // Export as CSV
  const exportAsCSV = useCallback(() => {
    if (history.length === 0) {
      alert('No predictions to export')
      return
    }

    const headers = ['Date', 'Disease', 'Risk Level', 'Confidence (%)', 'Prediction']
    const rows = history.map(p => [
      new Date(p.timestamp).toLocaleString(),
      p.disease,
      p.risk_level,
      p.confidence != null ? p.confidence.toFixed(2) : 'N/A',
      p.prediction === 1 ? 'Yes' : 'No'
    ])

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell =>
        `"${String(cell).replace(/"/g, '""')}"`
      ).join(','))
    ].join('\n')

    downloadFile(csv, 'predictions.csv', 'text/csv')
  }, [history])

  // Export as JSON
  const exportAsJSON = useCallback(() => {
    if (history.length === 0) {
      alert('No predictions to export')
      return
    }

    const data = {
      exportDate: new Date().toISOString(),
      totalPredictions: history.length,
      statistics,
      predictions: history.map(p => ({
        date: p.timestamp,
        disease: p.disease,
        riskLevel: p.risk_level,
        confidence: p.confidence,
        prediction: p.prediction === 1 ? 'Positive' : 'Negative',
        advice: p.advice
      }))
    }

    downloadFile(JSON.stringify(data, null, 2), 'predictions.json', 'application/json')
  }, [history, statistics])

  return {
    history,
    addPrediction,
    deletePrediction,
    clearHistory,
    statistics,
    exportAsCSV,
    exportAsJSON
  }
}

// Helper function to download files (module-scoped, not inside hook)
function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
