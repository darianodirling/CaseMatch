# CaseMatch Deployment Guide

## Overview
CaseMatch is a React-based SAS case search dashboard with AI-powered similarity search using your SAS Viya server at trck1056928.trc.sas.com.

## Architecture
- **Frontend**: React with TypeScript, TailwindCSS, shadcn/ui components
- **Backend**: Node.js with Express, Python CAS integration
- **Database**: SAS Viya CAS (topic_vectors table in casuser library)
- **Authentication**: SAS Viya with sasboot credentials

## SAS Server Configuration
```
Host: trck1056928.trc.sas.com
Port: 5570
Protocol: CAS
Username: sasboot
Password: Orion123
Library: casuser
Table: topic_vectors
```

## Required Environment Variables
```bash
# CAS Server Configuration
CAS_HOST=trck1056928.trc.sas.com
CAS_PORT=5570
CAS_USERNAME=sasboot
CAS_PASSWORD=Orion123
CAS_LIBRARY=casuser

# Application Configuration
NODE_ENV=production
PORT=5000
```

## Deployment Options

### Option 1: Local Development with VPN Access
1. **Prerequisites**:
   - VPN connection to access trck1056928.trc.sas.com
   - Python 3.8+ with pip
   - Node.js 18+ with npm

2. **Setup**:
   ```bash
   # Install Python dependencies
   pip install swat pandas python-dotenv

   # Install Node.js dependencies
   npm install

   # Configure environment
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings

   # Start application
   npm run dev
   ```

3. **Verification**:
   - Access http://localhost:5000
   - Test CAS connection: GET /api/cas-status
   - Test table access: GET /api/table-preview
   - Test similarity search: POST /api/search-similar

### Option 2: Hybrid Deployment (Recommended)
1. **Frontend**: Deploy on Replit for public access
2. **Backend**: Run locally with VPN access for CAS connectivity
3. **Configuration**: Update frontend API base URL to point to local backend

### Option 3: Enterprise Deployment
1. **Server Requirements**:
   - Network access to trck1056928.trc.sas.com:5570
   - Python 3.8+ with SWAT package
   - Node.js 18+ runtime

2. **Installation**:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd casematch

   # Install dependencies
   pip install -r requirements.txt
   npm install

   # Configure environment variables
   export CAS_HOST=trck1056928.trc.sas.com
   export CAS_PORT=5570
   export CAS_USERNAME=sasboot
   export CAS_PASSWORD=Orion123

   # Start production server
   npm run build
   npm start
   ```

## API Endpoints

### CAS Connectivity
- `GET /api/cas-status` - Test connection to your SAS server
- `GET /api/table-preview` - Load sample data from topic_vectors table
- `POST /api/search-similar` - Find similar cases using topic vectors

### Case Management
- `GET /api/cases` - Get all cases
- `GET /api/cases/search?q=<query>` - Search cases by keyword
- `GET /api/cases/filter` - Filter cases by assignment group, type, status

## Data Structure

### topic_vectors Table Schema
```
Case Number: string          - Unique case identifier
Description: string          - Case description/title
Resolution: string           - Case resolution details
Assignment Group: string     - Responsible team
Concern: string             - Case type/category
_TextTopic_1: float         - Topic vector component 1
_TextTopic_2: float         - Topic vector component 2
_TextTopic_3: float         - Topic vector component 3
_TextTopic_4: float         - Topic vector component 4
_TextTopic_5: float         - Topic vector component 5
```

### Similarity Search Algorithm
1. **Input**: Target case number
2. **Process**: 
   - Extract topic vector for target case
   - Calculate cosine similarity with all other cases
   - Rank by similarity score
3. **Output**: Top K most similar cases with scores

## Security Considerations
- SAS credentials are configured in environment variables
- VPN access required for production connectivity
- HTTPS recommended for production deployment
- Consider implementing SAS OAuth2 for enhanced security

## Troubleshooting

### Common Issues
1. **SWAT Import Error**: Install swat package with `pip install swat`
2. **Connection Timeout**: Verify VPN access to trck1056928.trc.sas.com
3. **Authentication Failed**: Confirm sasboot credentials are current
4. **Table Not Found**: Verify topic_vectors exists in casuser library

### Development Mode
- Application works with mock data when CAS server unavailable
- Full functionality requires network access to your SAS server
- Test endpoints return appropriate error messages when offline

## Performance Optimization
- Topic vector calculations limited to 100 cases for performance
- Connection pooling implemented for CAS sessions
- Caching recommended for production deployment
- Consider CAS analytics procedures for large-scale similarity searches

## Monitoring
- Check `/api/cas-status` for server connectivity
- Monitor CAS session usage
- Log similarity search performance metrics
- Track case search patterns and usage

## Next Steps
1. Deploy frontend to Replit for public access
2. Configure backend on server with VPN access
3. Test complete workflow with authentic data
4. Implement additional SAS analytics features
5. Consider OAuth2 integration for enhanced security