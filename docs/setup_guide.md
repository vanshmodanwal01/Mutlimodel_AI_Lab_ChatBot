# MindBridge AI: Local Setup & Execution Guide

## 1. Prerequisites

- **Python**: 3.10+ (tested on Python 3.13)
- **MySQL**: 8.0+ (Optional: automatic SQLite fallback is enabled by default for zero-configuration testing)
- **Git**

---

## 2. Installation

1. **Clone or Navigate to the Project Root**:
   ```bash
   cd mini_pro_AI_lab
   ```

2. **Create and Activate a Virtual Environment (Recommended)**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

---

## 3. Environment Configuration

Copy the example configuration file:
```bash
cp .env.example .env
```

Open `.env` and set your configuration parameters:
- `GEMINI_API_KEY`: Obtain your free Gemini API key from [Google AI Studio](https://aistudio.google.com/).
- `DATABASE_URL`: Primary MySQL connection URL:
  ```env
  DATABASE_URL=mysql+pymysql://root:password@localhost:3306/mindbridge_db
  DB_AUTO_FALLBACK_SQLITE=true
  ```
  *(Note: If local MySQL is not running, the application will automatically initialize local SQLite storage at `mindbridge.db`).*

---

## 4. MySQL Database Setup (Optional)

If running MySQL locally:
```bash
mysql -u root -p < database/schema.sql
```

---

## 5. Running the Application

### Option A: Using the All-in-One CLI Launcher
```bash
# Terminal 1: Start FastAPI REST Backend (port 8000)
python app.py backend

# Terminal 2: Start Streamlit Frontend UI (port 8501)
python app.py frontend
```

### Option B: Using Native Tool Commands
```bash
# Backend:
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Frontend:
streamlit run frontend/app.py --server.port 8501
```

Once both servers are running, access the user interface at:
**`http://localhost:8501`**

FastAPI interactive OpenAPI documentation is available at:
**`http://localhost:8000/docs`**

---

## 6. Running Automated Tests

Execute the complete automated test suite (covering unit tests, RAG, safety, crisis intervention, and multimodal processing):
```bash
python app.py test
# or
pytest backend/tests/ -v
```
