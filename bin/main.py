"""
Starts the PiHub application.
"""

import app from '../lib/app'
import {install as install_werkzeug_patch} from '../lib/werkzeug-patch'

install_werkzeug_patch()

if require.main == module:
  app.run(debug=True)
