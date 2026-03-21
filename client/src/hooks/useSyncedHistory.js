// IMPROVED: Centralized history synchronization between localStorage and in-memory state so history consumers share a single reconciliation path.
import { useCallback, useEffect, useRef, useState } from 'react'

export const HISTORY_STORAGE_KEY = 'prediction_history'
const SYNC_EVENT = 'prediction_history_updated'

export function useSyncedHistory() {
  const [history, setHistory] = useState(() => {
    try {
      const saved = localStorage.getItem(HISTORY_STORAGE_KEY)
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })

  const isSelfUpdate = useRef(false)

  useEffect(() => {
    const sync = () => {
      if (isSelfUpdate.current) {
        isSelfUpdate.current = false
        return
      }
      try {
        const saved = localStorage.getItem(HISTORY_STORAGE_KEY)
        setHistory(saved ? JSON.parse(saved) : [])
      } catch {
        setHistory([])
      }
    }

    const onStorage = (event) => {
      if (event.key === HISTORY_STORAGE_KEY) sync()
    }

    window.addEventListener(SYNC_EVENT, sync)
    window.addEventListener('storage', onStorage)
    return () => {
      window.removeEventListener(SYNC_EVENT, sync)
      window.removeEventListener('storage', onStorage)
    }
  }, [])

  const persistHistory = useCallback((nextHistory) => {
    isSelfUpdate.current = true
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(nextHistory))
    window.dispatchEvent(new Event(SYNC_EVENT))
  }, [])

  const clearSyncedHistory = useCallback(() => {
    setHistory([])
    localStorage.removeItem(HISTORY_STORAGE_KEY)
    window.dispatchEvent(new Event(SYNC_EVENT))
  }, [])

  return { history, setHistory, persistHistory, clearSyncedHistory }
}
