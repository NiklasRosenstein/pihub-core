"""
Initializes the PiHub WSGI application.
"""

import {app as application} from '../app'
import config from '../config'
import database from '../database'

config.loader.load_components(config.components)
database.initialize()

[x.init_component() for x in config.loader.components
  if hasattr(x, 'init_component')]


if require.main == module:
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--host')
  parser.add_argument('--port', type=int)
  parser.add_argument('--debug', action='store_true')
  args = parser.parse_args()
  if args.host: config.host = args.host
  if args.port: config.port = args.port
  if args.debug: config.debug = True

  application.run(
    host = getattr(config, 'host', 'localhost'),
    port = getattr(config, 'port', 7442),
    debug = getattr(config, 'debug', False)
  )
