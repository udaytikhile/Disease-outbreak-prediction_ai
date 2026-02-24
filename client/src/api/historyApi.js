/**
 * History API — Prediction history endpoint functions.
 *
 * @module api/historyApi
 */
import { getJSON } from './client'

/**
 * Fetch paginated prediction history.
 *
 * @param {Object} params - Query parameters
 * @param {number} params.page - Page number (default 1)
 * @param {number} params.perPage - Items per page (default 20)
 * @param {string} [params.disease] - Optional disease type filter
 * @returns {Promise<Object>} Paginated history response
 */
export async function getHistory({ page = 1, perPage = 20, disease } = {}) {
    let endpoint = `/history?page=${page}&per_page=${perPage}`
    if (disease) endpoint += `&disease=${disease}`
    return getJSON(endpoint)
}

/**
 * Fetch aggregate prediction statistics.
 *
 * @returns {Promise<Object>} Statistics by disease type
 */
export async function getStats() {
    return getJSON('/history/stats')
}
