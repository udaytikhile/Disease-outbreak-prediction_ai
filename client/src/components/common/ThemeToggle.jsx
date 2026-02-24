import { useState, useEffect } from 'react'

const ThemeToggle = () => {
    const [isDark, setIsDark] = useState(() => {
        const saved = localStorage.getItem('theme')
        return saved === 'dark'
    })

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
        localStorage.setItem('theme', isDark ? 'dark' : 'light')
    }, [isDark])

    return (
        <button
            className="theme-toggle"
            onClick={() => setIsDark(!isDark)}
            aria-label="Toggle theme"
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
            <div className={`theme-toggle-track ${isDark ? 'dark' : 'light'}`}>
                <span className="theme-toggle-icon sun">☀️</span>
                <span className="theme-toggle-icon moon">🌙</span>
                <div className="theme-toggle-thumb" />
            </div>
        </button>
    )
}

export default ThemeToggle
