const TermsOfUsePage = ({ onClose }) => {
  return (
    <div className="history-container">
      <div className="history-header">
        <div>
          <h1 className="history-title">Terms of Use</h1>
          <p className="history-subtitle">Medixa AI</p>
        </div>
        <button className="btn btn-secondary" onClick={onClose} style={{ width: 'auto' }}>
          ← Back
        </button>
      </div>

      <div className="glass-card" style={{ padding: '1.25rem', lineHeight: 1.6 }}>
        <p>
          <strong>Medical disclaimer:</strong> Medixa AI is an AI-powered screening and educational tool.
          It does <strong>not</strong> provide medical advice, diagnosis, or treatment. Always consult a
          qualified healthcare professional for medical concerns. If you believe you have a medical emergency,
          call your local emergency number immediately.
        </p>

        <p>
          <strong>No clinician-patient relationship:</strong> Use of this product does not create a
          clinician-patient relationship.
        </p>

        <p>
          <strong>Limitations:</strong> Outputs may be incorrect, incomplete, or less reliable for inputs outside
          the model’s training distribution or for unusual clinical presentations. Do not use the platform as the
          sole basis for medical decisions.
        </p>

        <p>
          <strong>Acceptable use:</strong> You agree not to misuse the service, attempt to bypass safety controls,
          or overload the system (e.g., automated requests).
        </p>

        <p>
          <strong>Changes:</strong> These terms may be updated. Continued use indicates acceptance of the updated terms.
        </p>
      </div>
    </div>
  )
}

export default TermsOfUsePage

