/**
 * Prediction API — Disease prediction endpoint functions.
 *
 * Wraps the /predict/* and /diseases API calls with proper
 * error handling and response normalization.
 *
 * @module api/predictionApi
 */
import { postJSON, getJSON } from './client'

/**
 * Submit a disease prediction request.
 *
 * @param {string} diseaseType - Disease identifier (heart, diabetes, kidney, depression)
 * @param {Object} formData - Form input data matching the ML model schema
 * @returns {Promise<Object>} Prediction result with success, risk_level, confidence, etc.
 */
export async function predictDisease(diseaseType, formData) {
    return postJSON(`/predict/${diseaseType}`, formData)
}

/**
 * Fetch the list of supported disease models.
 *
 * @returns {Promise<Object>} Object with diseases array
 */
export async function getDiseases() {
    return getJSON('/diseases')
}
