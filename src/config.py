"""
Loads and exports the PiHub configuratation.
"""

import os

filename = os.getenv('PIHUB_CONFIG', 'pihub.config.py')
config = require(os.path.abspath(filename))

def add_web_module(route_module_name):
  config.web_modules.append(route_module_name)

config.add_web_module = add_web_module
config.setdefault = vars(config).setdefault
config.setdefault('components', [])
config.setdefault('web_modules', [])
config.setdefault('build_directory', 'build/src')
config.setdefault('bundle_directory', 'build/bundle')

module.exports = config
