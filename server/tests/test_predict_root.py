import requests

tests = {
    'diabetes': {
        "HighBP": 1, "HighChol": 1, "CholCheck": 1, "BMI": 25, "Smoker": 0, "Stroke": 0,
        "HeartDiseaseorAttack": 0, "PhysActivity": 1, "Fruits": 1, "Veggies": 1,
        "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0, "GenHlth": 3,
        "MentHlth": 0, "PhysHlth": 0, "DiffWalk": 0, "Sex": 1, "Age": 5, "Education": 4,
        "Income": 5
    },
    'heart': {
        "age": 45, "sex": "Male", "cp": "asymptomatic", "trestbps": 120, "chol": 200,
        "fbs": "FALSE", "restecg": "normal", "thalch": 150, "exang": "FALSE",
        "oldpeak": 1.0, "slope": "flat", "ca": 0, "thal": "normal"
    },
    'kidney': {
        "age": 45, "bp": 80, "sg": 1.020, "al": 0, "su": 0, "rbc": 1, "pc": 1, "pcc": 0,
        "ba": 0, "bgr": 120, "bu": 30, "sc": 1.0, "sod": 140, "pot": 4.5, "hemo": 15,
        "pcv": 44, "wc": 8000, "rc": 5.0, "htn": 0, "dm": 0, "cad": 0, "appet": 1,
        "pe": 0, "ane": 0
    },
    'depression': {
        "gender": "Male", "age": 20, "profession": "Student", "academic_pressure": 3,
        "work_pressure": 0, "cgpa": 8.0, "study_satisfaction": 4, "job_satisfaction": 0,
        "sleep_duration": "7-8 hours", "dietary_habits": "Moderate", "degree": "BSc",
        "suicidal_thoughts": "No", "work_study_hours": 6, "financial_stress": 2,
        "family_history": "No"
    }
}

for disease, data in tests.items():
    try:
        res = requests.post(f"http://localhost:5001/api/predict/{disease}", json=data)
        print(f"[{disease}] -> {res.status_code}")
        print(res.json())
    except Exception as e:
        print(f"[{disease}] -> ERROR {e}")

