"""
LLM-Powered Symptom Checker Service.

Uses Google Gemini for conversational medical triage with graceful fallback
to the existing rule-based symptom checker when no API key is configured.
"""
import logging
import os
import uuid

logger = logging.getLogger('api')

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False
    logger.warning("⚠️  google-generativeai not installed — LLM symptom checker disabled.")

# In-memory session store (swap for Redis in production)
_sessions = {}

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


def is_llm_available():
    """Check if LLM service is available and configured."""
    if not _GENAI_AVAILABLE:
        return False
    api_key = os.getenv('GEMINI_API_KEY', '')
    return bool(api_key.strip())


def create_session():
    """Create a new chat session and return session ID."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        'history': [],
        'turn_count': 0,
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

    api_key = os.getenv('GEMINI_API_KEY', '')
    genai.configure(api_key=api_key)

    # Get or create session
    if session_id not in _sessions:
        session_id = create_session()

    session = _sessions[session_id]
    session['turn_count'] += 1

    # Build conversation history for context
    history_text = ""
    for turn in session['history']:
        history_text += f"Patient: {turn['user']}\nAssistant: {turn['assistant']}\n"

    # Construct the prompt
    prompt = f"{MEDICAL_SYSTEM_PROMPT}\n\nConversation so far:\n{history_text}\nPatient: {user_message}\n\nAssistant:"

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

    # Save to history
    session['history'].append({
        'user': user_message,
        'assistant': ai_response,
    })

    # Check for emergency indicators
    emergency_keywords = [
        'emergency', 'call 911', 'call 988', 'go to er',
        'seek immediate', 'medical emergency', '🚨',
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
