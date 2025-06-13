# CaseMatch Flask Backend Integration Guide

## Overview

Your React CaseMatch dashboard now includes a Python Flask backend that provides AI-powered case similarity search using SAS Viya and machine learning.

## What's Been Added

### Backend Structure
```
backend/
├── app.py              # Flask server with API endpoints
├── similarity.py       # SAS Viya integration and similarity logic
├── config.py          # Configuration management
├── requirements.txt   # Python dependencies
├── setup.py          # Automated setup script
├── run.py            # Server startup script
├── .env.example      # Environment configuration template
└── README.md         # Backend documentation
```

### Frontend Integration
- New **AI Similarity** tab in your dashboard
- Tab-based interface to switch between regular search and AI similarity
- SimilaritySearch component that connects to the Flask backend
- Enhanced UI with loading states and error handling

## Quick Start

### 1. Setup Backend Environment
```bash
cd backend
python setup.py
```

### 2. Configure SAS Viya Connection
Edit `backend/.env` with your credentials:
```
SAS_HOST=your-viya-server.com
SAS_USERNAME=your-username
SAS_PASSWORD=your-password
CAS_HOST=your-cas-server.com
```

### 3. Start Both Servers
```bash
# Option 1: Use the development script (starts both React and Flask)
./start-dev.sh

# Option 2: Start manually
# Terminal 1 - Backend
cd backend && python run.py

# Terminal 2 - Frontend  
npm run dev
```

## API Endpoints

### POST /search
Find similar cases using machine learning analysis.

**Request:**
```json
{
  "case_number": "CS10023856",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "case_number": "CS10023856",
  "similar_cases": [
    {
      "case_number": "CS13458729",
      "similarity_score": 0.87,
      "title": "Performance issue description",
      "resolution": "Resolution details",
      "assignment_group": "performance",
      "case_type": "performance",
      "status": "resolved"
    }
  ],
  "total_found": 5
}
```

### GET /test-connection
Verify SAS Viya connectivity.

### GET /health
Backend health check.

## Data Requirements

The backend expects a CAS table named `topic_vectors` in the `casuser` library with:
- `case_number`: Unique case identifier
- `title` or `description`: Case description
- `resolution`: Resolution text
- `assignment_group`, `case_type`, `status`: Metadata fields
- Vector columns starting with `topic_`, `vector_`, or `dim_`

## Usage

1. Navigate to your CaseMatch dashboard at http://localhost:5000
2. Click the **AI Similarity** tab
3. Enter a case number (e.g., CS10023856)
4. View similar cases ranked by machine learning similarity scores
5. Click on any result card to view case details

## Troubleshooting

**Backend Connection Issues:**
- Verify Flask server is running on port 5001
- Check SAS Viya credentials in `.env` file
- Ensure network connectivity to SAS servers

**No Similar Cases Found:**
- Verify the case number exists in your topic_vectors table
- Check CAS table permissions and data availability
- Review backend logs for detailed error messages

**CORS Errors:**
- The backend is pre-configured for development ports
- For production, update CORS settings in `app.py`

## Architecture

The integration follows a clean separation of concerns:

1. **React Frontend**: Handles UI, user interactions, and display
2. **Node.js Express**: Serves static assets and handles basic case data
3. **Python Flask**: Provides AI similarity search via SAS Viya integration
4. **SAS Viya/CAS**: Stores topic vectors and performs similarity calculations

This architecture allows you to leverage both the existing case management system and advanced analytics capabilities.