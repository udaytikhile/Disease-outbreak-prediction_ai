// IMPROVED: Added motion-based message entrance and richer markdown rendering styles for improved chat readability and feel.
import { useState, useRef, useEffect, useCallback } from 'react'
import { getCheckerMode, chatSymptomChecker, endChatSession } from '../../api/symptomApi'
import ReactMarkdown from 'react-markdown'
import { motion, AnimatePresence } from 'framer-motion'
import '../../styles/symptom-checker-chat.css'

const SAFE_PROTOCOLS = new Set(['http:', 'https:', 'mailto:', 'tel:'])
const MESSAGE_VARIANTS = {
    hidden: { opacity: 0, y: 18 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.22, ease: [0.4, 0, 0.2, 1] } },
}
const MARKDOWN_COMPONENTS = {
    code: ({ inline, children }) =>
        inline ? <code className="md-inline-code">{children}</code> : <code className="md-code-block">{children}</code>,
    h1: ({ children }) => <h3 className="md-h1">{children}</h3>,
    h2: ({ children }) => <h4 className="md-h2">{children}</h4>,
    ul: ({ children }) => <ul className="md-list">{children}</ul>,
    ol: ({ children }) => <ol className="md-list">{children}</ol>,
    li: ({ children }) => <li className="md-list-item">{children}</li>,
    a: ({ href, children, ...props }) => {
        const safe = sanitizeHref(href)
        if (!safe) return <span {...props}>{children}</span>
        const external = safe.startsWith('http')
        return (
            <a
                href={safe}
                target={external ? '_blank' : undefined}
                rel={external ? 'noreferrer noopener' : undefined}
                {...props}
            >
                {children}
            </a>
        )
    },
}

function sanitizeHref(href) {
    if (!href || typeof href !== 'string') return null
    try {
        const url = new URL(href, window.location.origin)
        if (!SAFE_PROTOCOLS.has(url.protocol)) return null
        return url.toString()
    } catch {
        return null
    }
}

/**
 * LLM-powered conversational symptom checker chat UI.
 * Falls back to rule-based mode when LLM is unavailable.
 */
const SymptomCheckerChat = ({ onClose, onStartAssessment }) => {
    const mkMessage = useCallback((message) => ({ id: crypto.randomUUID(), ...message }), [])
    const [messages, setMessages] = useState(() => [
        mkMessage({
            role: 'assistant',
            content: "Hello! I'm your AI Health Assistant. 👋\n\nI can help you understand your symptoms and guide you to the right care. **Tell me what symptoms you're experiencing**, and I'll ask follow-up questions to better understand your situation.\n\n> ⚕️ Remember: I'm not a doctor. Always consult a healthcare professional for medical advice.",
            suggestions: [
                "I have chest pain",
                "I feel very tired lately",
                "I've been feeling anxious and sad",
            ],
        }),
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [mode, setMode] = useState('checking')
    const messagesEndRef = useRef(null)
    const inputRef = useRef(null)

    // Check which mode is available
    useEffect(() => {
        const checkMode = async () => {
            try {
                const data = await getCheckerMode()
                setMode(data.mode || 'rule-based')
            } catch {
                setMode('rule-based')
            }
        }
        checkMode()
    }, [])

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const sendMessage = async (text) => {
        if (!text.trim() || loading) return

        const userMsg = mkMessage({ role: 'user', content: text })
        setMessages((prev) => [...prev, userMsg])
        setInput('')
        setLoading(true)

        try {
            const data = await chatSymptomChecker(text, sessionId)

            if (data.success && data.chat) {
                if (!sessionId && data.chat.session_id) {
                    setSessionId(data.chat.session_id)
                }

                const assistantMsg = {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: data.chat.response,
                    isEmergency: data.chat.is_emergency,
                    suggestions: data.chat.suggestions || [],
                    mode: data.chat.mode,
                }
                setMessages((prev) => [...prev, assistantMsg])
            } else {
                setMessages((prev) => [
                    ...prev,
                    {
                        id: crypto.randomUUID(),
                        role: 'assistant',
                        content: data.error || "I'm sorry, something went wrong. Please try again.",
                        isError: true,
                    },
                ])
            }
        } catch (err) {
            console.error('Chat error:', err)
            setMessages((prev) => [
                ...prev,
                {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: "I couldn't connect to the server. Please check your connection and try again.",
                    isError: true,
                },
            ])
        } finally {
            setLoading(false)
            inputRef.current?.focus()
        }
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        sendMessage(input)
    }

    const handleSuggestion = (suggestion) => {
        sendMessage(suggestion)
    }

    const handleEndSession = async () => {
        if (sessionId) {
            try {
                await endChatSession(sessionId)
            } catch { /* ignore */ }
        }
        onClose?.()
    }

    return (
        <div className="chat-container" role="main" aria-label="AI Symptom Checker Chat">
            {/* Header */}
            <div className="chat-header">
                <div className="chat-header-info">
                    <h2 className="chat-title">🤖 AI Health Assistant</h2>
                    <span className={`chat-mode-badge ${mode}`}>
                        {mode === 'llm' ? '✨ AI-Powered' : '📋 Rule-Based'}
                    </span>
                </div>
                <button
                    className="chat-close-btn"
                    onClick={handleEndSession}
                    aria-label="Close chat"
                >
                    ✕
                </button>
            </div>

            <div className="chat-disclaimer-banner" role="note" aria-label="Medical disclaimer">
                ⚕️ This is for informational screening only — not medical advice or a diagnosis.
                If you have severe symptoms or an emergency, call your local emergency number immediately.
            </div>

            {/* Messages */}
            <div className="chat-messages" role="log" aria-live="polite">
                <AnimatePresence initial={false}>
                {messages.map((msg) => (
                    <motion.div
                        key={msg.id}
                        className={`chat-bubble ${msg.role} ${msg.isEmergency ? 'emergency' : ''} ${msg.isError ? 'error' : ''}`}
                        variants={MESSAGE_VARIANTS}
                        initial="hidden"
                        animate="visible"
                    >
                        {msg.role === 'assistant' && (
                            <div className="chat-avatar" aria-hidden="true">🤖</div>
                        )}
                        <div className="chat-bubble-content">
                            {msg.role === 'assistant' ? (
                                <ReactMarkdown
                                    components={MARKDOWN_COMPONENTS}
                                >
                                    {msg.content}
                                </ReactMarkdown>
                            ) : (
                                <p>{msg.content}</p>
                            )}

                            {msg.isEmergency && (
                                <div className="chat-emergency-banner" role="alert">
                                    🚨 Emergency indicators detected. Please seek immediate medical attention.
                                </div>
                            )}

                            {msg.suggestions && msg.suggestions.length > 0 && (
                                <div className="chat-suggestions">
                                    {msg.suggestions.map((s, i) => (
                                        <button
                                            key={i}
                                            className="chat-suggestion-chip"
                                            onClick={() => handleSuggestion(s)}
                                            disabled={loading}
                                        >
                                            {s}
                                        </button>
                                    ))}
                                </div>
                            )}

                            {msg.role === 'assistant' && (
                                <div className="chat-message-disclaimer">
                                    Not medical advice. For emergencies, call your local emergency number.
                                </div>
                            )}
                        </div>
                    </motion.div>
                ))}
                </AnimatePresence>

                {loading && (
                    <motion.div className="chat-bubble assistant" variants={MESSAGE_VARIANTS} initial="hidden" animate="visible">
                        <div className="chat-avatar" aria-hidden="true">🤖</div>
                        <div className="chat-typing">
                            <span></span><span></span><span></span>
                        </div>
                    </motion.div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form className="chat-input-form" onSubmit={handleSubmit}>
                <input
                    ref={inputRef}
                    type="text"
                    className="chat-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Describe your symptoms..."
                    disabled={loading}
                    aria-label="Type your symptoms"
                    autoFocus
                />
                <button
                    type="submit"
                    className="chat-send-btn"
                    disabled={!input.trim() || loading}
                    aria-label="Send message"
                >
                    ➤
                </button>
            </form>

            {/* Quick actions */}
            <div className="chat-quick-actions">
                <button
                    className="chat-action-btn"
                    onClick={() => onStartAssessment?.('heart')}
                    aria-label="Start heart disease assessment"
                >
                    ❤️ Heart Assessment
                </button>
                <button
                    className="chat-action-btn"
                    onClick={() => onStartAssessment?.('diabetes')}
                    aria-label="Start diabetes assessment"
                >
                    🩺 Diabetes Assessment
                </button>
                <button
                    className="chat-action-btn"
                    onClick={() => onStartAssessment?.('kidney')}
                    aria-label="Start kidney disease assessment"
                >
                    🫘 Kidney Assessment
                </button>
                <button
                    className="chat-action-btn"
                    onClick={() => onStartAssessment?.('depression')}
                    aria-label="Start depression screening"
                >
                    🧠 Depression Screening
                </button>
            </div>
        </div>
    )
}

export default SymptomCheckerChat
