const PrivacyPolicyPage = ({ onClose }) => {
  return (
    <div className="history-container">
      <div className="history-header">
        <div>
          <h1 className="history-title">Privacy Policy</h1>
          <p className="history-subtitle">Medixa AI</p>
        </div>
        <button className="btn btn-secondary" onClick={onClose} style={{ width: 'auto' }}>
          ← Back
        </button>
      </div>

      <div className="glass-card" style={{ padding: '1.25rem', lineHeight: 1.6 }}>
        <p>
          <strong>Local-first:</strong> Your prediction history is stored in your browser via localStorage
          (e.g., <code>prediction_history</code>) and is not automatically uploaded to a cloud service.
        </p>

        <p>
          <strong>Backend processing:</strong> When you run a prediction or use the symptom checker, your input is
          sent to the backend API to compute results. The API may store prediction logs in the server database
          (including your submitted biomarker fields and model output) to support auditing and reliability.
        </p>

        <p>
          <strong>IP address:</strong> The server currently stores the request IP address with prediction logs to
          support abuse prevention and basic record ownership checks.
        </p>

        <p>
          <strong>LLM:</strong> If the AI chat mode is enabled, your chat messages are sent to the configured LLM provider
          for response generation. Do not include identifying information. If LLM mode is disabled, the rule-based checker
          runs without third-party LLM calls.
        </p>

        <p>
          <strong>Your choices:</strong> You can clear your local history at any time from the History page. If you operate
          the platform in a multi-user environment, treat the device/browser as sensitive because localStorage is not encrypted.
        </p>

        <p>
          <strong>Security:</strong> We apply rate limiting and input validation. No system is risk-free; use strong access controls
          and HTTPS in production.
        </p>
      </div>
    </div>
  )
}

export default PrivacyPolicyPage

