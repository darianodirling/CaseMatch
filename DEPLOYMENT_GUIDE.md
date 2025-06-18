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

The `.env` file is already configured with your credentials:
```
SAS_HOST=trck1056928.trc.sas.com
SAS_USERNAME=daodir
SAS_PASSWORD=daodir1
TOPIC_VECTORS_TABLE=topic_vectors
TOPIC_VECTORS_CASLIB=casuser
```

### 3. Test SAS Viya Connection

```bash
cd backend
python test_connection.py
```

Expected output when working:
```
✓ SAS Viya connection successful
✓ Topic vectors loaded successfully
✓ Loaded [N] records from topic_vectors
```

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

Your `topic_vectors` table should contain:
- `case_number`: Unique case identifier
- `title` or `description`: Case description
- `resolution`: Resolution text
- `assignment_group`, `case_type`, `status`: Metadata
- Vector columns (e.g., `topic_1`, `topic_2`, etc.)

## Troubleshooting

**Connection Issues:**
- Verify network access to `trck1056928.trc.sas.com`
- Check credentials in `.env` file
- Ensure SAS Viya server is running

**Data Access Issues:**
- Verify `topic_vectors` table exists in `casuser(daodir)`
- Check table permissions
- Confirm table structure matches expectations

**Performance Issues:**
- Consider limiting vector dimensions for faster similarity calculations
- Implement caching for frequently accessed cases
- Monitor memory usage with large datasets

## Production Deployment

For production deployment:
1. Update CORS settings in `app.py` for your domain
2. Use environment variables instead of `.env` file
3. Configure proper logging and monitoring
4. Consider using a production WSGI server like Gunicorn
5. Implement authentication and authorization as needed

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