import { useState, useEffect, useCallback, useRef, useMemo } from 'react'

const STORAGE_KEY = 'prediction_history'
const MAX_HISTORY = 100 // Store max 100 predictions

// Custom event name for cross-component sync
const SYNC_EVENT = 'prediction_history_updated'

export const usePredictionHistory = () => {
  const [history, setHistory] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? JSON.parse(saved) : []
    } catch (e) {
      console.error('Failed to load history:', e)
      return []
    }
  })

  // Ref to skip self-triggered sync events (Bug #6 fix)
  const isSelfUpdate = useRef(false)

  // Listen for changes from other component instances using this hook
  useEffect(() => {
    const handleSync = () => {
      if (isSelfUpdate.current) {
        isSelfUpdate.current = false
        return
      }
      try {
        const saved = localStorage.getItem(STORAGE_KEY)
        setHistory(saved ? JSON.parse(saved) : [])
      } catch (e) {
        console.error('Failed to sync history:', e)
      }
    }

    const handleStorageEvent = (e) => {
      if (e.key === STORAGE_KEY) handleSync()
    }

    window.addEventListener(SYNC_EVENT, handleSync)
    // Also sync on storage changes (e.g. from other tabs)
    window.addEventListener('storage', handleStorageEvent)

    return () => {
      window.removeEventListener(SYNC_EVENT, handleSync)
      window.removeEventListener('storage', handleStorageEvent)
    }
  }, [])

  // Helper to persist and broadcast changes
  const persistAndBroadcast = useCallback((updated) => {
    isSelfUpdate.current = true
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
    // Dispatch custom event so other hook instances sync
    window.dispatchEvent(new Event(SYNC_EVENT))
  }, [])

  // Save prediction to history
  const addPrediction = useCallback((prediction) => {
    const newPrediction = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      ...prediction
    }

    setHistory(prev => {
      const updated = [newPrediction, ...prev].slice(0, MAX_HISTORY)
      persistAndBroadcast(updated)
      return updated
    })
  }, [persistAndBroadcast])

  // Delete prediction from history
  const deletePrediction = useCallback((id) => {
    setHistory(prev => {
      const updated = prev.filter(p => p.id !== id)
      persistAndBroadcast(updated)
      return updated
    })
  }, [persistAndBroadcast])

  // Clear all history
  const clearHistory = useCallback(() => {
    setHistory([])
    localStorage.removeItem(STORAGE_KEY)
    window.dispatchEvent(new Event(SYNC_EVENT))
  }, [])

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
