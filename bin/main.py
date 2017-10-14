"""
Starts the PiHub application.
"""

import argparse
import {Application} from '../lib/app'
import {install as install_werkzeug_patch} from '../lib/werkzeug-patch'
import {load_component} from '../lib/component'
import os

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='Filename to load the '
  'configuration from. Defaults to ~/.pihub/config.py')
parser.add_argument('--debug', help='Run PiHub in debug mode. '
  'Heightens the logging level and runs the Flask application with the '
  'Werkzeug reloader enabled.', action='store_true')
parser.add_argument('-P', '--port', help='The port to have the webserver '
  'listen to. Defaults to 7442')
parser.add_argument('-H', '--host', help='The hostname to bind the server '
  'to. Defaults to localhost')


def main(argv=None):
  args = parser.parse_args(argv)
  if not args.config:
    args.config = os.path.expanduser('~/.pihub/config.py')

  # Load the configuration.
  default_config = require('../lib/default_config', exports=False)
  if os.path.isfile(args.config):
    config = require.resolve(os.path.abspath(args.config))
    config.init()
    vars(config.namespace).update({
      k: v for k, v in vars(default_config.namespace).items()
      if k not in vars(config.namespace)
    })
    require.context.load_module(config, do_init=False)
    config = config.namespace
  else:
    config = default_config.namespace

  # Update the configuration from the command-line args.
  if args.debug:
    config.debug = args.debug
  if args.port:
    config.port = args.port
  if args.host:
    config.host = args.host

  app = Application(config)

  # Load configured components.
  for comp in config.components:
    app.components.append(load_component(comp))

  install_werkzeug_patch()
  app.init_components()
  app.flask.run(host=config.host, port=config.port, debug=config.debug)


if require.main == module:
  main()
