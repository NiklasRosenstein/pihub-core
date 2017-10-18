"""
Default configuration. The namespace of this file is merged into the actual
configuration file.
"""

from apscheduler.triggers.date import DateTrigger as date
from apscheduler.triggers.cron import CronTrigger as cron
from apscheduler.triggers.interval import IntervalTrigger as interval

import os
import uuid

# ============================================================================
# Installed components configuration
# ============================================================================

components = [
  '@pihub/core:auth',
  '@pihub/core:dashboard',
  '@pihub/core:speedtest',
  '@pihub/core:rss_feeds'
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

# The secret key for user sessions. If PIHUB_SECRET_KEY is not set, a UUID
# is automatically generated for the secret key. Note that this will change
# the secret key with every start, thus session information is no retained
# during a restart of the application.
secret_key = os.getenv('PIHUB_SECRET_KEY', str(uuid.uuid4()))

# The PiHub database configuration. Defaults to SQLite in your PiHub
# configuration directory.
database = {
  'provider': 'sqlite',
  'filename': os.path.expanduser('~/.pihub/pihub.sqlite'),
  'create_db': True
}

# Number of worker threads for event processing.
num_event_processors = 10

# User timezone information.
timezone = 'Europe/Berlin'

# ============================================================================
# @pihub/core:auth Component configuration
# ============================================================================

pihub_core_auth = {
  'password': 'welcome'
}
