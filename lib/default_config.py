"""
Default configuration. The namespace of this file is merged into the actual
configuration file.
"""

import os

debug = False
port = 7442
host = 'localhost'
secret_key = os.getenv('PIHUB_SECRET_KEY', 'This Should definitely be replaced with something secure.')

# Configuration of the @pihub/core:auth component.
auth = {
  'password': 'welcome'
}

components = [
  '@pihub/core:auth',
  '@pihub/core:dashboard'
]

component_hooks = {
}
