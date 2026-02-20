# 🏥 Disease Outbreak Prediction

AI-powered disease prediction platform built with **React** + **Flask** + **scikit-learn**.

## Quick Start

```bash
make install   # Install all dependencies
make dev       # Start both servers
```

- **Frontend** → http://localhost:5173
- **Backend API** → http://localhost:5001

## Project Structure

```
├── client/          # React + Vite frontend
├── server/          # Flask REST API
├── ml/
│   ├── data/        # Training datasets (CSV)
│   ├── models/      # Trained models (.sav)
│   ├── notebooks/   # Jupyter notebooks
│   └── scripts/     # Training scripts
├── Makefile         # Dev commands
└── .gitignore
```

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React 19, Vite 7 |
| Backend | Flask 3, Flask-CORS |
| ML | scikit-learn, NumPy, Pandas |

## Available Models

- ❤️ Heart Disease Prediction
- 🩸 Diabetes Prediction
- 🧠 Parkinson's Disease Prediction

## License

MIT
