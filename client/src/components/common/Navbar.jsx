import { useState, useEffect } from 'react'
import logo from '../../assets/logo-icon.png'
import { useLocation, Link } from 'react-router-dom'

const Navbar = ({ onNavigate }) => {
    const [isOpen, setIsOpen] = useState(false)
    const [scrolled, setScrolled] = useState(false)
    const [isDark, setIsDark] = useState(() => {
        const saved = localStorage.getItem('theme')
        return saved === 'dark'
    })
    const location = useLocation()

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20)
        window.addEventListener('scroll', handleScroll, { passive: true })
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
        localStorage.setItem('theme', isDark ? 'dark' : 'light')
    }, [isDark])

    // Close mobile menu on route change
    useEffect(() => {
        setIsOpen(false)
    }, [location.pathname])

    const navLinks = [
        { path: '/', label: 'Home', icon: '🏠' },
        { path: '/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/history', label: 'History', icon: '📋' },
        { path: '/tips', label: 'Health Info', icon: '🏥' },
        { path: '/checker', label: 'Symptom Check', icon: '🔍' },
        { path: '/profile', label: 'Profile', icon: '👤' },
    ]

    const isActive = (path) => location.pathname === path

    return (
        <>
            <nav className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>
                <div className="navbar-inner">
                    <Link to="/" className="navbar-brand">
                        <img src={logo} alt="Medixa AI" className="navbar-logo-img" style={{ height: '36px', width: '36px', objectFit: 'contain', flexShrink: 0 }} />
                        <span className="navbar-title">Medixa AI</span>
                    </Link>

                    <div className={`navbar-links ${isOpen ? 'open' : ''}`}>
                        {navLinks.map(link => (
                            <button
                                key={link.path}
                                className={`navbar-link ${isActive(link.path) ? 'active' : ''}`}
                                onClick={() => onNavigate(link.path)}
                            >
                                <span className="navbar-link-icon">{link.icon}</span>
                                <span className="navbar-link-label">{link.label}</span>
                            </button>
                        ))}
                    </div>

                    <div className="navbar-actions">
                        <button
                            className="navbar-theme-toggle"
                            onClick={() => setIsDark(!isDark)}
                            aria-label="Toggle theme"
                            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                        >
                            <div className={`navbar-toggle-track ${isDark ? 'dark' : 'light'}`}>
                                <span className="navbar-toggle-icon sun">☀️</span>
                                <span className="navbar-toggle-icon moon">🌙</span>
                                <div className="navbar-toggle-thumb" />
                            </div>
                        </button>

                        <button
                            className={`navbar-hamburger ${isOpen ? 'open' : ''}`}
                            onClick={() => setIsOpen(!isOpen)}
                            aria-label="Toggle menu"
                        >
                            <span></span>
                            <span></span>
                            <span></span>
                        </button>
                    </div>
                </div>
            </nav>

            {/* Mobile overlay */}
            {isOpen && <div className="navbar-overlay" onClick={() => setIsOpen(false)} />}
        </>
    )
}

export default Navbar
