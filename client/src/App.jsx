import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { usePredictionHistory } from './hooks/usePredictionHistory'
import config from './config'
import Navbar from './components/Navbar'
import HomePage from './components/HomePage'
import HeartForm from './components/HeartForm'
import DiabetesForm from './components/DiabetesForm'
import ParkinsonsForm from './components/ParkinsonsForm'
import ResultCard from './components/ResultCard'
import HistoryPage from './components/HistoryPage'
import ToastContainer, { showToast } from './components/Toast'
import UserProfile from './components/UserProfile'
import HealthTips from './components/HealthTips'
import Dashboard from './components/Dashboard'
import SymptomChecker from './components/SymptomChecker'

// Defined outside App to prevent re-mounting on every render (BUG-7 fix)
const PredictionLayout = ({ children, title, error, result }) => (
  <div className="prediction-page">
    <div className="container">
      <div className="glass-card prediction-card-wrapper">
        <h2 className="prediction-page-title">{title}</h2>
        {children}

        {error && (
          <div className="error-banner">
            <span className="error-banner-icon">⚠️</span>
            <div>
              <strong>Error</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {result && <ResultCard result={result} />}
      </div>

      <footer className="text-center mt-4" style={{ color: 'var(--text-light)', padding: '2rem 0' }}>
        <p>© 2026 Prexiza AI | Made with ❤️ for better health awareness</p>
        <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
          ⚠️ This tool is for educational purposes only. Always consult a medical professional.
        </p>
      </footer>
    </div>
  </div>
)

function App() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const { addPrediction } = usePredictionHistory()
  const navigate = useNavigate()
  const location = useLocation()

  // Initialize theme on mount
  useEffect(() => {
    const saved = localStorage.getItem('theme')
    document.documentElement.setAttribute('data-theme', saved || 'light')
  }, [])

  // Clear result/error on navigation
  useEffect(() => {
    setResult(null)
    setError(null)
  }, [location.pathname])

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
      const response = await fetch(`${config.API_URL}/predict/${diseaseType}`, {
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
      setError(`Connection error: Make sure the backend server is running at ${config.API_URL}`)
      showToast('Connection error. Is the backend running?', 'error')
      console.error('API Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    navigate('/')
  }


  return (
    <div className="app-container">
      <Navbar onNavigate={(path) => navigate(path)} />
      <ToastContainer />
      <Routes>
        <Route path="/" element={
          <HomePage
            onSelectDisease={(id) => navigate(`/predict/${id}`)}
            onViewHistory={() => navigate('/history')}
            onViewProfile={() => navigate('/profile')}
            onViewTips={() => navigate('/tips')}
            onViewDashboard={() => navigate('/dashboard')}
            onViewChecker={() => navigate('/checker')}
            userName={getUserName()}
          />
        } />

        <Route path="/predict/heart" element={
          <PredictionLayout title="❤️ Heart Disease Prediction" error={error} result={result}>
            <HeartForm onSubmit={(data) => handlePrediction('heart', data)} loading={loading} />
          </PredictionLayout>
        } />

        <Route path="/predict/diabetes" element={
          <PredictionLayout title="🩺 Diabetes Prediction" error={error} result={result}>
            <DiabetesForm onSubmit={(data) => handlePrediction('diabetes', data)} loading={loading} />
          </PredictionLayout>
        } />

        <Route path="/predict/parkinsons" element={
          <PredictionLayout title="🧠 Parkinson's Prediction" error={error} result={result}>
            <ParkinsonsForm onSubmit={(data) => handlePrediction('parkinsons', data)} loading={loading} />
          </PredictionLayout>
        } />

        <Route path="/history" element={<HistoryPage onClose={() => navigate('/')} />} />
        <Route path="/profile" element={<UserProfile onClose={() => navigate('/')} />} />
        <Route path="/tips" element={<HealthTips onClose={() => navigate('/')} />} />
        <Route path="/dashboard" element={<Dashboard onClose={() => navigate('/')} />} />
        <Route path="/checker" element={
          <SymptomChecker
            onClose={() => navigate('/')}
            onStartAssessment={(disease) => navigate(`/predict/${disease}`)}
          />
        } />
      </Routes>
    </div>
  )
}

export default App
