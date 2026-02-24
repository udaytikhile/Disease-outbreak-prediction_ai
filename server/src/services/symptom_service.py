"""
Symptom Checker — Business Logic Service.

Pure functions for symptom analysis, scoring, and triage.
No Flask dependencies (no `request`, `jsonify`, or Blueprint) — making
this module independently testable and reusable.

Functions:
    expand_synonyms: Resolve user phrases to canonical symptom names
    check_red_flags: Detect emergency symptom combinations
    match_symptoms: Score user symptoms against the disease database
    apply_followup_boosts: Refine scores with follow-up question answers
    generate_advice: Produce severity-tiered medical guidance
    group_by_body_system: Organize results by anatomical system
    validate_demographics: Sanitize age/sex input values
    validate_symptoms: Sanitize and validate symptom list input
"""
from difflib import SequenceMatcher

from .symptom_data import (
    SYNONYM_MAP,
    RED_FLAG_RULES,
    SYMPTOM_DATABASE,
    FOLLOW_UP_QUESTIONS,
)


# ══════════════════════════════════════════════════════════════════════════
#  INPUT VALIDATION
# ══════════════════════════════════════════════════════════════════════════

def validate_symptoms(symptoms):
    """Validate and sanitize the symptom list.

    Args:
        symptoms: Raw symptom input from the request

    Returns:
        tuple: (cleaned_symptoms_list, error_message_or_None)
    """
    if not symptoms or not isinstance(symptoms, list):
        return [], 'Please provide a list of symptoms'

    cleaned = [s.strip() for s in symptoms if isinstance(s, str) and s.strip()]

    if len(cleaned) == 0:
        return [], 'Please provide at least one valid symptom'

    if len(cleaned) > 20:
        return [], 'Please provide no more than 20 symptoms at a time'

    return cleaned, None


def validate_demographics(age, sex):
    """Validate and normalize age/sex demographic values.

    Args:
        age: Raw age value (may be None, int, or string)
        sex: Raw sex value (may be None or string)

    Returns:
        tuple: (validated_age_or_None, validated_sex_or_None)
    """
    validated_age = None
    if age is not None:
        try:
            validated_age = int(age)
            if validated_age < 0 or validated_age > 150:
                validated_age = None
        except (ValueError, TypeError):
            validated_age = None

    validated_sex = None
    if sex:
        validated_sex = str(sex).lower()
        if validated_sex not in ('male', 'female', 'other'):
            validated_sex = None

    return validated_age, validated_sex


# ══════════════════════════════════════════════════════════════════════════
#  SYNONYM EXPANSION
# ══════════════════════════════════════════════════════════════════════════

def expand_synonyms(symptom_text):
    """Expand user input through synonym map to canonical form.

    First attempts a direct lookup, then tries partial/substring matching
    for more flexible resolution of colloquial symptom descriptions.

    Args:
        symptom_text: Raw user symptom string

    Returns:
        Canonical symptom name (str)
    """
    lower = symptom_text.lower().strip()

    # Direct synonym match (O(1) lookup)
    if lower in SYNONYM_MAP:
        return SYNONYM_MAP[lower]

    # Partial/substring match (fallback for compound phrases)
    for phrase, canonical in SYNONYM_MAP.items():
        if phrase in lower or lower in phrase:
            return canonical

    return lower


def _fuzzy_similarity(a, b):
    """Calculate Levenshtein-like similarity ratio between two strings.

    Uses Python's SequenceMatcher for typo tolerance in symptom matching.
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# ══════════════════════════════════════════════════════════════════════════
#  RED-FLAG DETECTION
# ══════════════════════════════════════════════════════════════════════════

def check_red_flags(canonical_symptoms):
    """Check if symptom combination triggers any emergency red flags.

    Evaluates each rule's required + supporting symptom thresholds.
    Uses substring matching to handle symptom name variations.

    Args:
        canonical_symptoms: List of canonical (expanded) symptom strings

    Returns:
        List of alert dicts with name, message, action, severity
    """
    alerts = []
    symptom_set = set(canonical_symptoms)

    for rule in RED_FLAG_RULES:
        # All required symptoms must be present (with substring tolerance)
        required_met = all(
            any(req in s or s in req for s in symptom_set)
            for req in rule["required"]
        )
        if not required_met:
            continue

        # Count how many supporting symptoms are present
        supporting_count = sum(
            1 for sup in rule["supporting"]
            if any(sup in s or s in sup for s in symptom_set)
        )
        if supporting_count >= rule["min_supporting"]:
            alerts.append({
                "name": rule["name"],
                "message": rule["message"],
                "action": rule["action"],
                "severity": "critical",
            })

    return alerts


# ══════════════════════════════════════════════════════════════════════════
#  CORE SYMPTOM MATCHING
# ══════════════════════════════════════════════════════════════════════════

def match_symptoms(user_symptoms, age=None, sex=None, severity_map=None):
    """Match user symptoms against the disease database with scoring.

    Applies synonym expansion, fuzzy matching, severity weighting,
    and demographic modifiers to produce ranked disease results.

    Args:
        user_symptoms: List of raw symptom strings
        age: Optional patient age (int)
        sex: Optional patient sex ('male'/'female'/'other')
        severity_map: Optional dict mapping symptom → severity level

    Returns:
        tuple: (sorted_results_list, expansion_log_list)
    """
    severity_map = severity_map or {}
    results = []

    # Step 1: Expand all synonyms
    canonical_symptoms = []
    expansion_log = []
    for s in user_symptoms:
        expanded = expand_synonyms(s)
        canonical_symptoms.append(expanded)
        if expanded != s.lower().strip():
            expansion_log.append({"original": s, "resolved_to": expanded})

    # Step 2: Score each disease
    for disease_key, disease_info in SYMPTOM_DATABASE.items():
        matched = []
        total_score = 0

        for idx, user_symptom in enumerate(user_symptoms):
            canonical = canonical_symptoms[idx]
            best_match = None
            best_score = 0

            for known_symptom, weight in disease_info["symptoms"].items():
                # Exact match on canonical form
                if canonical == known_symptom:
                    best_match = known_symptom
                    best_score = weight
                    break

                # Partial / substring match
                elif canonical in known_symptom or known_symptom in canonical:
                    if weight > best_score:
                        best_match = known_symptom
                        best_score = weight

                # Word-level overlap (handles multi-word symptoms)
                else:
                    user_words = set(canonical.split())
                    symptom_words = set(known_symptom.split())
                    overlap = user_words & symptom_words
                    if len(overlap) >= 1 and len(overlap) / max(len(user_words), len(symptom_words)) > 0.4:
                        candidate_score = weight * (len(overlap) / len(symptom_words))
                        if candidate_score > best_score:
                            best_match = known_symptom
                            best_score = candidate_score

                # Fuzzy match (typo tolerance, ~75% similarity threshold)
                if weight > best_score:
                    similarity = _fuzzy_similarity(canonical, known_symptom)
                    if similarity >= 0.75 and (weight * similarity) > best_score:
                        best_match = known_symptom
                        best_score = weight * similarity

            # Apply severity multiplier to matched score
            if best_match and best_score > 0:
                sev = severity_map.get(user_symptom, "moderate")
                sev_multiplier = {"mild": 0.7, "moderate": 1.0, "severe": 1.4}.get(sev, 1.0)
                best_score *= sev_multiplier

                matched.append({
                    "user_input": user_symptom,
                    "matched_to": best_match,
                    "weight": round(best_score, 2),
                    "severity": sev,
                })
                total_score += best_score

        if matched:
            # Apply demographic modifiers
            demo_factor = 1.0
            demo_notes = []
            if age is not None:
                age_mod = disease_info.get("age_modifier", {})
                if age_mod and age >= age_mod.get("threshold", 999):
                    demo_factor *= age_mod["factor"]
                    pct = round((age_mod["factor"] - 1) * 100)
                    demo_notes.append(f"Age {age} increases {disease_info['name']} risk (+{pct}%)")

            if sex:
                sex_mod = disease_info.get("sex_modifier", {})
                factor = sex_mod.get(sex.lower(), 1.0)
                if factor != 1.0:
                    demo_factor *= factor
                    pct = round((factor - 1) * 100)
                    demo_notes.append(f"Sex-based risk adjustment (+{pct}%)")

            adjusted_score = total_score * demo_factor

            # Confidence = adjusted score / max possible score for this symptom count
            max_possible = sum(
                sorted(disease_info["symptoms"].values(), reverse=True)[:len(user_symptoms)]
            )
            confidence = min(round(adjusted_score / max(max_possible, 1), 2), 0.99)

            # Urgency tiering based on score vs threshold
            urgency = "low"
            if adjusted_score >= disease_info["urgency_threshold"] * 1.5:
                urgency = "high"
            elif adjusted_score >= disease_info["urgency_threshold"]:
                urgency = "moderate"

            # Triage level (maps urgency + confidence to care pathway)
            if urgency == "high" and confidence > 0.5:
                triage = "urgent"
            elif urgency == "high":
                triage = "prompt"
            elif urgency == "moderate":
                triage = "standard"
            else:
                triage = "informational"

            # Determine if follow-up questions should be offered
            has_followups = (
                disease_key in FOLLOW_UP_QUESTIONS
                and 0.15 <= confidence <= 0.65
            )

            results.append({
                "name": disease_info["name"],
                "id": disease_info["id"],
                "icon": disease_info["icon"],
                "body_system": disease_info["body_system"],
                "body_system_icon": disease_info["body_system_icon"],
                "confidence": confidence,
                "score": round(adjusted_score, 1),
                "raw_score": round(total_score, 1),
                "matched_symptoms": matched,
                "urgency": urgency,
                "triage": triage,
                "description": disease_info["description"],
                "symptom_count": len(matched),
                "total_symptoms_checked": len(user_symptoms),
                "demographic_notes": demo_notes,
                "has_followup_questions": has_followups,
            })

    # Sort by score descending (highest-risk diseases first)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results, expansion_log


# ══════════════════════════════════════════════════════════════════════════
#  FOLLOW-UP ANSWER PROCESSING
# ══════════════════════════════════════════════════════════════════════════

def apply_followup_boosts(results, answers):
    """Apply follow-up question answer boosts to refine disease scores.

    Supports 'yesno' and 'select' question types. Also detects crisis
    triggers (e.g., self-harm affirmation).

    Args:
        results: List of disease result dicts from match_symptoms()
        answers: Dict mapping question_id → user answer

    Returns:
        tuple: (updated_results, crisis_triggered_bool)
    """
    if not isinstance(answers, dict):
        answers = {}

    crisis_triggered = False

    for r in results:
        disease_id = r["id"]
        disease_qs = FOLLOW_UP_QUESTIONS.get(disease_id, [])

        for q in disease_qs:
            answer = answers.get(q["id"])
            if answer is None:
                continue

            if q["type"] == "yesno" and str(answer).lower() in ("yes", "true", "1"):
                boosts = q.get("yes_boost", {})
                for boost_symptom, boost_val in boosts.items():
                    if boost_symptom == "_global":
                        r["score"] = round(r["score"] * boost_val, 1)
                        r["confidence"] = min(round(r["confidence"] * boost_val, 2), 0.99)
                    elif boost_symptom == "_crisis":
                        crisis_triggered = True
                    else:
                        r["score"] = round(r["score"] + boost_val, 1)

            elif q["type"] == "select":
                boosts_map = q.get("boosts", {})
                if str(answer) in boosts_map:
                    for boost_symptom, boost_val in boosts_map[str(answer)].items():
                        if boost_symptom == "_global":
                            r["score"] = round(r["score"] * boost_val, 1)
                            r["confidence"] = min(round(r["confidence"] * boost_val, 2), 0.99)
                        else:
                            r["score"] = round(r["score"] + boost_val, 1)

    # Re-sort after boosts
    results.sort(key=lambda x: x["score"], reverse=True)

    # Re-evaluate urgency after score changes
    for r in results:
        disease_info = SYMPTOM_DATABASE.get(r["id"], {})
        threshold = disease_info.get("urgency_threshold", 5)
        if r["score"] >= threshold * 1.5:
            r["urgency"] = "high"
            r["triage"] = "urgent"
        elif r["score"] >= threshold:
            r["urgency"] = "moderate"
            r["triage"] = "standard"
        else:
            r["urgency"] = "low"
            r["triage"] = "informational"

    return results, crisis_triggered


# ══════════════════════════════════════════════════════════════════════════
#  ADVICE GENERATION (severity-tiered)
# ══════════════════════════════════════════════════════════════════════════

def generate_advice(results, user_symptoms, emergency_alerts):
    """Generate contextual, severity-tiered medical advice.

    Returns different guidance based on whether emergencies were detected,
    and the urgency level of the top-scoring disease.

    Args:
        results: Sorted disease results from match_symptoms()
        user_symptoms: Original symptom list
        emergency_alerts: List of emergency alerts from check_red_flags()

    Returns:
        dict with level, icon, text, and self_care keys
    """
    if emergency_alerts:
        return {
            "level": "emergency",
            "icon": "🚨",
            "text": (
                "CRITICAL: Some of your symptoms match patterns associated with medical emergencies. "
                "Please review the emergency alerts above and seek immediate medical attention."
            ),
            "self_care": [],
        }

    if not results:
        return {
            "level": "informational",
            "icon": "ℹ️",
            "text": (
                "Based on the symptoms you described, I wasn't able to find a strong match "
                "with the conditions in our database. Consider consulting a healthcare "
                "professional for a thorough evaluation."
            ),
            "self_care": [
                "Keep a symptom diary to track patterns",
                "Stay hydrated and get adequate rest",
                "Schedule a check-up with your primary care physician",
            ],
        }

    top = results[0]
    if top["urgency"] == "high":
        return {
            "level": "urgent",
            "icon": "⚠️",
            "text": (
                f"Your symptoms show a notable alignment with {top['name']}. "
                f"I strongly recommend consulting a healthcare professional promptly. "
                f"You can take our {top['name']} risk assessment for a more detailed analysis."
            ),
            "self_care": [
                "Do not ignore persistent or worsening symptoms",
                "Seek medical attention within 24-48 hours",
                f"Consider our detailed {top['name']} assessment for more insights",
            ],
        }
    elif top["urgency"] == "moderate":
        return {
            "level": "standard",
            "icon": "📋",
            "text": (
                f"Your symptoms have some alignment with {top['name']}. "
                f"Consider taking our detailed assessment for a more comprehensive evaluation. "
                f"A follow-up with your doctor is also advisable."
            ),
            "self_care": [
                "Monitor your symptoms and note any changes",
                "Maintain healthy lifestyle habits",
                "Schedule a routine check-up with your doctor",
            ],
        }
    else:
        return {
            "level": "informational",
            "icon": "💡",
            "text": (
                f"Your symptoms show a mild correlation with {top['name']}. "
                f"While this may not be urgent, you can take our assessment for peace of mind, "
                f"or monitor your symptoms and consult a doctor if they persist."
            ),
            "self_care": [
                "Continue monitoring your symptoms",
                "Maintain a healthy diet and exercise routine",
                "Consult a healthcare provider if symptoms persist beyond 2 weeks",
            ],
        }


# ══════════════════════════════════════════════════════════════════════════
#  RESULT GROUPING
# ══════════════════════════════════════════════════════════════════════════

def group_by_body_system(results):
    """Group disease results by body system for organized display.

    Args:
        results: List of disease result dicts

    Returns:
        List of body-system group dicts
    """
    groups = {}
    for r in results:
        system = r["body_system"]
        if system not in groups:
            groups[system] = {
                "system": system,
                "icon": r["body_system_icon"],
                "diseases": [],
            }
        groups[system]["diseases"].append(r)
    return list(groups.values())


def collect_followup_questions(results, max_diseases=3):
    """Collect follow-up questions for the top disease results.

    Only includes questions for diseases where confidence is ambiguous
    (between 0.15 and 0.65), as indicated by has_followup_questions.

    Args:
        results: Sorted disease results
        max_diseases: Maximum number of diseases to collect questions for

    Returns:
        List of dicts with disease_id, disease_name, questions
    """
    followup_questions = []
    for r in results[:max_diseases]:
        if r.get("has_followup_questions"):
            disease_id = r["id"]
            qs = FOLLOW_UP_QUESTIONS.get(disease_id, [])
            followup_questions.append({
                "disease_id": disease_id,
                "disease_name": r["name"],
                "questions": qs,
            })
    return followup_questions
