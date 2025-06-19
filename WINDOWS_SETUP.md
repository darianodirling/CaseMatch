# Windows Setup Guide for CaseMatch

## Quick Fix for Current Error

The `ENOTSUP` error happens due to Windows network binding issues. Here are 3 solutions:

### Solution 1: Use Alternative Port (Recommended)
```powershell
# Set environment and run on port 3000
$env:NODE_ENV="development"; $env:PORT="3000"; npx tsx server-windows.ts
```

### Solution 2: Try Different Host Binding
```powershell
# Run with explicit localhost binding
$env:NODE_ENV="development"; $env:HOST="127.0.0.1"; npx tsx server/index.ts
```

### Solution 3: Use Command Prompt Instead
```cmd
set NODE_ENV=development && set PORT=3000 && npx tsx server-windows.ts
```

## Complete Setup Steps

1. **Install Python Dependencies**:
```powershell
pip install -r python-requirements.txt
```

2. **Install Node Dependencies**:
```powershell
npm install
```

3. **Create Environment File**:
```powershell
# Create backend/.env
@"
CAS_HOST=trck1056928.trc.sas.com
CAS_PORT=5570
CAS_USERNAME=sasboot
CAS_PASSWORD=Orion123
CAS_LIBRARY=casuser
DEVELOPMENT_MODE=false
"@ | Out-File -FilePath "backend\.env" -Encoding utf8
```

4. **Start Application** (choose one):
```powershell
# Option A: Use the Windows-compatible server
$env:NODE_ENV="development"; npx tsx server-windows.ts

# Option B: Try different port
$env:NODE_ENV="development"; $env:PORT="3000"; npx tsx server/index.ts

# Option C: Use Command Prompt
# Open cmd.exe and run:
# set NODE_ENV=development && npx tsx server/index.ts
```

## Verify Setup

1. **Check if server starts**: Look for "serving on port XXXX" message
2. **Test in browser**: http://localhost:3000 (or whatever port it shows)
3. **Test CAS connection**: http://localhost:3000/api/cas-status
4. **Test table access**: http://localhost:3000/api/table-preview

## Common Windows Issues

### Port 5000 Conflicts
- Windows often reserves port 5000 for system services
- Solution: Use port 3000 instead with `$env:PORT="3000"`

### Network Binding Issues
- Some Windows configurations don't support certain socket operations
- Solution: Use the `server-windows.ts` file which has fallback bindings

### PowerShell Environment Variables
- PowerShell syntax: `$env:VARIABLE="value"`
- Command Prompt syntax: `set VARIABLE=value`

### Python Virtual Environment
- Make sure you're in your `.venv` before installing Python packages
- If SWAT installation fails, try: `pip install --upgrade pip` first

## Troubleshooting

If you still get errors:

1. **Check firewall**: Windows Defender might block the server
2. **Try different terminal**: Use Command Prompt instead of PowerShell
3. **Check port availability**: 
   ```powershell
   netstat -an | findstr :5000
   netstat -an | findstr :3000
   ```
4. **Restart terminal**: Close and reopen your terminal as administrator

## Success Indicators

When working correctly, you should see:
- Server startup message with port number
- CAS connection status (may show unavailable without VPN)
- Dashboard loads in browser
- API endpoints respond (even if with empty data without VPN)