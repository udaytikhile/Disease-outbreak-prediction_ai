/**
 * PredictionContext — Centralized prediction state management.
 *
 * Extracts prediction state (loading, result, error) and the handlePrediction
 * logic from App.jsx into a React Context provider. This eliminates prop
 * drilling and makes prediction state accessible from any component.
 *
 * Usage:
 *   // Wrap app in provider:
 *   <PredictionProvider><App /></PredictionProvider>
 *
 *   // Consume in any component:
 *   const { result, loading, error, handlePrediction, handleReset } = usePrediction()
 *
 * @module context/PredictionContext
 */
import { createContext, useContext, useState, useCallback, useMemo } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { predictDisease } from '../api/predictionApi'
import { usePredictionHistory } from '../hooks/usePredictionHistory'
import { showToast } from '../components/common/Toast'

const PredictionContext = createContext(null)

/**
 * Provider component that manages all prediction-related state.
 * Wraps the app to provide prediction context to all children.
 */
export function PredictionProvider({ children }) {
    const [loading, setLoading] = useState(false)
    const [loadingDisease, setLoadingDisease] = useState(null)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const { addPrediction } = usePredictionHistory()
    const navigate = useNavigate()
    const location = useLocation()

    // Clear result/error on navigation
    useEffect(() => {
        setResult(null)
        setError(null)
    }, [location.pathname])

    /**
     * Submit a prediction request for a disease type.
     * Handles loading state, API call, success/error toasts, and history logging.
     */
    const handlePrediction = useCallback(async (diseaseType, formData) => {
        setLoading(true)
        setLoadingDisease(diseaseType)
        setResult(null)
        setError(null)

        try {
            const data = await predictDisease(diseaseType, formData)

            if (data.success) {
                setResult(data)
                addPrediction({
                    disease: data.disease,
                    risk_level: data.risk_level,
                    confidence: data.confidence,
                    prediction: data.prediction,
                    advice: data.advice,
                })
                showToast(
                    data.risk_level === 'High'
                        ? `⚠️ High risk detected for ${data.disease}`
                        : `✅ Low risk for ${data.disease}`,
                    data.risk_level === 'High' ? 'warning' : 'success'
                )
            } else {
                setError(data.error || 'An error occurred during prediction')
                showToast(data.error || 'Prediction failed', 'error')
            }
        } catch (err) {
            if (err.name === 'AbortError') {
                setError('Request timed out. The server may be overloaded — please try again.')
                showToast('Request timed out. Try again.', 'error')
            } else {
                setError('Connection error: Make sure the backend server is running.')
                showToast('Connection error. Is the backend running?', 'error')
            }
            console.error('API Error:', err)
        } finally {
            setLoading(false)
            setLoadingDisease(null)
        }
    }, [addPrediction])

    /** Reset prediction state and navigate home. */
    const handleReset = useCallback(() => {
        setResult(null)
        setError(null)
        navigate('/')
    }, [navigate])

    const value = useMemo(() => ({
        loading,
        loadingDisease,
        result,
        error,
        handlePrediction,
        handleReset,
    }), [loading, loadingDisease, result, error, handlePrediction, handleReset])

    return (
        <PredictionContext.Provider value={value}>
            {children}
        </PredictionContext.Provider>
    )
}

/**
 * Hook to access prediction state and actions.
 *
 * @returns {{ loading, loadingDisease, result, error, handlePrediction, handleReset }}
 * @throws {Error} If used outside PredictionProvider
 */
export function usePrediction() {
    const context = useContext(PredictionContext)
    if (!context) {
        throw new Error('usePrediction must be used within a PredictionProvider')
    }
    return context
}
