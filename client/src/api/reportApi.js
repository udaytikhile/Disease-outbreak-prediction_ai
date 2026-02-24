/**
 * Report API — PDF report generation endpoint.
 *
 * @module api/reportApi
 */
import { fetchWithTimeout } from './client'
import config from '../config'

/**
 * Generate a PDF report from prediction data.
 *
 * Returns a Blob (not JSON) since the response is a PDF file.
 *
 * @param {Object} predictionData - Prediction results to include in report
 * @returns {Promise<Blob>} PDF file blob
 * @throws {Error} If report generation fails
 */
export async function generateReport(predictionData) {
    const response = await fetchWithTimeout('/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(predictionData),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Report generation failed' }))
        throw new Error(error.error || 'Report generation failed')
    }

    return response.blob()
}
