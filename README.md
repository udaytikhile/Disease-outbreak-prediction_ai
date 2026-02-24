# Medixa AI — Disease Outbreak & Prediction System 🩺⚡

![React](https://img.shields.io/badge/React-19.0.0-blue?style=for-the-badge&logo=react)
![Vite](https://img.shields.io/badge/Vite-7.3.1-646CFF?style=for-the-badge&logo=vite)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![AI/ML](https://img.shields.io/badge/AI_Powered-Explainable_ML-00C7B7?style=for-the-badge)

Medixa AI is an advanced, AI-powered clinical health screening platform designed to empower early detection through intelligent risk assessment. It features predictive machine learning models for multiple diseases, explainable AI (XAI) via SHAP values, and an LLM-powered interactive symptom checker with emergency triage.

> **Disclaimer:** This tool is designed for **educational and preventive awareness purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment.

---

## ✨ Key Features

- **🧠 Predictive Disease Models**: Accurate risk assessment for **Heart Disease**, **Diabetes**, **Kidney Disease**, and **Depression** using trained ML models.
- **📊 Explainable AI (SHAP)**: Transparent predictions showing exactly which clinical biomarkers (e.g., age, BMI, glucose) contributed to the risk score and by how much.
- **💬 Conversational Symptom Checker**: An interactive, LLM-driven chat interface that analyzes symptoms, asks follow-up questions, and flags potential medical emergencies for immediate triage.
- **📈 Comprehensive Dashboard**: Visual analytics tracking your prediction history, health trends, and most frequently assessed conditions using interactive charts.
- **📄 Medical Reports**: Instantly generate and download detailed PDF clinical reports of your assessment results.
- **🔐 Privacy First**: All prediction history is stored locally in your browser. Encrypted and safe export capabilities (CSV/JSON).
- **🌗 Dark/Light Mode**: Full glassmorphic UI with seamless theme switching for clinical and nighttime use.

---

## 🛠️ Technology Stack

### Frontend (`/client`)
- **Core**: React 19, React Router v7
- **Build Tool**: Vite 7
- **Styling**: Modular Vanilla CSS with CSS Variables & Glassmorphism
- **Performance**: Code-split routing (`React.lazy`), memoized context, and strict WCAG accessibility standards.

### Backend (`/server`)
- **API Engine**: Python (Flask / FastAPI)
- **Machine Learning**: Scikit-Learn, Pandas, NumPy
- **Explainability**: SHAP (SHapley Additive exPlanations)
- **NLP / Chat**: LLM integration for the Symptom Checker

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python 3.10+
- npm or yarn

### 1. Clone the Repository
```bash
git clone https://github.com/udaytikhile/Disease-outbreak-prediction_ai.git
cd Disease-outbreak-prediction_ai
```

### 2. Setup the Backend (Python API)
```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python run.py  # Typically runs on http://localhost:5001
```

### 3. Setup the Frontend (React App)
```bash
cd client
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

---

## 📂 Project Structure

```text
Disease-outbreak-prediction_ai/
├── client/                     # Frontend React SPA
│   ├── public/                 # Static assets & icons
│   └── src/
│       ├── api/                # Isolated API clients (client.js, predictionApi.js)
│       ├── components/         # React Components
│       │   ├── common/         # Navbar, ErrorBoundary, Inputs, Toasts
│       │   ├── dashboard/      # Analytics, Charts, History tables
│       │   ├── pages/          # Home, Profile, 404
│       │   ├── prediction/     # Disease forms (Heart, Diabetes, etc.) & Result cards
│       │   └── symptom-checker/# LLM Chat interface
│       ├── context/            # React Context (PredictionContext)
│       ├── hooks/              # Custom hooks (usePredictionHistory)
│       └── styles/             # Modular CSS architecture
│
├── server/                     # Backend API & ML Models
│   ├── models/                 # Pre-trained .pkl models
│   ├── routes/                 # API endpoint handlers
│   └── ...
│
└── run.sh                      # Helper script to launch the full stack
```

---

## 🛡️ Security & Performance
- **Code Splitting**: The frontend utilizes dynamic imports, heavily reducing initial bundle size.
- **Accessible Design**: Complies with comprehensive WCAG standards (Contrast, Screen Reader ARIA labels, Keyboard navigation).
- **API Safety**: Unified HTTP client with mandatory timeout aborts and strict response validation.

---

## 👨‍💻 Author

**Uday Tikhile**
- [GitHub](https://github.com/udaytikhile)
- [LinkedIn](https://www.linkedin.com/in/uday-tikhile-b63159374)

---

*Made with ❤️ for better health awareness.*
