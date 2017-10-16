"""
Default configuration. The namespace of this file is merged into the actual
configuration file.
"""

import os

# ============================================================================
# Installed components configuration
# ============================================================================

components = [
  '@pihub/core:auth',
  '@pihub/core:dashboard',
  '@pihub/core:speedtest'
]

component_hooks = {
}

# ============================================================================
# Server configuration
# ============================================================================

# True if the Flask application should be run with the Werkzeug reloader and
# exceptions should return the traceback in the HTML response.
debug = False

# The port for the HTTP application.
port = 7442

# The hostname to bind the HTTP server to.
host = 'localhost'

# The secret key for user sessions. This should always be overwritten by the
# user using either the PIHUB_SECRET_KEY environment variable or in the user's
# custom PiHub configuration!
# Check out the WordPress secret key generator if you're unsure what to
# put here.
#     https://api.wordpress.org/secret-key/1.1/salt/
secret_key = os.getenv('PIHUB_SECRET_KEY', 'Update This!')

# The PiHub database configuration. Defaults to SQLite in your PiHub
# configuration directory.
database = {
  'provider': 'sqlite',
  'filename': os.path.expanduser('~/.pihub/pihub.sqlite'),
  'create_db': True
}

# Number of worker threads for event processing.
num_event_processors = 10

# ============================================================================
# @pihub/core:auth Component configuration
# ============================================================================

pihub_core_auth = {
  'password': 'welcome'
}
