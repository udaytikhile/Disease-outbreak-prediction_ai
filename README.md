# 🏥 Disease Outbreak Prediction

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-19.2.0-blue?logo=react)
![Flask](https://img.shields.io/badge/Flask-3.0-orange?logo=flask)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)

An AI-powered disease prediction platform built with **React**, **Flask**, and **scikit-learn** to proactively predict and analyze upcoming health risks and potential disease outbreaks based on user-entered clinical data.

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#-features">Features</a></li>
    <li><a href="#-available-models">Available Models</a></li>
    <li><a href="#-tech-stack">Tech Stack</a></li>
    <li><a href="#-project-structure">Project Structure</a></li>
    <li><a href="#-getting-started">Getting Started</a></li>
    <li><a href="#-contributing">Contributing</a></li>
    <li><a href="#-license">License</a></li>
  </ol>
</details>

## ✨ Features

- **Predictive Analytics**: Utilizes various machine learning models to predict multiple diseases.
- **Modern UI**: A sleek, user-friendly interface built with React and styled beautifully.
- **RESTful API**: Standardized backend architecture using Flask, providing scalable model inference capabilities.
- **Easily Extensible**: Designed so new machine learning models can be dropped in easily.

## 🧬 Available Models

- ❤️ **Heart Disease Prediction**
- 🩸 **Diabetes Prediction**
- 🧠 **Parkinson's Disease Prediction**

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, Vite, React Router |
| **Backend** | Flask, Flask-CORS, RESTful APIs |
| **Machine Learning** | scikit-learn, NumPy, Pandas |

## 📁 Project Structure

```text
├── client/          # React + Vite frontend
├── server/          # Flask REST API
├── ml/
│   ├── data/        # Training datasets (CSV)
│   ├── models/      # Trained models (.sav)
│   ├── notebooks/   # Jupyter notebooks for EDA and model training
│   └── scripts/     # Training and evaluation scripts
├── Makefile         # Centralized development commands
└── README.md
```

## 🚀 Getting Started

Follow these steps to set up the project locally on your machine.

### Prerequisites

- [Node.js](https://nodejs.org/) (v16+)
- [Python](https://www.python.org/) (v3.10+)
- `make` utility

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Disease-outbreak-prediction.git
   cd Disease-outbreak-prediction
   ```

2. Install all dependencies for both frontend and backend using Make:
   ```bash
   make install
   ```

### Running the Application

To start both the frontend (**Client**) and the backend (**API server**) simultaneously:
```bash
make dev
```

- **Frontend Application** is now running at: `http://localhost:5173`
- **Backend API Service** is available at: `http://localhost:5001`

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please check out our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
