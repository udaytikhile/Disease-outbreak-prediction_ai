/**
 * Symptom API — Symptom checker endpoint functions.
 *
 * @module api/symptomApi
 */
import { postJSON, getJSON } from './client'

/**
 * Submit symptoms for rule-based analysis.
 *
 * @param {Object} params
 * @param {string[]} params.symptoms - List of symptom strings
 * @param {number} [params.age] - Patient age
 * @param {string} [params.sex] - Patient sex
 * @param {Object} [params.severityMap] - Symptom severity overrides
 * @returns {Promise<Object>} Analysis results with diseases, advice, alerts
 */
export async function checkSymptoms({ symptoms, age, sex, severityMap }) {
    return postJSON('/symptom-check', {
        symptoms,
        age,
        sex,
        severity_map: severityMap,
    })
}

/**
 * Submit follow-up answers to refine symptom analysis.
 *
 * @param {Object} params
 * @param {string[]} params.symptoms - Original symptom list
 * @param {Object} params.answers - Follow-up question answers
 * @param {number} [params.age] - Patient age
 * @param {string} [params.sex] - Patient sex
 * @returns {Promise<Object>} Refined analysis results
 */
export async function submitFollowup({ symptoms, answers, age, sex, severityMap }) {
    return postJSON('/symptom-followup', {
        symptoms,
        answers,
        age,
        sex,
        severity_map: severityMap,
    })
}

/**
 * Get symptom suggestions for autocomplete.
 *
 * @returns {Promise<Object>} Suggestions list
 */
export async function getSuggestions() {
    return getJSON('/symptom-suggestions')
}

/**
 * Check which symptom checker mode is active.
 *
 * @returns {Promise<Object>} Mode info (llm or rule-based)
 */
export async function getCheckerMode() {
    return getJSON('/symptom-checker/mode')
}

/**
 * Send a message to the LLM-powered symptom checker.
 *
 * @param {string} message - User message
 * @param {string} [sessionId] - Existing session ID
 * @returns {Promise<Object>} Chat response
 */
export async function chatSymptomChecker(message, sessionId) {
    return postJSON('/symptom-checker/chat', { message, session_id: sessionId })
}

/**
 * End an LLM chat session.
 *
 * @param {string} sessionId - Session ID to clean up
 * @returns {Promise<Object>} Confirmation
 */
export async function endChatSession(sessionId) {
    return postJSON('/symptom-checker/chat/end', { session_id: sessionId })
}
