import { useState } from 'react'
import { generateReport } from '../../api/reportApi'

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
            const blob = await generateReport({
                disease: result.disease,
                risk_level: result.risk_level,
                confidence: result.confidence,
                prediction: result.prediction,
                advice: result.advice,
                shap_contributions: result.shap_contributions || [],
            })

            // Download the PDF
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
