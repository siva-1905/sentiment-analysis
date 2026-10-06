# Sentiment Analysis Management System

## Overview
A full-stack web app where users log in, type or upload movie reviews, and get a sentiment (Positive / Negative / Neutral) with a confidence score. Users get history, a dashboard and downloadable reports. Admins manage users and see system statistics and audit logs.

## Features
- Register / login / logout with secure cookie sessions
- Role-based access control (user, admin) enforced by the Flask API
- Sentiment prediction (TF-IDF + Logistic Regression), Neutral when confidence < 60%
- Prediction history (view/delete own results)
- CSV / Excel upload with bulk prediction
- CSV, Excel and PDF reports
- Dashboard (personal for users, system-wide for admins)
- Admin: add / edit / delete users, activate / deactivate, change roles, audit logs

## Architecture
```
React (Vite)  --Axios/JSON + cookie-->  Flask REST API
                                         |-- SQLAlchemy -> SQLite (PostgreSQL in production)
                                         |-- predictor.py -> saved TF-IDF + Logistic Regression
```
React only shows screens. It never touches the database and contains no ML. All rules (login, roles, validation, prediction) live in Flask.

## Technology Stack
React 18, React Router, Axios, Vite | Flask, Flask-SQLAlchemy, Flask-Login, Flask-CORS, Werkzeug | scikit-learn, NLTK, pandas, joblib | openpyxl, reportlab | pytest, gunicorn.

## Machine Learning Pipeline
`backend/ml/train_model.py` (run once, offline):
1. Load `IMDB Dataset.csv` (columns `review`, `sentiment`; 50,000 rows)
2. Clean text: lowercase, remove HTML, keep letters only, tokenize, remove stopwords, lemmatize, join
3. 80/20 stratified train/test split
4. TF-IDF (30,000 features, unigrams + bigrams)
5. Logistic Regression
6. Print accuracy, precision, recall, F1, confusion matrix
7. Save `sentiment_model.pkl` and `vectorizer.pkl` with joblib into `backend/ml/models/`

Flask only **loads** these files (lazily, on the first prediction). It never trains. Prediction: `predict_proba` max value = confidence; below 0.60 the label becomes Neutral.

## Database Design
| Table | Columns |
|---|---|
| users | id, name, email (unique), password (hash), role, status, created_at |
| sentiment_results | id, user_id (FK), text, sentiment, confidence_score, prediction_date |
| audit_logs | id, user_id (FK, nullable), action, description, timestamp |

A user has many results (deleted with the user) and many audit logs (kept, `user_id` becomes NULL if the user is deleted). Tables are created automatically on startup (`db.create_all()`); no SQL needed.

## API Documentation
All responses are JSON. Errors look like `{"message": "..."}`.

| Method | Endpoint | Access | Notes |
|---|---|---|---|
| POST | /api/auth/register | public | `{name,email,password}` -> 201 / 400 / 409 |
| POST | /api/auth/login | public | 200 / 401 / 403 (disabled) |
| POST | /api/auth/logout | login | |
| GET | /api/auth/me | login | current user |
| POST | /api/sentiment/predict | login | `{text}` -> `{id,sentiment,confidence}` |
| GET | /api/sentiment/history | login | own results |
| GET | /api/sentiment/history/<id> | login | own result only (else 404) |
| DELETE | /api/sentiment/history/<id> | login | own result only (else 404) |
| POST | /api/sentiment/upload | login | multipart field `file` (.csv/.xlsx/.xls) |
| GET | /api/dashboard | login | `{total,positive,negative,neutral}` (admin: system-wide + `users`) |
| GET | /api/reports/csv, /excel, /pdf | login | own data (admin: all data) |
| GET/POST | /api/admin/users | admin | list / create |
| PUT/DELETE | /api/admin/users/<id> | admin | edit / delete |
| PATCH | /api/admin/users/<id>/status | admin | `{status: active\|disabled}` |
| PATCH | /api/admin/users/<id>/role | admin | `{role: user\|admin}` |
| GET | /api/admin/audit-logs | admin | `?limit=200` |
| GET | /api/health | public | health check |

## Authentication
Flask-Login stores the user id in a signed, HTTP-only session cookie. Axios is created with `withCredentials: true`, and Flask-CORS uses `supports_credentials=True` with an explicit origin list (never `*`). Passwords are hashed with Werkzeug. A disabled user is logged out on their next request. New accounts always get role `user`; the role cannot be chosen at registration.

## Role-Based Access Control
- `@login_required` protects user endpoints (401 if not logged in).
- `@admin_required` (in `extensions.py`) protects every `/api/admin/*` endpoint (401 if not logged in, **403** if not admin).
- React's `ProtectedRoute` / `AdminRoute` only hide pages for a nicer experience; the API is the real protection.
- Admins cannot delete, deactivate or demote themselves (prevents locking yourself out).

## Project Structure
```
sentiment-analysis/
  backend/   app.py config.py extensions.py models.py requirements.txt .env.example conftest.py
             routes/ (auth, sentiment, dashboard, admin, reports)
             services/ (predictor, report_service, audit_service)
             ml/ (train_model.py, preprocess.py, models/*.pkl)
             tests/test_api.py
  frontend/  package.json vite.config.js index.html src/(App, pages, components, services/api.js)
  postman/   Sentiment-Analysis.postman_collection.json, sample_reviews.csv
```

## Installation
Requirements: Python 3.10+, Node.js 18+. Download **IMDB Dataset.csv** (Kaggle: "IMDB Dataset of 50K Movie Reviews") and place it at `backend/ml/IMDB Dataset.csv`.

## Backend Setup
```bash
cd backend
python -m venv venv
# Windows:  venv\Scripts\activate        macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader stopwords wordnet
cp .env.example .env          # Windows: copy .env.example .env
```
Edit `.env`: set `SECRET_KEY` to a long random string (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`) and set `ADMIN_EMAIL` / `ADMIN_PASSWORD` (the first admin is created from these on startup).

Train the model once (takes a few minutes):
```bash
python ml/train_model.py
```
Run the tests (no trained model needed, the predictor is mocked):
```bash
python -m pytest
```

## Frontend Setup
```bash
cd frontend
cp .env.example .env          # Windows: copy .env.example .env
npm install
```

## Running the Application
```bash
# terminal 1
cd backend && python app.py            # http://127.0.0.1:5000
# terminal 2
cd frontend && npm run dev             # http://127.0.0.1:5173
```
Open **http://127.0.0.1:5173** (use `127.0.0.1` for both apps, not `localhost`, so the cookie is sent). Log in with your admin credentials, or register a normal user.

## Postman Testing
Import `postman/Sentiment-Analysis.postman_collection.json`. The `base_url` variable is `http://127.0.0.1:5000/api`. Postman keeps cookies automatically, so run Register -> Login -> other requests in order. For the upload request, select `postman/sample_reviews.csv` in the form-data `file` field. Run Logout, then "12a Login (admin)" (edit credentials to match your `.env`) for the admin requests. Try an admin request while logged in as a normal user to see the 403.

## Building for Production
```bash
cd frontend
npm run build      # output in frontend/dist
```

## Deployment
**Backend (Render or Railway)**: root directory `backend`, build command `pip install -r requirements.txt && python -m nltk.downloader stopwords wordnet`, start command `gunicorn "app:create_app()"`. Commit the `.pkl` files (or train during build). Environment variables:
`FLASK_ENV=production`, `SECRET_KEY` (random), `FRONTEND_URL` (your Vercel/Netlify URL, no trailing slash), `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `DATABASE_URL`.
In production the cookie is `Secure` + `SameSite=None` so it works across the two domains (needs HTTPS, which both hosts provide).

**Database**: SQLite is fine locally, but free hosting disks are usually temporary, so data would be lost on redeploy. Create a PostgreSQL database on the host and set `DATABASE_URL` to its URL (`postgres://...` is converted automatically; `psycopg2-binary` is already in requirements). No code changes needed. Use a single gunicorn worker on first start so two workers don't create tables at the same moment.

**Frontend (Vercel or Netlify)**: root directory `frontend`, build `npm run build`, output `dist`, environment variable `VITE_API_URL=https://your-backend.onrender.com/api`. `vercel.json` and `public/_redirects` make React Router work on refresh.

## Security Notes
Implemented: hashed passwords, HTTP-only session cookie, role checks on the server, input validation, upload validation (extension, 5 MB limit, parsed in memory only, never executed or saved), spreadsheet formula-injection protection in reports, explicit CORS origins, secrets from environment variables, debug off unless `FLASK_DEBUG=1`, no passwords in responses.
Not included (fine for a portfolio project, worth mentioning): rate limiting / login throttling, CSRF tokens (cookie + JSON only API; `SameSite=None` in production makes a CSRF token a good next step), email verification, password reset, database migrations (Flask-Migrate).

## Interview Explanation
- **What it does**: users submit reviews, the server predicts sentiment, results are stored and reported.
- **Why Flask handles everything**: the browser can't be trusted, so login, roles and ML run on the server; React just calls the API.
- **How login works**: password is checked against a hash, Flask sets a signed session cookie, the browser sends it back on each request (`withCredentials`).
- **How admin protection works**: a decorator checks `current_user.role` and returns 403; hiding links in React is only cosmetic.
- **ML**: clean text, TF-IDF turns words into weighted numbers, Logistic Regression outputs probabilities. If the top probability is under 60% I call it Neutral. Training is offline; the app loads the saved files.
- **Trade-offs**: SQLite for simplicity, PostgreSQL for production; no JWT because cookies sessions are simpler for a single web client; the model is bag-of-words so it can miss sarcasm and negation.
