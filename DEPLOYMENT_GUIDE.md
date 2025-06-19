# CaseMatch SAS Viya Integration - Deployment Guide

## Prerequisites

Your SAS Viya environment needs:
- Access to SAS Viya server: `https://trck1056928.trc.sas.com/`
- Username: `daodir`
- Password: `daodir1`
- CAS table: `topic_vectors` in `casuser(daodir)` library

## Local Setup Instructions

### 1. Install Python Dependencies

```bash
cd backend
pip install flask flask-cors saspy scikit-learn pandas numpy
```

### 2. Configure Environment

The `.env` file is configured with your exact table configuration:
```
SAS_HOST=trck1056928.trc.sas.com
SAS_USERNAME=daodir
SAS_PASSWORD=daodir1
TOPIC_VECTORS_TABLE=topic_vectors.sashdat
TOPIC_VECTORS_CASLIB=CASUSER(daodir)
```

### 3. Test SAS Viya Connection with OAuth2

Your SAS environment uses OAuth2 authentication. Run the OAuth2-aware setup:

```bash
cd backend
python oauth2_setup_guide.py
```

This will create OAuth2-compatible configurations and test authentication. Then run:

```bash
python sas_auth_handler.py
```

Expected output when working:
```
✓ SAS connection successful
✓ SAS session working
```

The integration automatically handles both OAuth2 and username/password authentication methods.

### 4. Start Backend Server

```bash
cd backend
python run_local.py
```

Server will start on: `http://localhost:5001`

### 5. Start Frontend

In a separate terminal:
```bash
npm run dev
```

Frontend available at: `http://localhost:5000`

## Using the AI Similarity Feature

1. Open your CaseMatch dashboard
2. Click the "AI Similarity" tab
3. Enter a case number from your topic_vectors table
4. View similar cases ranked by machine learning similarity scores

## API Testing

Test the backend directly:

```bash
# Health check
curl http://localhost:5001/health

# Test SAS connection
curl http://localhost:5001/test-connection

# Search for similar cases
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"case_number": "CS10023856", "top_k": 5}'
```

## Data Requirements

Your `topic_vectors` table contains:
- `__uniqueid__`: Unique identifier
- `Case Number`: Case identifier for search
- `Description`: Case description text
- `Resolution`: Resolution details
- `Assignment Group`: Case assignment information
- `Concern`: Issue description
- Vector columns: `_TextTopic_1` through `_TextTopic_5` (topic vectors)
- Additional columns: `_Col1_` through `_Col5_` (supplementary vectors)

## Troubleshooting

**Connection Issues:**
- The test failed with "Name or service not known" because this development environment cannot reach your SAS server
- When running locally with network access to `trck1056928.trc.sas.com`, the connection should work
- Verify credentials and ensure SAS Viya server is accessible from your network

**Data Access Issues:**
- Your table `topic_vectors.sashdat` exists in `CASUSER(daodir)` library (confirmed from screenshot)
- Table contains the expected columns: `_TextTopic_1` through `_TextTopic_5`, `Case Number`, `Assignment Group`, etc.
- No changes needed to table structure

**Environment Issues:**
- The test showed numpy import conflicts in this environment
- On your local machine with proper Python setup, dependencies should install cleanly
- Use the production deployment script for clean environment setup

## Production Deployment

For production deployment, use the automated deployment script:

```bash
cd backend
python deploy_production.py
```

This script will:
1. Install all dependencies with proper versions
2. Create production environment configuration
3. Generate systemd service files
4. Create nginx reverse proxy configuration
5. Set up proper logging and monitoring

Manual production steps:
1. Run the deployment script on your production server
2. Copy and enable the systemd service
3. Configure nginx for SSL and reverse proxy
4. Update CORS settings for your production domain
5. Set up log rotation and monitoring

## Architecture Overview

```
React Frontend (Port 5000)
├── Traditional Case Search (existing)
└── AI Similarity Search (new)
    ↓
Flask Backend (Port 5001)
├── /search endpoint
├── SAS Viya integration
└── Cosine similarity calculation
    ↓
SAS Viya Server
├── CAS session
└── topic_vectors table
```

The integration maintains your existing case search functionality while adding AI-powered similarity search through SAS Viya's machine learning capabilities.