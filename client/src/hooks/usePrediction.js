import { useContext } from 'react'
import { PredictionContext } from '../context/PredictionContext'

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
