"""
Starts the PiHub application.
"""

__version__ = module.package.payload['version']

import argparse
import code
import {Application} from '../lib/app'
import {load_component} from '../lib/component'
import {install as install_werkzeug_patch} from 'werkzeug-reloader-patch'
import db from '../lib/database'
import {migrate} from '../lib/database/migrate'
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
parser.add_argument('--upgrade', help='Upgrade any outdated database '
  'schemas and exit.', action='store_true')
parser.add_argument('--dbshell', help='Enter an interactive shell with '
  'access to the Pony ORM database object.', action='store_true')


def main(argv=None):
  args = parser.parse_args(argv)
  if not args.config:
    args.config = os.path.expanduser('~/.pihub/config.py')

  conf_dir = os.path.expanduser('~/.pihub')
  if not os.path.exists(conf_dir):
    print('note: creating empty configuration directory ~/.pihub')
    os.makedirs(conf_dir)

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
  for comp in config.components:
    app.components.append(load_component(comp, config.component_hooks))
  db.db.bind(**config.database)
  db.db.generate_mapping(create_tables=True)

  if args.dbshell:
    with db.session():
      code.interact('PiHub {} DB Shell'.format(__version__), local={'db': db.db})
    return 0
  if args.upgrade:
    app.upgrade_database_revisions()
    return 0
  if not app.check_database_revisions():
    print('fatal: some database schemas are not up to date.')
    print('       try using the pihub --upgrade command.')
    return 1

  if not config.debug or os.getenv('WERKZEUG_RUN_MAIN', '') == 'true':
    # We don't want to run the job scheduler twice, really.
    app.scheduler.start()
    app.init_components()

  install_werkzeug_patch()
  app.flask.run(host=config.host, port=config.port, debug=config.debug)


if require.main == module:
  main()
