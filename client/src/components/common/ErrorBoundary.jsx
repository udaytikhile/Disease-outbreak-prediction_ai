import { Component } from 'react'

/**
 * React Error Boundary — catches render errors in child components
 * and shows a fallback UI instead of a white screen.
 */
class ErrorBoundary extends Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false, error: null, errorInfo: null }
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error }
    }

    componentDidCatch(error, errorInfo) {
        this.setState({ errorInfo })
        console.error('ErrorBoundary caught:', error, errorInfo)
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null })
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary" role="alert" aria-live="assertive">
                    <div className="error-boundary-card">
                        <div className="error-boundary-icon">⚠️</div>
                        <h2 className="error-boundary-title">Something went wrong</h2>
                        <p className="error-boundary-message">
                            An unexpected error occurred. Please try again or return to the home page.
                        </p>
                        {this.state.error && (
                            <details className="error-boundary-details">
                                <summary>Technical Details</summary>
                                <pre>{this.state.error.toString()}</pre>
                            </details>
                        )}
                        <div className="error-boundary-actions">
                            <button
                                className="error-boundary-btn primary"
                                onClick={this.handleReset}
                                aria-label="Try again"
                            >
                                🔄 Try Again
                            </button>
                            <button
                                className="error-boundary-btn secondary"
                                onClick={() => window.location.href = '/'}
                                aria-label="Go to home page"
                            >
                                🏠 Go Home
                            </button>
                        </div>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
