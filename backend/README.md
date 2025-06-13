# CaseMatch Flask Backend

This Flask backend provides case similarity search functionality using SAS Viya and CAS integration.

## Features

- **Case Similarity Search**: Find similar cases using cosine similarity on topic vectors
- **SAS Viya Integration**: Connect to SAS Viya and CAS servers using saspy
- **RESTful API**: Clean JSON API endpoints for React frontend integration
- **CORS Support**: Configured for seamless frontend-backend communication

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and update with your SAS Viya credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual SAS Viya connection details:

```
SAS_HOST=your-viya-server.com
SAS_USERNAME=your-username
SAS_PASSWORD=your-password
CAS_HOST=your-cas-server.com
```

### 3. Start the Server

```bash
python run.py
```

The server will start on `http://localhost:5001`

## API Endpoints

### POST /search

Search for similar cases based on a case number.

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
      "title": "User reported intermittent performance lags",
      "resolution": "Confirmed system resources and adjusted configuration",
      "assignment_group": "performance",
      "case_type": "performance",
      "status": "resolved"
    }
  ],
  "total_found": 5
}
```

### GET /test-connection

Test the SAS Viya connection.

**Response:**
```json
{
  "success": true,
  "message": "SAS Viya connection successful"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Flask backend is running"
}
```

## Data Requirements

The backend expects a CAS table named `topic_vectors` in the `casuser` library with the following structure:

- `case_number`: Unique case identifier
- `title` or `description`: Case title/description
- `resolution`: Case resolution text
- `assignment_group`: Assignment group
- `case_type`: Type of case
- `status`: Case status
- Vector columns starting with `topic_`, `vector_`, or `dim_`

## Integration with React Frontend

To integrate with your React frontend, update your API calls to use the Flask backend:

```javascript
// Example API call from React
const searchSimilarCases = async (caseNumber) => {
  const response = await fetch('http://localhost:5001/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      case_number: caseNumber,
      top_k: 5
    })
  });
  
  return await response.json();
};
```

## Troubleshooting

1. **SAS Connection Issues**: Verify your SAS Viya credentials and network connectivity
2. **Missing Table**: Ensure the `topic_vectors` table exists in the `casuser` library
3. **CORS Errors**: The backend is configured for common development ports (3000, 5000, 5173)
4. **Port Conflicts**: Change `FLASK_PORT` in `.env` if port 5001 is in use