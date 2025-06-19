# CaseMatch SAS Viya Integration

A React dashboard with AI-powered case similarity search using SAS Viya.

## Core Files

### Frontend (React)
- `client/src/components/SimilaritySearch.tsx` - AI similarity search component
- `client/src/pages/dashboard.tsx` - Main dashboard with search tabs
- `client/src/components/CaseCard.tsx` - Case result display cards

### Backend (Flask + SAS)
- `backend/app.py` - Flask API server
- `backend/similarity.py` - SAS Viya connection and similarity calculations
- `backend/config.py` - Configuration management
- `backend/sascfg_personal.py` - SAS OAuth2 authentication setup
- `backend/sas_auth_handler.py` - Authentication handler
- `backend/.env` - Environment variables

## Setup

1. Install dependencies:
   ```bash
   npm install
   cd backend && pip install flask flask-cors saspy pandas numpy scikit-learn
   ```

2. Configure SAS credentials in `backend/.env`

3. Start backend:
   ```bash
   cd backend && python run_local.py
   ```

4. Start frontend:
   ```bash
   npm run dev
   ```

## Features

- Traditional case search with filters
- AI similarity search using SAS Viya topic vectors
- OAuth2 authentication with SAS server
- Cosine similarity calculations on text topics
- Real-time case recommendations

## SAS Integration

Connects to `topic_vectors.sashdat` table in `CASUSER(daodir)` library using OAuth2 authentication to perform similarity calculations on `_TextTopic_1` through `_TextTopic_5` columns.