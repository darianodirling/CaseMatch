"""
SASPy configuration file for SAS Viya connection
This file configures the connection to your SAS Viya environment
"""

# SAS Viya configuration
SAS_config_names = ['viya']

SAS_config_options = {
    'lock_down': False,
    'verbose': False,
    'prompt': False
}

viya = {
    'sasurl': 'https://trck1056928.trc.sas.com',
    'client_id': 'dariansclientid',
    'client_secret': 'dariansclientsecret',    
    'username': 'daodir',                   
    'password': 'daodir1',              
    'authentication': 'oauth',
    'context': 'SAS Studio compute context' 
}