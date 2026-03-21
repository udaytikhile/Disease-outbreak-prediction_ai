// IMPROVED: Added per-toast duration styling hook to sync auto-dismiss progress animation with each toast's lifetime.
import { useState, useEffect, useCallback, useRef } from 'react'
import { toastEmitter } from '../../utils/events'

let toastIdCounter = 0

const ToastContainer = () => {
    const [toasts, setToasts] = useState([])
    const timeoutRefs = useRef(new Map())

    const addToast = useCallback(({ message, type, duration }) => {
        const id = ++toastIdCounter
        const safeDuration = Number(duration) > 0 ? Number(duration) : 4000
        setToasts(prev => [...prev, { id, message, type, exiting: false, duration: safeDuration }])

        const exitTimeout = setTimeout(() => {
            setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t))
            const removeTimeout = setTimeout(() => {
                setToasts(prev => prev.filter(t => t.id !== id))
                timeoutRefs.current.delete(id)
            }, 400)
            timeoutRefs.current.set(`${id}-remove`, removeTimeout)
        }, safeDuration)
        timeoutRefs.current.set(id, exitTimeout)
    }, [])

    useEffect(() => {
        const handler = (e) => addToast(e.detail)
        toastEmitter.addEventListener('toast', handler)
        const timeouts = timeoutRefs.current
        return () => {
            toastEmitter.removeEventListener('toast', handler)
            // Cleanup all pending timeouts on unmount
            timeouts.forEach(timeout => clearTimeout(timeout))
            timeouts.clear()
        }
    }, [addToast])

    const removeToast = (id) => {
        // Clear any pending auto-remove timeouts for this toast
        if (timeoutRefs.current.has(id)) {
            clearTimeout(timeoutRefs.current.get(id))
            timeoutRefs.current.delete(id)
        }
        setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t))
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id))
        }, 400)
    }

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    }

    return (
        <div className="toast-container" role="status">
            {toasts.map(toast => (
                <div
                    key={toast.id}
                    className={`toast toast-${toast.type} ${toast.exiting ? 'toast-exit' : 'toast-enter'}`}
                    role={toast.type === 'error' ? 'alert' : 'status'}
                    style={{ '--toast-duration': `${toast.duration || 4000}ms` }}
                >
                    <span className="toast-icon" aria-hidden="true">{icons[toast.type]}</span>
                    <span className="toast-message">{toast.message}</span>
                    <button className="toast-close" onClick={() => removeToast(toast.id)} aria-label="Dismiss notification">×</button>
                </div>
            ))}
        </div>
    )
}

export default ToastContainer
