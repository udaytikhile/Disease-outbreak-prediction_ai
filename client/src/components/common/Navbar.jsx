import { useState, useEffect } from 'react'
import logo from '../../assets/logo-icon.png'
import { useLocation, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const Navbar = () => {
    const MotionDiv = motion.div
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

    // Prevent scrolling when mobile menu is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden'
            const handleEscape = (e) => {
                if (e.key === 'Escape') setIsOpen(false)
            }
            document.addEventListener('keydown', handleEscape)
            return () => {
                document.body.style.overflow = ''
                document.removeEventListener('keydown', handleEscape)
            }
        } else {
            document.body.style.overflow = ''
        }
        return () => {
            document.body.style.overflow = ''
        }
    }, [isOpen])

    // Mobile menu is closed by clicking links directly or outside click

    const navLinks = [
        { path: '/', label: 'Home', icon: '🏠' },
        { path: '/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/history', label: 'History', icon: '📋' },
        { path: '/tips', label: 'Health Info', icon: '🏥' },
        { path: '/checker', label: 'Symptom Check', icon: '🔍' },
        { path: '/profile', label: 'Profile', icon: '👤' },
        { path: '/privacy', label: 'Privacy', icon: '🔒' },
        { path: '/terms', label: 'Terms', icon: '📜' },
    ]

    const isActive = (path) => location.pathname === path

    return (
        <>
            <nav className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>
                <div className="navbar-inner">
                    <Link to="/" className="navbar-brand">
                        <img src={logo} alt="Medixa AI" className="navbar-logo-img" />
                        <span className="navbar-title">Medixa AI</span>
                    </Link>

                    <AnimatePresence>
                        {(isOpen || window.innerWidth > 768) && (
                            <MotionDiv
                                id="navbar-links"
                                className={`navbar-links ${isOpen ? 'open' : ''}`}
                                initial={isOpen ? { height: 0, opacity: 0 } : false}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.2 }}
                            >
                                {navLinks.map(link => (
                                    <Link
                                        key={link.path}
                                        to={link.path}
                                        className={`navbar-link ${isActive(link.path) ? 'active' : ''}`}
                                        onClick={() => setIsOpen(false)}
                                    >
                                        <span className="navbar-link-icon">{link.icon}</span>
                                        <span className="navbar-link-label">{link.label}</span>
                                    </Link>
                                ))}
                            </MotionDiv>
                        )}
                    </AnimatePresence>

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
                            aria-label={isOpen ? 'Close menu' : 'Open menu'}
                            aria-expanded={isOpen}
                            aria-controls="navbar-links"
                        >
                            <span></span>
                            <span></span>
                            <span></span>
                        </button>
                    </div>
                </div>
            </nav>

            {/* Mobile overlay */}
            {isOpen && <div className="navbar-overlay" role="presentation" onClick={() => setIsOpen(false)} />}
        </>
    )
}

export default Navbar
