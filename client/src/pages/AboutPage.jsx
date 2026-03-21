import { useEffect } from 'react'
import { motion } from 'framer-motion'
import logoIcon from '../assets/logo-icon.png'
import udayImg from '../assets/uday-tikhile.png'
import '../styles/about.css'

const AboutPage = ({ onClose }) => {
    useEffect(() => {
        window.scrollTo(0, 0)
    }, [])

    // To use real photos, upload them to the client/src/assets folder,
    // import them at the top of the file (e.g., import udayImg from '../assets/uday.jpg')
    // and replace the 'image' string with the imported variable (e.g., image: udayImg).
    const team = [
        {
            name: 'Uday Tikhile',
            role: 'Lead Developer & AI Architect',
            desc: 'Merging healthcare with artificial intelligence to build predictive systems that save lives.',
            image: udayImg,
            highlight: true
        },
        {
            name: 'Amit Wadode',
            role: 'UI/UX Design',
            desc: 'Ensuring the platform is clean, intuitive, and easy to use for everyone.',
            image: 'https://ui-avatars.com/api/?name=Amit+Wadode&background=64748b&color=fff&size=200&bold=true',
            highlight: false
        },
        {
            name: 'Om Itnare',
            role: 'Backend & Database Manager',
            desc: 'Managing data processing, system logic, and performance optimization.',
            image: 'https://ui-avatars.com/api/?name=Om+Itnare&background=64748b&color=fff&size=200&bold=true',
            highlight: false
        },
        {
            name: 'Ujjwal Itnare',
            role: 'Content, Testing & Growth',
            desc: 'Ensuring accuracy, improving user experience, and helping the platform reach more users.',
            image: 'https://ui-avatars.com/api/?name=Ujjwal+Itnare&background=64748b&color=fff&size=200&bold=true',
            highlight: false
        }
    ]

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.15 }
        }
    }

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: {
            opacity: 1,
            y: 0,
            transition: { type: 'spring', stiffness: 100, damping: 15 }
        }
    }

    return (
        <div className="about-page">
            <button onClick={onClose} className="about-back-btn" aria-label="Go back">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="19" y1="12" x2="5" y2="12"></line>
                    <polyline points="12 19 5 12 12 5"></polyline>
                </svg>
                Back to app
            </button>

            <motion.div
                className="about-container"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
            >
                {/* Hero Section */}
                <motion.section className="about-hero" variants={itemVariants}>
                    <div className="about-hero-bg-glow"></div>
                    <img src={logoIcon} alt="Medixa AI Logo" className="about-logo" />
                    <h1 className="about-title">About Us</h1>
                    <p className="about-subtitle">Using AI to predict and prevent disease outbreaks</p>
                </motion.section>

                {/* Introduction Section */}
                <motion.section className="about-intro-card" variants={itemVariants}>
                    <div className="about-card-glow"></div>
                    <p>
                        At Medixa AI, we believe that the future of medicine lies in proactive prevention rather than responsive treatment.
                        By leveraging state-of-the-art machine learning models trained on validated clinical datasets, we empower individuals
                        and healthcare professionals to detect early warning signs of chronic diseases before they escalate.
                    </p>
                </motion.section>

                {/* Mission Section */}
                <motion.section className="about-mission" variants={itemVariants}>
                    <h2 className="about-section-title">Our Mission</h2>
                    <div className="mission-content">
                        <span className="mission-icon">🚀</span>
                        <p>
                            To democratize access to clinical-grade health screenings worldwide, making powerful predictive analytics
                            available, understandable, and actionable for everyone, everywhere.
                        </p>
                    </div>
                </motion.section>

                {/* Team Section */}
                <motion.section className="about-team" variants={itemVariants}>
                    <h2 className="about-section-title">The Team</h2>
                    <div className="team-grid">
                        {team.map((member, idx) => (
                            <motion.div
                                key={idx}
                                className={`team-card ${member.highlight ? 'team-lead' : ''}`}
                                whileHover={{ y: -8, transition: { duration: 0.2 } }}
                            >
                                <div className="team-avatar">
                                    {member.image ? (
                                        <img src={member.image} alt={`${member.name} photo`} />
                                    ) : (
                                        member.icon
                                    )}
                                </div>
                                <h3 className="team-name">{member.name}</h3>
                                <div className="team-role">{member.role}</div>
                                <p className="team-desc">{member.desc}</p>
                                {member.highlight && <div className="team-badge">Lead</div>}
                            </motion.div>
                        ))}
                    </div>
                </motion.section>

                {/* Footer Section */}
                <motion.section className="about-footer" variants={itemVariants}>
                    <p className="about-footer-text">This is just the beginning.</p>
                    <div className="about-footer-line"></div>
                </motion.section>
            </motion.div>
        </div>
    )
}

export default AboutPage
