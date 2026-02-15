import streamlit as st
import pickle
import numpy as np
from io import BytesIO
from fpdf import FPDF
import os
import base64
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Checkup Buddy", layout="wide", page_icon="🧫")

with st.sidebar:
    # Center the image using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("Images/Logo 1.png"):
            st.image("Images/Logo 1.png", width=200)
# Language Selection
lang = st.sidebar.selectbox("🌐 Select Language / மொழியையை தேர்வு செல்லவும்", ["English", "Tamil"])

# Translations
def get_translations():
    return {
        "English": {
            "title": "Disease Prediction Model ⚕️",
            "welcome": "Welcome to the Disease Prediction Web App",
            "about": "### About\nThis application uses machine learning to predict the risk of three major diseases using user-provided health metrics.",
            "instructions": "### Instructions\n1. Use the **sidebar** to select a disease (Heart, Diabetes, or Parkinson’s).\n2. Enter the patient’s information and test values.\n3. Click **Diagnose** to view the prediction and advice.\n4. Download a PDF report if needed.",
            "purpose": "### Purpose\nEarly detection can help initiate medical consultation and preventive care.",
            "contact": "📧 Contact",
            "disclaimer": "✅ This tool is for **educational** and **preventive awareness** purposes only.\nAlways consult a licensed medical professional for real diagnoses.",
            "nav": "## Navigation",
            "goto": "Go to",
            "home": "Home",
            "no_risk": "The Person does not have a risk of",
            "risk": "The Person has a risk of",
            "download": "📄 Download Report (PDF)",
            "advice": "💡 Advice",
            "heart": "Heart Disease Prediction",
            "diabetes": "Diabetes Prediction",
            "parkinsons": "Parkinson's Disease Prediction",
            "diagnose": "Diagnose",
            "advice_heart_positive": "Consult a cardiologist.",
            "advice_heart_negative": "Maintain a healthy lifestyle.",
            "advice_diabetes_positive": "Check sugar regularly.",
            "advice_diabetes_negative": "Maintain a balanced diet and exercise.",
            "advice_parkinsons_positive": "Consult a neurologist.",
            "advice_parkinsons_negative": "Stay active and healthy.",
            "inputs_heart": {
                "name": "Patient Name", "age": "Age", "sex": "Sex", "cp": "Chest Pain Type",
                "trestbps": "Resting Blood Pressure", "chol": "Serum Cholesterol",
                "fbs": "Fasting Blood Sugar", "restecg": "Resting ECG", "thalach": "Max Heart Rate",
                "exang": "Exercise Induced Angina", "oldpeak": "ST Depression",
                "slope": "Slope of ST", "ca": "Major Vessels Colored", "thal": "Thalassemia",
                "options": {"sex": ["0 - Male", "1 - Female"]}
            },
            "inputs_diabetes": {
                "name": "Patient Name", "age": "Age", "sex": "Sex","pregnancies": "Pregnancies", "glucose": "Glucose",
                "blood_pressure": "Blood Pressure", "skin_thickness": "Skin Thickness",
                "insulin": "Insulin", "bmi": "BMI", "dpf": "Diabetes Pedigree Function",
                "options": {"sex": ["0 - Male", "1 - Female"]}
            },
            "inputs_parkinsons": {
                "name": "Patient Name", "age": "Age", "sex": "Sex", "fo": "MDVP:Fo(Hz)", "fhi": "MDVP:Fhi(Hz)",
                "flo": "MDVP:Flo(Hz)", "jitter": "MDVP:Jitter(%)", "jitter_abs": "MDVP:Jitter(Abs)",
                "rap": "MDVP:RAP", "ppq": "MDVP:PPQ", "ddp": "Jitter:DDP", "shimmer": "MDVP:Shimmer",
                "shimmer_db": "MDVP:Shimmer(dB)", "apq3": "Shimmer:APQ3", "apq5": "Shimmer:APQ5",
                "apq": "MDVP:APQ", "dda": "Shimmer:DDA", "nhr": "NHR", "hnr": "HNR",
                "rpde": "RPDE", "dfa": "DFA", "spread1": "Spread1", "spread2": "Spread2",
                "d2": "D2", "ppe": "PPE", "options": {"sex": ["0 - Male", "1 - Female"]}
            }
        },

        "Tamil": {
            "title": "நோய் கணிப்பதற்கான மாதல் ⚕️",
            "welcome": "நோய் கணிப்பு இணைய பயன்பாட்டிற்கு வரவேற்கிறோம்",
            "about": "### பற்றி\nஇந்த பயன்பாடு, பயனர் வழங்கும் உடல்நலக் கூறுகளை அடிப்படையாகக் கொண்டு மூன்று முக்கிய நோய்களின் அபாயத்தை இயந்திரக் கற்றலின் மூலம் கணிக்கிறது.",
            "instructions": "### வழிமுறைகள்\n1. பக்கப்பட்டியில் இருந்து (இதய நோய், மதுமேகம் அல்லது பார்கின்சன்) தேர்ந்தெடுக்கவும்.\n2. நோயாளியின் விவரங்களையும் மருத்துவ மதிப்பீடுகளையும் உள்ளிடவும்.\n3. **கணிக்கவும்** பொத்தானை அழுத்தவும்.\n4. தேவைப்பட்டால் PDF அறிக்கையை பதிவிறக்கவும்.",
            "purpose": "### நோக்கம்\nமுன்கூட்டிய கண்டறிதல் மருத்துவ ஆலோசனையையும் தடுப்பு பராமரிப்பையும் துவக்க உதவும்.",
            "contact": "📧 தொடர்புக்கு",
            "disclaimer": "✅ இந்த கருவி கல்வி மற்றும் தடுப்பு விழிப்புணர்வு நோக்கத்திற்காக மட்டுமே.\nஉண்மையான மருத்துவக் கண்டறிதலுக்காக தவறாமல் தகுதியுள்ள மருத்துவ நிபுணரை அணுகவும்.",
            "nav": "## வழிசெலுத்தல்",
            "goto": "செல்ல",
            "home": "முகப்பு",
            "no_risk": "நபருக்கு நோய்க்கான அபாயம் இல்லை",
            "risk": "நபருக்கு நோய்க்கான அபாயம் உள்ளது",
            "download": "📄 அறிக்கையை பதிவிறக்கவும் (PDF)",
            "advice": "💡 ஆலோசனை",
            "heart": "இதய நோய் கணிப்பு",
            "diabetes": "மதுமேகம் கணிப்பு",
            "parkinsons": "பார்கின்சன் நோய் கணிப்பு",
            "diagnose": "கணிக்கவும்",
            "advice_heart_positive": "மருத்துவ ஆலோசனைக்காக கார்டியாலஜிஸ்டைப் பாருங்கள்.",
            "advice_heart_negative": "நல்ல வாழ்க்கை முறையை பராமரிக்கவும்.",
            "advice_diabetes_positive": "இரத்த சர்க்கரை நிலையை அடிக்கடி பரிசோதிக்கவும்.",
            "advice_diabetes_negative": "மனநலனுடன் உணவு பழக்கவழக்கத்தையும் பயிற்சியையும் பின்பற்றவும்.",
            "advice_parkinsons_positive": "நரம்பியல் நிபுணரை அணுகவும்.",
            "advice_parkinsons_negative": "சுறுசுறுப்பாகவும் ஆரோக்கியமாகவும் இருங்கள்.",
            "inputs_heart": {
                "name": "நோயாளி பெயர்", "age": "வயது", "sex": "பாலினம்", "cp": "மார்புதவிச்சொட்டு வகை",
                "trestbps": "ஓய்வு இரத்த அழுத்தம்", "chol": "சேரம் கொழுப்பு அளவு",
                "fbs": "உணவிற்கு பிந்தைய இரத்த சர்க்கரை", "restecg": "ஓய்வு ECG முடிவுகள்", "thalach": "அதிகபட்ச இதய துடிப்பு",
                "exang": "விளையாட்டு நேரத்தில் ஏஞ்சினா", "oldpeak": "ST தாழ்வு மதிப்பு",
                "slope": "ST உரையின் சாய்வு", "ca": "வண்ணமிடப்பட்ட பெரிய இரத்தக் குழாய்கள்", "thal": "தலாசீமியா",
                "options": {"sex": ["0 - ஆண்", "1 - பெண்"]}
            },
            "inputs_diabetes": {
                "name": "நோயாளி பெயர்", "age": "வயது", "sex": "பாலினம்","pregnancies": "கருப்பை நோய்கள்", "glucose": "குளுக்கோஸ்",
                "blood_pressure": "இரத்த அழுத்தம்", "skin_thickness": "தோல் தடிப்பு",
                "insulin": "இன்சுலின்", "bmi": "உடல் குமிழ்வுப் காட்டி", "dpf": "மரபணு செயல்பாடு",
                "options": {"sex": ["0 - ஆண்", "1 - பெண்"]}
            },
            "inputs_parkinsons": {
                "name": "நோயாளி பெயர்", "age": "வயது", "sex": "பாலினம்","fo": "MDVP:Fo(Hz)", "fhi": "MDVP:Fhi(Hz)",
                "flo": "MDVP:Flo(Hz)", "jitter": "MDVP:Jitter(%)", "jitter_abs": "MDVP:Jitter(Abs)",
                "rap": "MDVP:RAP", "ppq": "MDVP:PPQ", "ddp": "Jitter:DDP", "shimmer": "MDVP:Shimmer",
                "shimmer_db": "MDVP:Shimmer(dB)", "apq3": "Shimmer:APQ3", "apq5": "Shimmer:APQ5",
                "apq": "MDVP:APQ", "dda": "Shimmer:DDA", "nhr": "NHR", "hnr": "HNR",
                "rpde": "RPDE", "dfa": "DFA", "spread1": "Spread1", "spread2": "Spread2",
                "d2": "D2", "ppe": "PPE", "options": {"sex": ["0 - ஆண்", "1 - பெண்"]}
            }
        }
    }

# Use selected language translation
translations = get_translations()
T = translations[lang]

# Sidebar Navigation
with st.sidebar:
    st.markdown(T["nav"])
    selection = st.radio(T["goto"], [T["home"], T["heart"], T["diabetes"], T["parkinsons"]])
    st.markdown("---")
    st.markdown(f"### {T['contact']}")
    st.write("jananiviswa05@gmail.com")

# Load Models
try:
    heart_model = pickle.load(open('Saved_Models/heart_disease_model.sav', 'rb'))
    heart_scaler = pickle.load(open('Saved_Models/scaler_heart.sav', 'rb'))
    diabetes_model = pickle.load(open('Saved_Models/diabetes_model.sav', 'rb'))
    diabetes_scaler = pickle.load(open('Saved_Models/scaler_diabetes.sav', 'rb'))
    parkinsons_model = pickle.load(open('Saved_Models/parkinsons_model.sav', 'rb'))
    parkinsons_scaler = pickle.load(open('Saved_Models/scaler_parkinsons.sav', 'rb'))
except FileNotFoundError as e:
    st.error(f"Error loading model files: {e}")
    st.stop()

# Prediction functions
def predict_heart_disease(features):
    arr = heart_scaler.transform([features])
    return heart_model.predict(arr)[0]

def predict_diabetes(features):
    arr = diabetes_scaler.transform([features])
    return diabetes_model.predict(arr)[0]

def predict_parkinsons(features):
    arr = parkinsons_scaler.transform([features])
    return parkinsons_model.predict(arr)[0]

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.fonts_available = False

        # Font paths
        regular_font_path = "Font/NotoSansTamil-Regular.ttf"
        bold_font_path = "Font/NotoSansTamil-Bold.ttf"

        # Font availability check with graceful fallback
        if os.path.exists(regular_font_path) and os.path.exists(bold_font_path):
            try:
                self.add_font("Noto", "", regular_font_path, uni=True)
                self.add_font("Noto", "B", bold_font_path, uni=True)
                self.fonts_available = True
                self.set_font("Noto", "", 12)
            except Exception:
                self.set_font("Arial", "", 12)
        else:
            self.set_font("Arial", "", 12)

    def header(self):
        logo_path = "Images/Logo 1.png"
        if os.path.exists(logo_path):
            self.image(logo_path, x=10, y=8, w=25)
        font_name = "Noto" if self.fonts_available else "Arial"
        self.set_font(font_name, "B", 14)
        self.cell(0, 10, "Health Diagnosis Report", ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        font_name = "Noto" if self.fonts_available else "Arial"
        self.set_font(font_name, "", 9)
        self.cell(0, 10, f"Page {self.page_no()}", align='C')

def sanitize_for_pdf(text):
    """Convert text to latin-1 safe format by removing non-ASCII characters"""
    return text.encode('latin-1', errors='replace').decode('latin-1')

def generate_pdf(name, result, advice, T, inputs_dict):
    pdf = PDF()
    pdf.add_page()

    # Main Title
    font_name = "Noto" if pdf.fonts_available else "Arial"
    pdf.set_font(font_name, "B", 16)
    pdf.cell(0, 10, sanitize_for_pdf(T["title"]), ln=True, align='C')
    pdf.ln(8)

    # Patient Name
    pdf.set_font(font_name, "B", 12)
    pdf.cell(0, 10, f"Patient Name: {sanitize_for_pdf(name)}", ln=True)
    pdf.ln(4)

    # Health Data Table
    pdf.set_font(font_name, "B", 12)
    pdf.cell(0, 10, "Entered Health Data:", ln=True)
    pdf.set_font(font_name, "", 11)

    pdf.set_fill_color(245, 245, 245)
    col_width_label = 70
    col_width_value = 110
    row_height = 8

    for label, value in inputs_dict.items():
        label_text = sanitize_for_pdf(str(label))
        value_text = sanitize_for_pdf(str(value))
        if len(value_text) > 50:
            value_text = value_text[:47] + "..."
        pdf.cell(col_width_label, row_height, label_text, border=1, fill=True)
        pdf.cell(col_width_value, row_height, value_text, border=1, ln=True)

    pdf.ln(6)

    # Prediction Result
    pdf.set_font(font_name, "B", 12)
    pdf.cell(0, 10, sanitize_for_pdf(T["diagnose"]) + ":", ln=True)
    pdf.set_font(font_name, "", 11)
    pdf.multi_cell(0, 8, sanitize_for_pdf(result))
    pdf.ln(4)

    # Advice
    pdf.set_font(font_name, "B", 12)
    pdf.cell(0, 10, sanitize_for_pdf(T["advice"]) + ":", ln=True)
    pdf.set_font(font_name, "", 11)
    pdf.multi_cell(0, 8, sanitize_for_pdf(advice))
    pdf.ln(4)

    # Timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font(font_name, "", 9)
    pdf.cell(0, 10, f"Generated on: {now}", ln=True)

    # Generate PDF with error handling
    try:
        pdf_bytes = pdf.output(dest='S')
        # Ensure pdf_bytes is bytes type
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
        
        b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        return f'<a href="data:application/pdf;base64,{b64}" download="Health_Report.pdf">{sanitize_for_pdf(T["download"])}</a>'
    except (UnicodeEncodeError, TypeError) as e:
        return '<p style="color:red;">PDF generation encountered issues. Please use ASCII characters in patient name.</p>'

if selection == T["home"]:
    st.title(T["title"])
    st.markdown(f"### 👋 {T['welcome']}")
    
    st.markdown(T["about"])
    st.markdown(f"""
    - 🫀 **{T['heart']}**
    - 🩸 **{T['diabetes']}**
    - 🧠 **{T['parkinsons']}**
    """)
    
    st.markdown(T["instructions"])
    st.markdown(T["purpose"])

    st.markdown("----")
    st.markdown(T["disclaimer"])


elif selection == T["heart"]:
    st.header(T["heart"] + " 🫀")
    inputs = T["inputs_heart"]
    
    name = st.text_input(inputs["name"])
    age = st.slider(inputs["age"], 1, 100)
    sex = st.selectbox(inputs["sex"], inputs["options"]["sex"])

    cp = st.selectbox(inputs["cp"], [0, 1, 2, 3])
    trestbps = st.number_input(inputs["trestbps"], 0)
    chol = st.number_input(inputs["chol"], 0)
    fbs = st.selectbox(inputs["fbs"], [0, 1])
    restecg = st.selectbox(inputs["restecg"], [0, 1, 2])
    thalach = st.number_input(inputs["thalach"], 0)
    exang = st.selectbox(inputs["exang"], [0, 1])
    oldpeak = st.number_input(inputs["oldpeak"], 0.0)
    slope = st.selectbox(inputs["slope"], [0, 1, 2])
    ca = st.selectbox(inputs["ca"], [0, 1, 2, 3])
    thal = st.selectbox(inputs["thal"], [1, 2, 3])

    if st.button(T["diagnose"]):
        # Convert 'sex' from string to integer
        sex_value = int(sex.split(" - ")[0])

        features = [
            age, sex_value, cp, trestbps, chol, fbs, restecg,
            thalach, exang, oldpeak, slope, ca, thal
        ]
        result = predict_heart_disease(features)

        pdf_result = (
            f"{T['risk']}: {T['heart']}"
            if result == 1
            else f"{T['no_risk']}: {T['heart']}"
        )
        advice = (
            T["advice_heart_positive"]
            if result == 1
            else T["advice_heart_negative"]
        )

        if result == 1:
            st.error(f"⚠️ {T['risk']} {T['heart']}")
        else:
            st.success(f"✅ {T['no_risk']} {T['heart']}")

        input_summary = {
        inputs["name"]: name,
        inputs["age"]: age,
        inputs["sex"]: sex,
        inputs["cp"]: cp,
        inputs["trestbps"]: trestbps,
        inputs["chol"]: chol,
        inputs["fbs"]: fbs,
        inputs["restecg"]: restecg,
        inputs["thalach"]: thalach,
        inputs["exang"]: exang,
        inputs["oldpeak"]: oldpeak,
        inputs["slope"]: slope,
        inputs["ca"]: ca,
        inputs["thal"]: thal,
        }

        st.markdown(generate_pdf(name, pdf_result, advice, T, input_summary), unsafe_allow_html=True)
        st.info(f"{T['advice']}: {advice}")


elif selection == T["diabetes"]:
    st.header(T["diabetes"] + " 🩸")
    inputs = T["inputs_diabetes"]
    name = st.text_input(inputs["name"])
    age = st.slider(inputs["age"], 1, 100)
    sex = st.selectbox(inputs["sex"], inputs["options"]["sex"])
    pregnancies = st.number_input(inputs["pregnancies"], 0)
    glucose = st.number_input(inputs["glucose"], 0)
    bp = st.number_input(inputs["blood_pressure"], 0)
    skin = st.number_input(inputs["skin_thickness"], 0)
    insulin = st.number_input(inputs["insulin"], 0)
    bmi = st.number_input(inputs["bmi"], 0.0)
    dpf = st.number_input(inputs["dpf"], 0.0)
    if st.button(T["diagnose"]):
        features = [pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]
        result = predict_diabetes(features)
        pdf_result = f"{T['risk']}: {T['diabetes']}" if result == 1 else f"{T['no_risk']}: {T['diabetes']}"
        advice = T["advice_diabetes_positive"] if result == 1 else T["advice_diabetes_negative"]
        if result == 1:
            st.error(f"⚠️ {T['risk']} {T['diabetes']}")
        else:
            st.success(f"✅ {T['no_risk']} {T['diabetes']}")

        input_summary = {
        inputs["name"]: name,
        inputs["age"]: age,
        inputs["sex"]: sex,
        inputs["pregnancies"]: pregnancies,
        inputs["glucose"]: glucose,
        inputs["blood_pressure"]: bp,
        inputs["skin_thickness"]: skin,
        inputs["insulin"]: insulin,
        inputs["bmi"]: bmi,
        inputs["dpf"]: dpf,
        }
        st.markdown(generate_pdf(name, pdf_result, advice, T, input_summary), unsafe_allow_html=True)
        st.info(f"{T['advice']}: {advice}")


elif selection == T["parkinsons"]:
    st.header(T["parkinsons"] + " 🧠")
    inputs = T["inputs_parkinsons"]
    
    name = st.text_input(inputs["name"])
    age = st.slider(inputs["age"], 1, 100)

    # If 'sex' and 'options' are inside, handle them:
    if "sex" in inputs and "options" in inputs:
        sex = st.selectbox(inputs["sex"], inputs["options"]["sex"])
        start_idx = 3  # Skip name, age, sex
    else:
        start_idx = 2  # Skip name, age

    # Get the remaining keys for features
    feature_keys = list(inputs.keys())[start_idx:]

    # Get number inputs for each
    features = []
    for key in feature_keys:
        if isinstance(inputs[key], str):  # Ensure it's a string label
            val = st.number_input(inputs[key], 0.0)
            features.append(val)

    if st.button(T["diagnose"]):
        result = predict_parkinsons(features)
        pdf_result = f"{T['risk']}: {T['parkinsons']}" if result == 1 else f"{T['no_risk']}: {T['parkinsons']}"
        advice = T["advice_parkinsons_positive"] if result == 1 else T["advice_parkinsons_negative"]

        # Prepare input summary
        input_summary = {
            inputs["name"]: name,
            inputs["age"]: age
        }

        if "sex" in inputs:
            input_summary[inputs["sex"]] = sex

        for i in range(len(features)):
            key = feature_keys[i]
            input_summary[inputs[key]] = features[i]
        if result == 1:
            st.error(f"⚠️ {T['risk']} {T['parkinsons']}")
        else:
            st.success(f"✅ {T['no_risk']} {T['parkinsons']}")

        st.markdown(generate_pdf(name, pdf_result, advice, T, input_summary), unsafe_allow_html=True)

        st.info(f"{T['advice']}: {advice}")





