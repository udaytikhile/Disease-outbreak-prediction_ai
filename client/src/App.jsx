/**
 * App — Root application component (routing shell).
 *
 * This component is intentionally thin: it handles only routing and layout.
 * All business logic is in PredictionContext, all API calls in api/ modules,
 * and all state management in context/ and hooks/.
 *
 * Architecture:
 *   PredictionProvider → Navbar + Routes → Feature Components
 *
 * @module App
 */
import { useEffect, useMemo, lazy, Suspense } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { PredictionProvider } from './context/PredictionContext'
import { usePrediction } from './hooks/usePrediction'

// ── Common Components (eagerly loaded — always visible) ─────────────────
import Navbar from './components/common/Navbar'
import ToastContainer from './components/common/Toast'
import LoadingAnalysis from './components/common/LoadingAnalysis'
import ErrorBoundary from './components/common/ErrorBoundary'

// ── Lazy-loaded route components (code-split per route) ─────────────────
const PredictionLayout = lazy(() => import('./components/prediction/PredictionLayout'))
const HeartForm = lazy(() => import('./components/prediction/HeartForm'))
const DiabetesForm = lazy(() => import('./components/prediction/DiabetesForm'))
const KidneyForm = lazy(() => import('./components/prediction/KidneyForm'))
const DepressionForm = lazy(() => import('./components/prediction/DepressionForm'))

const HomePage = lazy(() => import('./pages/HomePage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))
const UserProfile = lazy(() => import('./pages/UserProfilePage'))
const HealthTips = lazy(() => import('./pages/HealthTipsPage'))

const HistoryPage = lazy(() => import('./pages/HistoryPage'))
const Dashboard = lazy(() => import('./pages/DashboardPage'))
const SymptomChecker = lazy(() => import('./components/symptom-checker/SymptomChecker'))
const SymptomCheckerChat = lazy(() => import('./components/symptom-checker/SymptomCheckerChat'))




/**
 * AppRoutes — Inner component that consumes PredictionContext.
 * Separated from App to allow usePrediction() hook usage.
 */
function AppRoutes() {
  const navigate = useNavigate()
  const { loading, loadingDisease, result, error, handlePrediction } = usePrediction()

  // Memoize to avoid JSON.parse on every render
  const userName = useMemo(() => {
    try {
      const profile = JSON.parse(localStorage.getItem('user_profile') || '{}')
      return profile.name || ''
    } catch { return '' }
  }, [])

  // Initialize theme on mount
  useEffect(() => {
    const saved = localStorage.getItem('theme')
    document.documentElement.setAttribute('data-theme', saved || 'light')
  }, [])

  // Move focus to main content on route change for accessibility
  const location = useLocation()
  useEffect(() => {
    const main = document.getElementById('main-content')
    if (main) {
      main.setAttribute('tabindex', '-1')
      main.focus({ preventScroll: true })
    }
  }, [location.pathname])

  return (
    <div className="app-container">
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <Navbar />
      <ToastContainer />
      {loading && <LoadingAnalysis disease={loadingDisease} />}
      <ErrorBoundary>
        <main id="main-content">
          <Suspense fallback={<LoadingAnalysis disease="app" />}>
            <Routes>
              {/* Home */}
              <Route path="/" element={
                <HomePage
                  onSelectDisease={(id) => navigate(`/predict/${id}`)}
                  onViewHistory={() => navigate('/history')}
                  onViewProfile={() => navigate('/profile')}
                  onViewTips={() => navigate('/tips')}
                  onViewDashboard={() => navigate('/dashboard')}
                  onViewChecker={() => navigate('/checker')}
                  userName={userName}
                />
              } />

              {/* Prediction Forms */}
              <Route path="/predict/heart" element={
                <PredictionLayout title="❤️ Heart Disease Prediction" error={error} result={result}>
                  <HeartForm onSubmit={(data) => handlePrediction('heart', data)} loading={loading} />
                </PredictionLayout>
              } />

              <Route path="/predict/diabetes" element={
                <PredictionLayout title="🩺 Diabetes Prediction" error={error} result={result} bgClass="diabetes-bg">
                  <DiabetesForm onSubmit={(data) => handlePrediction('diabetes', data)} loading={loading} />
                </PredictionLayout>
              } />

              <Route path="/predict/kidney" element={
                <PredictionLayout title="🫘 Kidney Disease Prediction" error={error} result={result}>
                  <KidneyForm onSubmit={(data) => handlePrediction('kidney', data)} loading={loading} />
                </PredictionLayout>
              } />

              <Route path="/predict/depression" element={
                <PredictionLayout title="🧠 Depression Screening" error={error} result={result}>
                  <DepressionForm onSubmit={(data) => handlePrediction('depression', data)} loading={loading} />
                </PredictionLayout>
              } />

              {/* Feature Pages */}
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
              <Route path="/chat" element={
                <SymptomCheckerChat
                  onClose={() => navigate('/')}
                  onStartAssessment={(disease) => navigate(`/predict/${disease}`)}
                />
              } />

              {/* 404 catch-all */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </main>
      </ErrorBoundary>
    </div>
  )
}


/**
 * App — Root component that wraps everything in providers.
 */
function App() {
  return (
    <PredictionProvider>
      <AppRoutes />
    </PredictionProvider>
  )
}

export default App
