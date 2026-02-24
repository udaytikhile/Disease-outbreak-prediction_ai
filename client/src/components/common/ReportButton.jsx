import { useState } from 'react'
import config from '../../config'

/**
 * PDF Report download button — calls the reports API with prediction data.
 */
const ReportButton = ({ result }) => {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleDownload = async () => {
        if (!result) return

        setLoading(true)
        setError(null)

        try {
            const response = await fetch(`${config.API_URL}/reports/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    disease: result.disease,
                    risk_level: result.risk_level,
                    confidence: result.confidence,
                    prediction: result.prediction,
                    advice: result.advice,
                    shap_contributions: result.shap_contributions || [],
                }),
            })

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.error || 'Failed to generate report')
            }

            // Download the PDF
            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = `health_report_${result.disease || 'assessment'}.pdf`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            window.URL.revokeObjectURL(url)
        } catch (err) {
            console.error('Report generation error:', err)
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="report-button-container">
            <button
                className="report-download-btn"
                onClick={handleDownload}
                disabled={loading || !result}
                aria-label="Download PDF health report"
            >
                {loading ? (
                    <>
                        <span className="report-spinner" aria-hidden="true"></span>
                        Generating...
                    </>
                ) : (
                    <>📄 Download PDF Report</>
                )}
            </button>
            {error && (
                <p className="report-error" role="alert">
                    {error}
                </p>
            )}
        </div>
    )
}

export default ReportButton
