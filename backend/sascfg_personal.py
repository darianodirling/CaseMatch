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
    'url': 'https://trck1056928.trc.sas.com',
    'context': 'SAS Studio compute context',
    'user': 'daodir',
    'pw': 'daodir1',
    'options': ['-fullstimer']
}