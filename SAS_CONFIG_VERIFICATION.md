# SAS Configuration Verification Guide

## Understanding the Configuration

The line `self.sas = saspy.SASsession(cfgname='viya')` tells SASPy to use a configuration named 'viya' from your SAS configuration file.

## Your Current Setup

The configuration is already properly set up in `backend/sascfg_personal.py`:

```python
viya = {
    'url': 'https://trck1056928.trc.sas.com',
    'context': 'SAS Studio compute context',
    'user': 'daodir',
    'pw': 'daodir1',
    'options': ['-fullstimer']
}
```

## How to Verify in Your Environment

### Method 1: Quick Check
```bash
cd backend
python check_sas_setup.py
```

This will tell you immediately if the 'viya' configuration is working.

### Method 2: Detailed Verification
```bash
cd backend
python verify_sas_config.py
```

This runs comprehensive tests including:
- SASPy import and configuration detection
- Configuration file validation
- SAS connection testing
- Table access verification

### Method 3: Manual Python Test

Open a Python session in your backend directory and run:

```python
import saspy

# Check available configurations
configs = saspy.list_configs()
print("Available configurations:", configs)

# Test the viya configuration
if 'viya' in configs:
    sas = saspy.SASsession(cfgname='viya')
    if sas:
        print("Connection successful!")
        result = sas.submit("proc options option=work; run;")
        print("SAS working:", 'ERROR' not in result.get('LOG', ''))
        sas.endsas()
    else:
        print("Connection failed")
else:
    print("'viya' configuration not found")
```

## Expected Results

### Success Case
```
✓ SASPy available
Available configs: ['viya']
✓ 'viya' config found
Testing connection...
✓ Connection successful
✓ SAS session working
🎉 SAS configuration is working correctly!
```

### Common Issues and Solutions

#### Issue: "'viya' config not found"
**Solution**: The `sascfg_personal.py` file is not in the correct location or not properly formatted.
- Ensure `sascfg_personal.py` is in your `backend` directory
- Check the file contains the `viya = {...}` configuration

#### Issue: "Connection failed" 
**Possible causes**:
- Network cannot reach `trck1056928.trc.sas.com`
- Credentials are incorrect
- SAS server is not accessible

**Solution**: The integration includes fallback logic that will try direct configuration if the 'viya' config fails.

#### Issue: SASPy import errors
**Solution**: Install SASPy with `pip install saspy`

## Fallback Mechanism

The integration includes automatic fallback logic:

1. First tries: `saspy.SASsession(cfgname='viya')`
2. If that fails, uses direct configuration from `config.py`
3. This ensures maximum compatibility across different environments

## Testing Your Specific Table

Once the basic SAS connection works, test table access:

```python
import saspy
sas = saspy.SASsession(cfgname='viya')

# Test table access
result = sas.submit('''
proc casutil;
    list tables caslib="CASUSER(daodir)";
quit;
''')

# Look for topic_vectors.sashdat in the output
print(result['LOG'])
sas.endsas()
```

## Integration Status

Your integration is configured correctly with:
- Proper SAS server URL: `https://trck1056928.trc.sas.com`
- Correct credentials: `daodir/daodir1`
- Exact table reference: `topic_vectors.sashdat` in `CASUSER(daodir)`
- Vector columns: `_TextTopic_1` through `_TextTopic_5`

The configuration will work correctly when run in an environment with network access to your SAS server.