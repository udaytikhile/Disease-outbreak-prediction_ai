/**
 * HTTP Client — Centralized fetch wrapper with timeout and error handling.
 *
 * All API calls go through this module, ensuring consistent:
 *   - Request timeout (15s default)
 *   - Base URL resolution
 *   - Content-Type headers
 *   - AbortController integration
 *   - HTTP status validation
 *
 * @module api/client
 */
import config from '../config'

const DEFAULT_TIMEOUT_MS = 15000

/**
 * Fetch with automatic timeout via AbortController.
 *
 * @param {string} endpoint - API endpoint path (e.g. '/predict/heart')
 * @param {Object} options - Standard fetch options (method, body, headers)
 * @param {number} timeoutMs - Request timeout in milliseconds
 * @returns {Promise<Response>} Fetch response
 * @throws {Error} AbortError on timeout, TypeError on network failure
 */
export async function fetchWithTimeout(endpoint, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeoutMs)

    const url = endpoint.startsWith('http') ? endpoint : `${config.API_URL}${endpoint}`

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
        })
        return response
    } finally {
        clearTimeout(timer)
    }
}

/**
 * Make a JSON POST request to an API endpoint.
 *
 * @param {string} endpoint - API endpoint path
 * @param {Object} data - Request body payload
 * @returns {Promise<Object>} Parsed JSON response
 * @throws {Error} On network failure, timeout, or non-OK response
 */
export async function postJSON(endpoint, data) {
    const response = await fetchWithTimeout(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    })
    if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`
        try {
            const errorBody = await response.text()
            errorMessage += `: ${errorBody.slice(0, 200)}`
        } catch { /* ignore parse failure */ }
        throw new Error(errorMessage)
    }
    return response.json()
}

/**
 * Make a GET request to an API endpoint.
 *
 * @param {string} endpoint - API endpoint path
 * @returns {Promise<Object>} Parsed JSON response
 * @throws {Error} On network failure, timeout, or non-OK response
 */
export async function getJSON(endpoint) {
    const response = await fetchWithTimeout(endpoint)
    if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`
        try {
            const errorBody = await response.text()
            errorMessage += `: ${errorBody.slice(0, 200)}`
        } catch { /* ignore parse failure */ }
        throw new Error(errorMessage)
    }
    return response.json()
}
