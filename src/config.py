"""
Loads and exports the PiHub configuratation.
"""

import os
import {ComponentLoader} from './component'

filename = os.getenv('PIHUB_CONFIG', 'pihub.config.py')
config = require(os.path.abspath(filename))

config.setdefault = vars(config).setdefault
config.setdefault('host', 'localhost')
config.setdefault('port', 7442)
config.setdefault('debug', False)
config.setdefault('components', [])
config.setdefault('ui_routes', [])
config.setdefault('build_directory', 'build/src')
config.setdefault('bundle_directory', 'build/bundle')
config.setdefault('loader', ComponentLoader())

module.exports = config
