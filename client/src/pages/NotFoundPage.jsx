/**
 * NotFoundPage — 404 error page component.
 *
 * Displayed for unmatched routes. Provides a clear message and navigation
 * back to the home page with consistent visual styling.
 *
 * @module components/pages/NotFoundPage
 */
import { Link } from 'react-router-dom'

const NotFoundPage = () => {
    return (
        <div className="prediction-page" style={{ textAlign: 'center', paddingTop: '80px' }}>
            <div style={{
                maxWidth: '500px', margin: '0 auto', padding: '3rem 2rem',
                borderRadius: '1.5rem', background: 'var(--card-bg, #fff)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.08)'
            }}>
                <div style={{ fontSize: '5rem', marginBottom: '1rem' }} aria-hidden="true">🔍</div>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--text-primary, #1a1a2e)' }}>
                    404
                </h1>
                <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary, #666)', marginBottom: '2rem' }}>
                    Page not found. The page you're looking for doesn't exist.
                </p>
                <Link
                    to="/"
                    style={{
                        display: 'inline-block', padding: '0.75rem 2rem',
                        borderRadius: '0.75rem', fontWeight: 600,
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        color: '#fff', textDecoration: 'none', fontSize: '1rem',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                    }}
                    aria-label="Return to home page"
                >
                    ← Back to Home
                </Link>
            </div>
        </div>
    )
}

export default NotFoundPage
