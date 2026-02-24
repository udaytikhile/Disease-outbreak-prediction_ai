"""
Symptom Checker — Route Controllers (thin layer).

These handlers parse HTTP requests, delegate to the symptom_service
for all business logic, and format JSON responses. No business logic
lives here — the route layer is a pure I/O boundary.
"""
from flask import Blueprint, request, jsonify
from ..extensions import limiter
from ..services.symptom_service import (
    validate_symptoms,
    validate_demographics,
    expand_synonyms,
    check_red_flags,
    match_symptoms,
    apply_followup_boosts,
    generate_advice,
    group_by_body_system,
    collect_followup_questions,
)
from ..services.symptom_data import (
    SYMPTOM_SUGGESTIONS,
    DISCLAIMER_TEXT,
)

symptom_checker_bp = Blueprint('symptom_checker', __name__)


# ══════════════════════════════════════════════════════════════════════════
#  RULE-BASED SYMPTOM ANALYSIS
# ══════════════════════════════════════════════════════════════════════════

@symptom_checker_bp.route('/symptom-check', methods=['POST'])
@limiter.limit("15 per minute")
def check_symptoms():
    """Enhanced AI-powered symptom analysis endpoint."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    # Validate inputs
    symptoms, symptom_error = validate_symptoms(data.get('symptoms', []))
    if symptom_error:
        return jsonify({'success': False, 'error': symptom_error}), 400

    age, sex = validate_demographics(data.get('age'), data.get('sex'))
    severity_map = data.get('severity_map', {})

    # Delegate all logic to service layer
    canonical_for_flags = [expand_synonyms(s) for s in symptoms]
    emergency_alerts = check_red_flags(canonical_for_flags)
    results, expansion_log = match_symptoms(symptoms, age=age, sex=sex, severity_map=severity_map)
    advice = generate_advice(results, symptoms, emergency_alerts)
    body_system_groups = group_by_body_system(results)
    followup_questions = collect_followup_questions(results)

    return jsonify({
        'success': True,
        'analysis': {
            'input_symptoms': symptoms,
            'expansion_log': expansion_log,
            'diseases': results,
            'body_system_groups': body_system_groups,
            'advice': advice,
            'emergency': len(emergency_alerts) > 0,
            'emergency_alerts': emergency_alerts,
            'followup_questions': followup_questions,
            'demographics': {'age': age, 'sex': sex},
            'total_symptoms_analyzed': len(symptoms),
            'diseases_screened': 4,
            'disclaimer': DISCLAIMER_TEXT,
        }
    })


@symptom_checker_bp.route('/symptom-followup', methods=['POST'])
@limiter.limit("15 per minute")
def symptom_followup():
    """Process follow-up question answers and refine diagnosis."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    # Validate inputs
    symptoms, symptom_error = validate_symptoms(data.get('symptoms', []))
    if symptom_error:
        return jsonify({'success': False, 'error': symptom_error}), 400

    age, sex = validate_demographics(data.get('age'), data.get('sex'))
    severity_map = data.get('severity_map', {})
    answers = data.get('answers', {})

    # Base matching
    results, _ = match_symptoms(symptoms, age=age, sex=sex, severity_map=severity_map)

    # Apply follow-up boosts
    results, crisis_triggered = apply_followup_boosts(results, answers)

    # Emergency detection
    canonical_for_flags = [expand_synonyms(s) for s in symptoms]
    emergency_alerts = check_red_flags(canonical_for_flags)

    # Handle crisis trigger (self-harm affirmation)
    if crisis_triggered:
        has_crisis = any(a["name"] == "Suicidal Crisis Indicators" for a in emergency_alerts)
        if not has_crisis:
            emergency_alerts.append({
                "name": "Suicidal Crisis Indicators",
                "message": (
                    "🚨 If you or someone you know is in crisis, please contact the "
                    "988 Suicide & Crisis Lifeline by calling or texting 988. "
                    "Help is available 24/7."
                ),
                "action": "Call/Text 988 Now",
                "severity": "critical",
            })

    advice = generate_advice(results, symptoms, emergency_alerts)
    body_system_groups = group_by_body_system(results)

    return jsonify({
        'success': True,
        'analysis': {
            'input_symptoms': symptoms,
            'diseases': results,
            'body_system_groups': body_system_groups,
            'advice': advice,
            'emergency': len(emergency_alerts) > 0,
            'emergency_alerts': emergency_alerts,
            'followup_questions': [],
            'demographics': {'age': age, 'sex': sex},
            'total_symptoms_analyzed': len(symptoms),
            'diseases_screened': 4,
            'disclaimer': DISCLAIMER_TEXT,
        }
    })


# ══════════════════════════════════════════════════════════════════════════
#  SUGGESTIONS
# ══════════════════════════════════════════════════════════════════════════

@symptom_checker_bp.route('/symptom-suggestions', methods=['GET'])
def get_suggestions():
    """Return expanded list of symptom suggestions with synonyms.
    ---
    tags:
      - Symptom Checker
    responses:
      200:
        description: Symptom suggestions list
    """
    from ..services.symptom_data import SYNONYM_MAP
    return jsonify({
        'success': True,
        'suggestions': SYMPTOM_SUGGESTIONS,
        'synonym_count': len(SYNONYM_MAP),
    })


# ══════════════════════════════════════════════════════════════════════════
#  LLM-POWERED CHAT ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════

@symptom_checker_bp.route('/symptom-checker/mode', methods=['GET'])
def get_checker_mode():
    """Check which symptom checker mode is active (LLM or rule-based).
    ---
    tags:
      - Symptom Checker
    responses:
      200:
        description: Current mode info
    """
    from ..services.llm_service import is_llm_available
    return jsonify({
        'success': True,
        'llm_available': is_llm_available(),
        'mode': 'llm' if is_llm_available() else 'rule-based',
    })


@symptom_checker_bp.route('/symptom-checker/chat', methods=['POST'])
@limiter.limit("20 per minute")
def chat_symptom_checker():
    """LLM-powered conversational symptom checker.
    ---
    tags:
      - Symptom Checker
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - message
          properties:
            message:
              type: string
              example: "I have been having chest pain and shortness of breath"
            session_id:
              type: string
              description: Session ID from a previous chat turn (omit for new session)
    responses:
      200:
        description: AI chat response
      400:
        description: Missing message
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400

    message = data.get('message', '').strip()
    if not message:
        return jsonify({'success': False, 'error': 'Message is required'}), 400

    if len(message) > 2000:
        return jsonify({'success': False, 'error': 'Message too long (max 2000 chars)'}), 400

    session_id = data.get('session_id')

    from ..services.llm_service import chat, create_session

    if not session_id:
        session_id = create_session()

    result = chat(session_id, message)

    return jsonify({
        'success': True,
        'chat': result,
    })


@symptom_checker_bp.route('/symptom-checker/chat/end', methods=['POST'])
def end_chat_session():
    """End and clean up a chat session.
    ---
    tags:
      - Symptom Checker
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            session_id:
              type: string
    responses:
      200:
        description: Session ended
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')

    if session_id:
        from ..services.llm_service import cleanup_session
        cleanup_session(session_id)

    return jsonify({'success': True, 'message': 'Session ended'})
