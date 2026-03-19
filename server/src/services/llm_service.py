"""
LLM-Powered Symptom Checker Service.

Uses Google Gemini for conversational medical triage with graceful fallback
to the existing rule-based symptom checker when no API key is configured.
"""
import logging
import os
import re
import time
import uuid

logger = logging.getLogger('api')

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False
    logger.warning("⚠️  google-generativeai not installed — LLM symptom checker disabled.")

# In-memory session store (swap for Redis in production)
# WARNING: This dict is per-process. With Gunicorn -w 4, each worker has
# its own copy — a session created in worker 1 won't exist in worker 2.
# TODO: Replace with Flask-Session backed by Redis or database for production.
_sessions = {}
_MAX_SESSIONS = 1000
_SESSION_TTL_SECONDS = 1800  # 30 minutes
_MAX_TURNS_STORED = 10
_configured = False

MEDICAL_SYSTEM_PROMPT = """You are a professional AI health assistant. Your role is to:

1. Ask about symptoms in a conversational, empathetic manner
2. Ask relevant follow-up questions based on the symptoms described
3. Consider demographics (age, sex) when assessing risk
4. Detect emergency symptoms and flag them immediately
5. Provide a preliminary assessment with recommended next steps

IMPORTANT RULES:
- You are NOT a doctor. Always recommend consulting a healthcare professional.
- Never diagnose. Say "this might suggest" or "this could be related to" instead.
- If symptoms suggest a medical emergency (chest pain + shortness of breath, 
  signs of stroke, severe allergic reaction, suicidal ideation), immediately 
  flag it as an EMERGENCY and provide crisis resources.
- Keep responses concise (2-4 sentences per turn).
- Ask ONE follow-up question at a time.
- After 3-5 turns of symptom collection, provide a summary assessment.

EMERGENCY INDICATORS (always flag these):
- Chest pain with breathing difficulty → Possible heart attack
- Sudden numbness/weakness on one side → Possible stroke
- Difficulty breathing with swelling → Possible anaphylaxis
- Suicidal thoughts or self-harm → Mental health crisis (988 Lifeline)

When providing a summary, format it as:
**Assessment**: Brief summary
**Risk Level**: Low / Moderate / High / Emergency
**Recommended Actions**: 1-3 actionable steps
**Related Conditions to Screen**: List relevant prediction models (heart, diabetes, kidney, depression)
"""

_PROMPT_INJECTION_PATTERNS = [
    r"\bignore (all|any|previous|earlier) (instructions|rules|messages)\b",
    r"\bdisregard (all|any|previous|earlier) (instructions|rules|messages)\b",
    r"\byou are now\b",
    r"\b(system prompt|developer message|hidden instructions)\b",
    r"\bact as\b",
    r"\bpretend to be\b",
    r"\bDAN\b",
    r"\bjailbreak\b",
]

_DISALLOWED_MEDICAL_OUTPUT_PATTERNS = [
    r"\b(i diagnose you with|my diagnosis is|you have)\b",
    r"\bprescribe\b",
    r"\btake\s+\d+(\.\d+)?\s*(mg|mcg|g|ml)\b",
    r"\bstart (taking|using)\b.*\b(medication|drug|antibiotic)\b",
]


def _looks_like_prompt_injection(user_message: str) -> bool:
    text = (user_message or "").lower()
    return any(re.search(p, text) for p in _PROMPT_INJECTION_PATTERNS)


def _sanitize_user_message(user_message: str) -> str:
    """Best-effort sanitization: normalize whitespace and strip control chars."""
    if not user_message:
        return ""
    msg = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", str(user_message))
    msg = re.sub(r"\s+", " ", msg).strip()
    return msg


def _is_response_safe(ai_response: str) -> bool:
    if not ai_response:
        return True
    text = ai_response.lower()
    return not any(re.search(p, text) for p in _DISALLOWED_MEDICAL_OUTPUT_PATTERNS)


def _safety_rewrite() -> str:
    """Fallback message if the model output violates safety constraints."""
    return (
        "I can’t provide a diagnosis or medication instructions. "
        "I can help you think through symptoms and safe next steps.\n\n"
        "**Recommended Actions**: If symptoms are severe, worsening, or you’re unsure, "
        "seek urgent medical care or contact a clinician. If you have chest pain, "
        "severe breathing difficulty, stroke symptoms, or thoughts of self-harm, "
        "call emergency services immediately.\n\n"
        "Tell me your main symptoms, when they started, and any red flags (chest pain, "
        "shortness of breath, one-sided weakness, severe allergic reaction, suicidal thoughts)."
    )


def is_llm_available():
    """Check if LLM service is available and configured."""
    if not _GENAI_AVAILABLE:
        return False
    api_key = os.getenv('GEMINI_API_KEY', '')
    return bool(api_key.strip())


def _evict_stale_sessions():
    """Remove sessions older than TTL."""
    now = time.time()
    stale = [sid for sid, s in _sessions.items()
             if now - s.get('created_at', 0) > _SESSION_TTL_SECONDS]
    for sid in stale:
        _sessions.pop(sid, None)


def create_session():
    """Create a new chat session and return session ID."""
    _evict_stale_sessions()
    # Cap total sessions to prevent memory exhaustion
    if len(_sessions) >= _MAX_SESSIONS:
        oldest = min(_sessions, key=lambda k: _sessions[k].get('created_at', 0))
        _sessions.pop(oldest, None)
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        'history': [],
        'turn_count': 0,
        'created_at': time.time(),
    }
    return session_id


def chat(session_id, user_message):
    """Send a message in a chat session and get AI response.

    Args:
        session_id: str — session identifier
        user_message: str — user's symptom description

    Returns:
        dict with keys: response, is_emergency, suggestions, session_id
    """
    if not is_llm_available():
        return {
            'response': 'LLM service is not available. Please use the standard symptom checker.',
            'is_emergency': False,
            'suggestions': [],
            'session_id': session_id,
            'mode': 'fallback',
        }

    global _configured
    if not _configured:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))
        _configured = True

    # Get or create session
    if session_id not in _sessions:
        session_id = create_session()

    session = _sessions[session_id]
    session['turn_count'] += 1

    cleaned_user_message = _sanitize_user_message(user_message)
    if _looks_like_prompt_injection(cleaned_user_message):
        return {
            'response': (
                "I can’t follow instructions that try to override my safety rules. "
                "Please describe your symptoms, when they started, and any severe/emergency signs."
            ),
            'is_emergency': False,
            'suggestions': [
                "I have chest pain and shortness of breath",
                "I feel very tired and dizzy",
                "I've been feeling hopeless and can't sleep",
            ],
            'session_id': session_id,
            'turn_count': session['turn_count'],
            'mode': 'llm-guardrail',
        }

    # Build conversation history for context
    history_text = ""
    for turn in session['history']:
        history_text += f"Patient: {turn['user']}\nAssistant: {turn['assistant']}\n"

    # Construct the prompt
    prompt = (
        f"{MEDICAL_SYSTEM_PROMPT}\n\n"
        "Conversation so far:\n"
        f"{history_text}\n"
        "<user_input>\n"
        f"{cleaned_user_message}\n"
        "</user_input>\n\n"
        "Assistant:"
    )

    if session['turn_count'] >= 4:
        prompt += "\n\n(This is turn 4+. Please provide a summary assessment now.)"

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        ai_response = response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {
            'response': 'I apologize, but I encountered an error. Please try again or use the standard symptom checker.',
            'is_emergency': False,
            'suggestions': [],
            'session_id': session_id,
            'mode': 'error',
        }

    if not _is_response_safe(ai_response):
        logger.warning("LLM output failed safety check; rewriting response.")
        ai_response = _safety_rewrite()

    # Save to history
    session['history'].append({
        'user': cleaned_user_message,
        'assistant': ai_response,
    })
    if len(session['history']) > _MAX_TURNS_STORED:
        session['history'] = session['history'][-_MAX_TURNS_STORED:]

    # Check for emergency indicators
    emergency_keywords = [
        'emergency', 'call 911', 'call 988', 'go to er',
        'seek immediate', 'medical emergency', '🚨',
        'go to the emergency room', 'go to an emergency room', 'call emergency services',
        'seek urgent care', 'seek immediate medical attention',
    ]
    is_emergency = any(kw in ai_response.lower() for kw in emergency_keywords)

    # Generate contextual suggestions
    suggestions = _generate_suggestions(ai_response, session['turn_count'])

    return {
        'response': ai_response,
        'is_emergency': is_emergency,
        'suggestions': suggestions,
        'session_id': session_id,
        'turn_count': session['turn_count'],
        'mode': 'llm',
    }


def _generate_suggestions(ai_response, turn_count):
    """Generate clickable follow-up suggestions based on context."""
    if turn_count <= 1:
        return [
            "I've been feeling this for a few days",
            "It started suddenly",
            "I also have other symptoms",
        ]
    elif turn_count <= 3:
        return [
            "Yes, that's correct",
            "No, it's different",
            "I'd like a summary now",
        ]
    else:
        return [
            "What should I do next?",
            "Take me to the heart assessment",
            "Take me to the diabetes assessment",
        ]


def cleanup_session(session_id):
    """Remove a session from memory."""
    _sessions.pop(session_id, None)
