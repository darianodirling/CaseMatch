# Local Development Setup

## 1. Install Python Dependencies
```bash
pip install swat pandas python-dotenv flask flask-cors numpy scikit-learn requests
```

## 2. Install Node.js Dependencies
```bash
npm install
```

## 3. Configure Environment Variables
Create `backend/.env` file:
```bash
# CAS Server Configuration
CAS_HOST=trck1056928.trc.sas.com
CAS_PORT=5570
CAS_USERNAME=sasboot
CAS_PASSWORD=Orion123
CAS_LIBRARY=casuser

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=true
DEVELOPMENT_MODE=false

# Topic Vectors Table
TOPIC_VECTORS_TABLE=topic_vectors
TOPIC_VECTORS_CASLIB=casuser
```

## 4. Start the Application
```bash
# Start the full-stack application
npm run dev
```

## 5. Verify CAS Connectivity
Open browser and test:
- Main app: http://localhost:5000
- CAS status: http://localhost:5000/api/cas-status
- Table preview: http://localhost:5000/api/table-preview

## Troubleshooting

### SWAT Package Issues
If you get import errors:
```bash
pip uninstall swat
pip install swat
```

### Network Connectivity
Ensure your VPN is connected and you can reach:
```bash
telnet trck1056928.trc.sas.com 5570
```

### Authentication
Verify your sasboot credentials are current and have access to the casuser library.

## Development Commands
```bash
# Start development server
npm run dev

# Run Python CAS tests
cd backend && python cas_service.py

# Test specific endpoints
curl http://localhost:5000/api/cas-status
curl http://localhost:5000/api/table-preview
```