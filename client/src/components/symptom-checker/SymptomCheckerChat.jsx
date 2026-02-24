import { useState, useRef, useEffect } from 'react'
import config from '../../config'
import ReactMarkdown from 'react-markdown'
import './SymptomCheckerChat.css'

/**
 * LLM-powered conversational symptom checker chat UI.
 * Falls back to rule-based mode when LLM is unavailable.
 */
const SymptomCheckerChat = ({ onClose, onStartAssessment }) => {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: "Hello! I'm your AI Health Assistant. 👋\n\nI can help you understand your symptoms and guide you to the right care. **Tell me what symptoms you're experiencing**, and I'll ask follow-up questions to better understand your situation.\n\n> ⚕️ Remember: I'm not a doctor. Always consult a healthcare professional for medical advice.",
            suggestions: [
                "I have chest pain",
                "I feel very tired lately",
                "I've been feeling anxious and sad",
            ],
        },
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
                const res = await fetch(`${config.API_URL}/symptom-checker/mode`)
                const data = await res.json()
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

        const userMsg = { role: 'user', content: text }
        setMessages((prev) => [...prev, userMsg])
        setInput('')
        setLoading(true)

        try {
            const res = await fetch(`${config.API_URL}/symptom-checker/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    session_id: sessionId,
                }),
            })

            const data = await res.json()

            if (data.success && data.chat) {
                if (!sessionId && data.chat.session_id) {
                    setSessionId(data.chat.session_id)
                }

                const assistantMsg = {
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
                await fetch(`${config.API_URL}/symptom-checker/chat/end`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId }),
                })
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

            {/* Messages */}
            <div className="chat-messages" role="log" aria-live="polite">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`chat-bubble ${msg.role} ${msg.isEmergency ? 'emergency' : ''} ${msg.isError ? 'error' : ''}`}
                    >
                        {msg.role === 'assistant' && (
                            <div className="chat-avatar" aria-hidden="true">🤖</div>
                        )}
                        <div className="chat-bubble-content">
                            {msg.role === 'assistant' ? (
                                <ReactMarkdown>{msg.content}</ReactMarkdown>
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
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="chat-bubble assistant">
                        <div className="chat-avatar" aria-hidden="true">🤖</div>
                        <div className="chat-typing">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
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
