import { useState, useEffect } from 'react'
import { usePredictionHistory } from './hooks/usePredictionHistory'
import HomePage from './components/HomePage'
import HeartForm from './components/HeartForm'
import DiabetesForm from './components/DiabetesForm'
import ParkinsonsForm from './components/ParkinsonsForm'
import ResultCard from './components/ResultCard'
import HistoryPage from './components/HistoryPage'
import ThemeToggle from './components/ThemeToggle'
import ToastContainer, { showToast } from './components/Toast'
import UserProfile from './components/UserProfile'
import HealthTips from './components/HealthTips'
import Dashboard from './components/Dashboard'
import SymptomChecker from './components/SymptomChecker'

const API_URL = 'http://localhost:5001/api'

function App() {
  const [selectedDisease, setSelectedDisease] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [currentPage, setCurrentPage] = useState('home') // home, history, profile, tips, dashboard, checker
  const { addPrediction } = usePredictionHistory()

  // Initialize theme on mount
  useEffect(() => {
    const saved = localStorage.getItem('theme')
    document.documentElement.setAttribute('data-theme', saved || 'light')
  }, [])

  // Get user name for personalization
  const getUserName = () => {
    try {
      const profile = JSON.parse(localStorage.getItem('user_profile') || '{}')
      return profile.name || ''
    } catch { return '' }
  }

  const handlePrediction = async (diseaseType, formData) => {
    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/predict/${diseaseType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (data.success) {
        setResult(data)
        addPrediction({
          disease: data.disease,
          risk_level: data.risk_level,
          confidence: data.confidence,
          prediction: data.prediction,
          advice: data.advice
        })
        showToast(
          data.risk_level === 'High'
            ? `⚠️ High risk detected for ${data.disease}`
            : `✅ Low risk for ${data.disease}`,
          data.risk_level === 'High' ? 'warning' : 'success'
        )
      } else {
        setError(data.error || 'An error occurred during prediction')
        showToast(data.error || 'Prediction failed', 'error')
      }
    } catch (error) {
      setError(`Connection error: Make sure the backend server is running at ${API_URL}`)
      showToast('Connection error. Is the backend running?', 'error')
      console.error('API Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedDisease(null)
    setResult(null)
    setError(null)
    setCurrentPage('home')
  }

  const handleSelectDisease = (disease) => {
    setSelectedDisease(disease)
    setCurrentPage('home')
    setResult(null)
    setError(null)
  }

  const renderForm = () => {
    switch (selectedDisease) {
      case 'heart':
        return <HeartForm onSubmit={(data) => handlePrediction('heart', data)} loading={loading} />
      case 'diabetes':
        return <DiabetesForm onSubmit={(data) => handlePrediction('diabetes', data)} loading={loading} />
      case 'parkinsons':
        return <ParkinsonsForm onSubmit={(data) => handlePrediction('parkinsons', data)} loading={loading} />
      default:
        return null
    }
  }

  // Render current page
  if (currentPage === 'history') {
    return (
      <>
        <ThemeToggle />
        <ToastContainer />
        <HistoryPage onClose={() => setCurrentPage('home')} />
      </>
    )
  }

  if (currentPage === 'profile') {
    return (
      <>
        <ThemeToggle />
        <ToastContainer />
        <UserProfile onClose={() => setCurrentPage('home')} />
      </>
    )
  }

  if (currentPage === 'tips') {
    return (
      <>
        <ThemeToggle />
        <ToastContainer />
        <HealthTips onClose={() => setCurrentPage('home')} />
      </>
    )
  }

  if (currentPage === 'dashboard') {
    return (
      <>
        <ThemeToggle />
        <ToastContainer />
        <Dashboard onClose={() => setCurrentPage('home')} />
      </>
    )
  }

  if (currentPage === 'checker') {
    return (
      <>
        <ThemeToggle />
        <ToastContainer />
        <SymptomChecker
          onClose={() => setCurrentPage('home')}
          onStartAssessment={(disease) => {
            handleSelectDisease(disease)
          }}
        />
      </>
    )
  }

  return (
    <div className="app-container">
      <ThemeToggle />
      <ToastContainer />
      {!selectedDisease ? (
        <HomePage
          onSelectDisease={handleSelectDisease}
          onViewHistory={() => setCurrentPage('history')}
          onViewProfile={() => setCurrentPage('profile')}
          onViewTips={() => setCurrentPage('tips')}
          onViewDashboard={() => setCurrentPage('dashboard')}
          onViewChecker={() => setCurrentPage('checker')}
          userName={getUserName()}
        />
      ) : (
        <div className="container">
          <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
              <button className="btn btn-secondary" onClick={handleReset}>
                ← Back to Home
              </button>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <button className="btn btn-secondary" onClick={() => setCurrentPage('dashboard')} style={{ width: 'auto' }}>
                  📊 Dashboard
                </button>
                <button className="btn btn-secondary" onClick={() => setCurrentPage('history')} style={{ width: 'auto' }}>
                  📋 History
                </button>
                <button className="btn btn-secondary" onClick={() => setCurrentPage('tips')} style={{ width: 'auto' }}>
                  🏥 Health Info
                </button>
              </div>
            </div>

            {renderForm()}

            {error && (
              <div style={{
                marginTop: '2rem',
                padding: '1rem',
                background: 'rgba(244, 92, 67, 0.1)',
                border: '2px solid #f45c43',
                borderRadius: '8px',
                color: '#f45c43',
                fontWeight: '500'
              }}>
                ⚠️ Error: {error}
              </div>
            )}

            {result && <ResultCard result={result} />}
          </div>

          <footer className="text-center mt-4" style={{ color: 'var(--text-light)', padding: '2rem 0' }}>
            <p>© 2026 Checkup Buddy | Made with ❤️ for better health awareness</p>
            <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
              ⚠️ This tool is for educational purposes only. Always consult a medical professional.
            </p>
          </footer>
        </div>
      )}
    </div>
  )
}

export default App
