"""
Symptom Checker — Data Constants Module.

Pure data definitions used by the symptom checker service.
Separating data from logic enables independent testing, easier updates
to symptom databases, and potential future migration to a database.

Contains:
    - SYNONYM_MAP: Common user phrases → canonical symptom names
    - RED_FLAG_RULES: Emergency symptom combination rules
    - SYMPTOM_DATABASE: Disease definitions with weighted symptoms
    - FOLLOW_UP_QUESTIONS: Contextual follow-up questions per disease
    - SYMPTOM_SUGGESTIONS: Quick-pick symptom list for the UI
    - DISCLAIMER_TEXT: Standard medical disclaimer
"""

# ══════════════════════════════════════════════════════════════════════════
#  SYNONYM MAP — Common phrases → canonical symptom names
# ══════════════════════════════════════════════════════════════════════════
SYNONYM_MAP = {
    # Breathing
    "cant breathe": "shortness of breath", "can't breathe": "shortness of breath",
    "hard to breathe": "shortness of breath", "breathing difficulty": "shortness of breath",
    "trouble breathing": "shortness of breath", "gasping": "shortness of breath",
    "out of breath": "shortness of breath", "breathless": "shortness of breath",
    "winded": "shortness of breath", "suffocating": "shortness of breath",
    # Chest
    "chest hurts": "chest pain", "chest ache": "chest pain",
    "heart hurts": "chest pain", "pressure in chest": "chest tightness",
    "heavy chest": "chest tightness", "chest squeeze": "chest tightness",
    # Urination
    "peeing a lot": "frequent urination", "pee a lot": "frequent urination",
    "always urinating": "frequent urination", "constant urination": "frequent urination",
    "blood when peeing": "blood in urine", "bloody urine": "blood in urine",
    "foamy pee": "foamy urine", "bubbly urine": "foamy urine",
    "dark pee": "dark urine", "brown urine": "dark urine",
    "pee less": "decreased urination", "not peeing": "decreased urination",
    # Thirst / Hunger
    "very thirsty": "excessive thirst", "always thirsty": "excessive thirst",
    "drink a lot of water": "excessive thirst", "parched": "excessive thirst",
    "always hungry": "increased hunger", "eating a lot": "increased hunger",
    # Fatigue / Energy
    "always tired": "fatigue", "no energy": "fatigue", "exhausted": "fatigue",
    "worn out": "fatigue", "drained": "fatigue", "weak": "fatigue",
    "low energy": "low energy", "lethargic": "fatigue", "sluggish": "fatigue",
    # Vision
    "blurry vision": "blurred vision", "cant see clearly": "blurred vision",
    "fuzzy vision": "blurred vision", "vision problems": "blurred vision",
    # Heart
    "heart racing": "rapid heartbeat", "fast heartbeat": "rapid heartbeat",
    "heart fluttering": "heart palpitations", "skipped heartbeat": "irregular heartbeat",
    "pounding heart": "heart palpitations", "heartbeat irregular": "irregular heartbeat",
    # Mental Health
    "feeling sad": "persistent sadness", "feeling down": "persistent sadness",
    "feeling blue": "persistent sadness", "feel depressed": "persistent sadness",
    "no motivation": "low motivation", "dont care anymore": "loss of interest",
    "lost interest": "loss of interest", "no interest": "loss of interest",
    "cant concentrate": "difficulty concentrating", "brain fog": "difficulty concentrating",
    "cant focus": "difficulty concentrating", "memory loss": "memory problems",
    "forgetful": "memory problems", "feeling hopeless": "hopelessness",
    "feeling worthless": "worthlessness", "feel guilty": "guilt",
    "cant sleep": "insomnia", "trouble sleeping": "sleep problems",
    "sleeping too much": "oversleeping", "mood changes": "mood swings",
    "nervous": "anxiety", "worried": "anxiety", "panic": "anxiety",
    "feel alone": "loneliness", "feel empty": "feeling empty",
    "withdrawn": "social withdrawal", "isolated": "social withdrawal",
    "crying a lot": "crying spells",
    # Movement / Neuro
    "shaky hands": "hand tremor", "hands shaking": "hand tremor",
    "trembling": "tremor", "shaking hands": "hand tremor",
    "stiff muscles": "muscle stiffness", "rigid muscles": "rigid muscles",
    "hard to walk": "difficulty walking", "balance issues": "balance problems",
    "off balance": "impaired balance", "clumsy": "coordination problems",
    "slow moving": "slow movement", "shuffling feet": "shuffling walk",
    "small writing": "small handwriting", "quiet voice": "soft speech",
    "face expressionless": "facial masking", "drool": "drooling",
    "hard to swallow": "difficulty swallowing", "cant smell": "loss of smell",
    # Pain
    "head hurts": "headaches", "headache": "headaches", "migraine": "headaches",
    "back hurts": "back pain", "lower back hurts": "lower back pain",
    "arm hurts": "arm pain", "left arm hurts": "left arm pain",
    "jaw hurts": "jaw pain", "shoulder hurts": "shoulder pain",
    "body hurts": "body aches", "aching body": "body aches",
    # Swelling
    "feet swollen": "swollen ankles", "legs swollen": "swollen legs",
    "ankles swollen": "swollen ankles", "puffy face": "puffy eyes",
    "swollen face": "puffy eyes", "bloated": "swelling",
    # Skin
    "itching": "itchy skin", "skin itching": "itchy skin",
    "dry patches": "dry skin", "skin dry": "dry skin",
    "dark patches": "darkened skin", "skin darkening": "darkened skin",
    # Digestive
    "throwing up": "vomiting", "feel sick": "nausea", "queasy": "nausea",
    "no appetite": "loss of appetite", "not hungry": "loss of appetite",
    "constipated": "constipation", "blocked up": "constipation",
    # Weight
    "losing weight": "unexplained weight loss", "weight dropping": "unexplained weight loss",
    "gaining weight": "weight gain", "putting on weight": "weight gain",
    # Other
    "dizzy": "dizziness", "lightheaded": "lightheadedness", "passed out": "fainting",
    "fainted": "fainting", "tingling hands": "tingling hands",
    "tingling feet": "tingling feet", "pins and needles": "tingling",
    "numb hands": "numbness in hands", "numb feet": "numbness in feet",
    "numb": "numbness", "sweaty": "cold sweats", "night sweats": "cold sweats",
    "dehydrated": "dehydration", "wounds not healing": "slow healing wounds",
    "cuts not healing": "slow healing wounds", "sweet breath": "sweet smelling breath",
    "fruity breath": "sweet smelling breath", "metallic mouth": "metallic taste",
    "taste metal": "metallic taste", "muscle cramp": "muscle cramps",
    "leg cramps": "muscle cramps", "bp high": "high blood pressure",
    "hypertension": "high blood pressure", "infections often": "frequent infections",
    "yeast infection": "yeast infections", "irritable": "irritability",
    "stressed": "stress", "restless": "restlessness", "agitated": "restlessness",
}

# ══════════════════════════════════════════════════════════════════════════
#  RED-FLAG EMERGENCY COMBINATIONS
# ══════════════════════════════════════════════════════════════════════════
RED_FLAG_RULES = [
    {
        "name": "Possible Heart Attack",
        "required": ["chest pain"],
        "supporting": ["shortness of breath", "cold sweats", "left arm pain", "jaw pain", "nausea"],
        "min_supporting": 1,
        "message": "🚨 Your symptoms may indicate a cardiac emergency. Please call emergency services (911) immediately or have someone drive you to the nearest emergency room.",
        "action": "Call 911 / Emergency Services NOW"
    },
    {
        "name": "Possible Stroke",
        "required": ["numbness"],
        "supporting": ["difficulty concentrating", "dizziness", "difficulty walking", "speech changes"],
        "min_supporting": 1,
        "message": "🚨 These symptoms could indicate a stroke. Remember FAST: Face drooping, Arm weakness, Speech difficulty, Time to call 911.",
        "action": "Call 911 / Emergency Services NOW"
    },
    {
        "name": "Diabetic Emergency",
        "required": ["sweet smelling breath"],
        "supporting": ["nausea", "vomiting", "excessive thirst", "frequent urination", "dehydration"],
        "min_supporting": 2,
        "message": "🚨 These symptoms may indicate diabetic ketoacidosis (DKA), a medical emergency. Seek immediate medical attention.",
        "action": "Go to Emergency Room Immediately"
    },
    {
        "name": "Severe Cardiac Symptoms",
        "required": ["irregular heartbeat", "fainting"],
        "supporting": ["chest pain", "shortness of breath", "dizziness"],
        "min_supporting": 0,
        "message": "🚨 Irregular heartbeat combined with fainting requires immediate medical evaluation. Do not drive yourself.",
        "action": "Call 911 / Emergency Services NOW"
    },
    {
        "name": "Suicidal Crisis Indicators",
        "required": ["hopelessness", "worthlessness"],
        "supporting": ["social withdrawal", "insomnia", "loss of interest", "feeling empty"],
        "min_supporting": 2,
        "message": "🚨 If you or someone you know is in crisis, please contact the 988 Suicide & Crisis Lifeline by calling or texting 988. Help is available 24/7.",
        "action": "Call/Text 988 Now"
    },
]

# ══════════════════════════════════════════════════════════════════════════
#  DISEASE DATABASE — with Body-System Grouping
# ══════════════════════════════════════════════════════════════════════════
SYMPTOM_DATABASE = {
    "heart": {
        "name": "Heart Disease", "icon": "❤️", "id": "heart",
        "body_system": "Cardiovascular",
        "body_system_icon": "🫀",
        "symptoms": {
            "chest pain": 3, "chest tightness": 3, "shortness of breath": 2.5,
            "irregular heartbeat": 3, "heart palpitations": 2.5, "dizziness": 1.5,
            "fatigue": 1, "swollen legs": 2, "swollen ankles": 2, "cold sweats": 2,
            "nausea": 1, "jaw pain": 2, "arm pain": 2.5, "left arm pain": 3,
            "shoulder pain": 1.5, "high blood pressure": 2, "rapid heartbeat": 2.5,
            "fainting": 2, "lightheadedness": 1.5, "chest discomfort": 2.5,
            "difficulty breathing": 2, "wheezing": 1, "back pain": 0.5, "numbness": 1,
        },
        "urgency_threshold": 6,
        "description": "Symptoms suggest possible cardiovascular concerns. Heart disease risk factors include high blood pressure, cholesterol, smoking, and family history.",
        "age_modifier": {"threshold": 45, "factor": 1.2},
        "sex_modifier": {"male": 1.15, "female": 1.0},
    },
    "diabetes": {
        "name": "Diabetes", "icon": "🩺", "id": "diabetes",
        "body_system": "Endocrine",
        "body_system_icon": "🧪",
        "symptoms": {
            "frequent urination": 3, "excessive thirst": 3, "increased hunger": 2.5,
            "unexplained weight loss": 2.5, "blurred vision": 2, "fatigue": 1.5,
            "slow healing wounds": 2.5, "slow healing": 2.5, "tingling hands": 2,
            "tingling feet": 2, "numbness in hands": 2, "numbness in feet": 2,
            "dry skin": 1, "frequent infections": 2, "darkened skin": 1.5,
            "yeast infections": 1.5, "irritability": 1, "sweet smelling breath": 3,
            "nausea": 1, "vomiting": 1, "dehydration": 2, "weight gain": 1.5,
            "numbness": 1.5, "tingling": 2,
        },
        "urgency_threshold": 5,
        "description": "Symptoms align with possible blood sugar irregularities. Diabetes risk increases with obesity, inactivity, family history, and age.",
        "age_modifier": {"threshold": 40, "factor": 1.15},
        "sex_modifier": {"male": 1.05, "female": 1.0},
    },
    "kidney": {
        "name": "Kidney Disease", "icon": "🫘", "id": "kidney",
        "body_system": "Renal",
        "body_system_icon": "🫘",
        "symptoms": {
            "swollen legs": 2.5, "swollen ankles": 2.5, "puffy eyes": 2.5,
            "frequent urination": 2, "decreased urination": 3, "blood in urine": 3,
            "foamy urine": 3, "dark urine": 2, "fatigue": 1.5, "nausea": 1.5,
            "vomiting": 1.5, "loss of appetite": 1.5, "muscle cramps": 2,
            "back pain": 2, "lower back pain": 2.5, "high blood pressure": 2,
            "difficulty sleeping": 1, "dry skin": 1, "itchy skin": 2,
            "metallic taste": 2, "shortness of breath": 1.5, "swelling": 2,
            "ankle swelling": 2.5, "dehydration": 1.5, "weight loss": 1,
        },
        "urgency_threshold": 5,
        "description": "Symptoms may indicate kidney function concerns. Risk factors include diabetes, high blood pressure, heart disease, and family history.",
        "age_modifier": {"threshold": 50, "factor": 1.1},
        "sex_modifier": {"male": 1.05, "female": 1.0},
    },
    "depression": {
        "name": "Depression", "icon": "🧠", "id": "depression",
        "body_system": "Mental Health",
        "body_system_icon": "🧠",
        "symptoms": {
            "persistent sadness": 3, "sadness": 2.5, "hopelessness": 3,
            "loss of interest": 3, "fatigue": 2, "sleep problems": 2.5,
            "insomnia": 2.5, "oversleeping": 2, "appetite changes": 2,
            "weight changes": 1.5, "difficulty concentrating": 2.5, "anxiety": 2,
            "irritability": 2, "restlessness": 1.5, "guilt": 2,
            "worthlessness": 3, "social withdrawal": 2.5, "low energy": 2,
            "low motivation": 2.5, "crying spells": 2, "body aches": 1,
            "headaches": 1, "memory problems": 1.5, "mood swings": 2,
            "feeling empty": 3, "loneliness": 2, "stress": 1.5,
        },
        "urgency_threshold": 5,
        "description": "Symptoms align with potential mood or mental health concerns. Depression is a common, treatable condition affecting millions worldwide.",
        "age_modifier": {"threshold": 0, "factor": 1.0},
        "sex_modifier": {"male": 1.0, "female": 1.1},
    },
}

# ══════════════════════════════════════════════════════════════════════════
#  FOLLOW-UP QUESTIONS — per disease, triggered on ambiguous confidence
# ══════════════════════════════════════════════════════════════════════════
FOLLOW_UP_QUESTIONS = {
    "heart": [
        {"id": "pain_radiation", "question": "Does the chest pain radiate to your arm, jaw, or back?",
         "type": "yesno", "yes_boost": {"left arm pain": 2, "jaw pain": 1.5}},
        {"id": "exertion_trigger", "question": "Do your symptoms worsen with physical exertion?",
         "type": "yesno", "yes_boost": {"chest pain": 1, "shortness of breath": 1}},
        {"id": "family_history", "question": "Do you have a family history of heart disease?",
         "type": "yesno", "yes_boost": {"_global": 1.2}},
    ],
    "diabetes": [
        {"id": "wound_healing", "question": "Have you noticed cuts or wounds healing more slowly than usual?",
         "type": "yesno", "yes_boost": {"slow healing wounds": 2}},
        {"id": "vision_change", "question": "Have you experienced any sudden changes in your vision?",
         "type": "yesno", "yes_boost": {"blurred vision": 1.5}},
        {"id": "family_diabetes", "question": "Does anyone in your family have diabetes?",
         "type": "yesno", "yes_boost": {"_global": 1.15}},
    ],
    "kidney": [
        {"id": "urine_change", "question": "Have you noticed any changes in your urine (color, foaminess, frequency)?",
         "type": "select", "options": ["Darker than usual", "Foamy/bubbly", "Much less output", "No changes"],
         "boosts": {"Darker than usual": {"dark urine": 2}, "Foamy/bubbly": {"foamy urine": 2},
                    "Much less output": {"decreased urination": 2}}},
        {"id": "swelling_location", "question": "Where do you notice swelling the most?",
         "type": "select", "options": ["Around eyes", "Ankles/feet", "Hands", "No swelling"],
         "boosts": {"Around eyes": {"puffy eyes": 2}, "Ankles/feet": {"swollen ankles": 2}}},
    ],
    "depression": [
        {"id": "duration", "question": "How long have you been feeling this way?",
         "type": "select", "options": ["Less than 2 weeks", "2-4 weeks", "1-3 months", "More than 3 months"],
         "boosts": {"2-4 weeks": {"_global": 1.1}, "1-3 months": {"_global": 1.2},
                    "More than 3 months": {"_global": 1.3}}},
        {"id": "daily_impact", "question": "Are these feelings affecting your daily activities (work, relationships)?",
         "type": "yesno", "yes_boost": {"_global": 1.2}},
        {"id": "self_harm", "question": "Have you had any thoughts of harming yourself?",
         "type": "yesno", "yes_boost": {"_crisis": True}},
    ],
}

# ── Quick Symptom Suggestions (expanded with common phrasing) ───────────
SYMPTOM_SUGGESTIONS = [
    "Chest Pain", "Shortness of Breath", "Fatigue", "Frequent Urination",
    "Excessive Thirst", "Blurred Vision", "Tremor", "Muscle Stiffness",
    "Persistent Sadness", "Insomnia", "Swollen Ankles", "Dizziness",
    "Nausea", "Back Pain", "Heart Palpitations", "Weight Loss",
    "Difficulty Concentrating", "Blood in Urine", "Anxiety",
    "Numbness", "Headaches", "High Blood Pressure",
    "Loss of Appetite", "Sleep Problems", "Cold Sweats",
    "Jaw Pain", "Left Arm Pain", "Vomiting", "Tingling",
    "Mood Swings", "Memory Problems", "Loss of Interest",
    "Hand Tremor", "Balance Problems", "Foamy Urine",
    "Itchy Skin", "Slow Healing Wounds", "Difficulty Walking",
]

# ── Standard Medical Disclaimer ─────────────────────────────────────────
DISCLAIMER_TEXT = (
    "⚕️ IMPORTANT: This AI-powered health analysis is for informational and "
    "educational purposes only. It does NOT constitute medical advice, diagnosis, "
    "or treatment. Always consult a qualified healthcare professional for proper "
    "evaluation. If you are experiencing a medical emergency, call 911 immediately. "
    "No data is stored or shared — your privacy is protected."
)
