# 🏥 ArogyaMitra 

**ArogyaMitra** is an AI-powered healthcare assistant designed to help primary healthcare workers predict diseases based on symptoms and generate detailed diagnostic reports. This project features a machine learning model deployed as a FastAPI service and a Node.js backend.

---

## 🚀 Machine Learning Model (ML-Model)

The core of the project is a disease prediction model trained on a dataset of symptoms and diseases. It uses **Random Forest** and **XGBoost** for high accuracy and **LIME** for explainability.

### 🔹 Features
- **Disease Prediction**: Predicts one of 41 diseases based on symptoms.
- **Explainable AI (LIME)**: Explains *why* a prediction was made (which symptoms contributed positively/negatively).
- **PDF Reports**: Generates a professional, downloadable PDF report with patient info, diagnosis, and precautions.
- **REST API**: fastAPI endpoints for easy integration.

### 🛠️ Tech Stack
- **Framework**: FastAPI, Uvicorn
- **ML Libraries**: Scikit-learn, XGBoost, Pandas, NumPy
- **Explainability**: LIME
- **PDF Generation**: ReportLab
- **Deployment**: Docker, Hugging Face Spaces

### 📦 Local Setup

1.  **Navigate to the ML directory:**
    ```bash
    cd ML-Model
    ```

2.  **Create details regarding Environment:**
    The project uses Python virtual environments with pip for dependency management, but standard `uv` works too.
    ```bash
    # Create virtual environment
    python -m venv .venv

    # Activate virtual environment (Windows)
    .venv\Scripts\activate

    # Activate virtual environment (Mac/Linux)
    source .venv/bin/activate

    # Upgrade pip (recommended)
    python -m pip install --upgrade pip

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Run the Jupyter Notebook (Optional - for training):**
    If you want to re-train the model:
    ```bash
    jupyter notebook notebook/disease_prediction.ipynb
    ```
    Run all cells to generate the model artifacts in `ML-Model/model/`.

4.  **Start the API Server:**
    ```bash
    uvicorn app:app --reload --port 8000
    ```
    The API will be available at `http://localhost:8000`.
    - **Swagger UI**: `http://localhost:8000/docs`

### 🌐 Deployment (Hugging Face)

The model is deployed on **Hugging Face Spaces** for free, 24/7 access.

-   **Live API**: `https://dashayush-arogyamitra-api.hf.space`
-   **Model Artifacts**: Hosted on [Hugging Face Hub](https://huggingface.co/DashAyush/arogyamitra-model) to keep the Git repo light.

#### **How to Deploy (For New Contributors)**

1.  **Model Upload**: The large `.pkl` files (model, training data) are **NOT** in this GitHub repo. They are uploaded to Hugging Face Hub.
    -   Create a model repo on HF (e.g., `your-username/arogyamitra-model`).
    -   Upload the contents of `ML-Model/model/` using `huggingface-cli` or Python script.

2.  **FastAPI Deployment**:
    -   Create a **Docker Space** on Hugging Face.
    -   The `Dockerfile` and `app.py` are set up to automatically download the model files from HF Hub on startup.
    -   Push the `ML-Model` code to the Space.

---

## 🔙 Backend (Node.js)

The backend handles user authentication, patient data management, and connects to the ML service.

### 🛠️ Tech Stack
- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: MongoDB (Mongoose)
- **Auth**: JWT, Bcrypt

### 📦 Local Setup

1.  **Navigate to the Backend directory:**
    ```bash
    cd Backend
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Environment:**
    -   Create a `.env` file based on `.env.example`.
    -   Add your MongoDB URI and other secrets.

4.  **Start the Server:**
    ```bash
    npm start
    # or for development
    npm run dev
    ```

---

## 📂 Project Structure

```
Techathon-3.0/
├── Backend/                 # Node.js Express Backend
│   ├── src/                 # Source code (controllers, routes, models)
│   ├── package.json         # Dependencies
│   └── ...
├── ML-Model/                # Machine Learning Service
│   ├── app.py               # FastAPI Server (Prediction & PDF generation)
│   ├── Dockerfile           # Deployment config for HF Spaces
│   ├── requirements.txt     # Python dependencies
│   ├── model/               # (Gitignored) Model artifacts are downloaded from HF Hub
│   ├── dataset/             # (Gitignored) CSV datasets
│   └── notebook/            # Jupyter notebook for training
├── Frontend/                # Frontend Application (In development)
└── README.md                # Project Documentation
```

---

## 🔗 API Endpoints (ML Service)

### `POST /predict`
Returns a JSON prediction with confidence score and LIME explanation.

**Body:**
```json
{
  "symptoms": ["fever", "headache", "chills"],
  "patientName": "Rahul"
}
```

### `POST /predict/pdf`
Returns a downloadable PDF report.

**Body:** Same as `/predict`.

---

**Built with ❤️ for Techathon 3.0**
