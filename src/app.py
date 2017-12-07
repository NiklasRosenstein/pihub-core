"""
The PiHub Flask application.
"""

import flask
import os
import uuid
import config from './config'
import database from './database'

app = flask.Flask(
  'pihub',
  static_url_path='/static',
  static_folder=os.path.abspath('build/bundle'),
  template_folder=str(module.directory.parent.joinpath('templates'))
)
app.config['SECRET_KEY'] = getattr(config, 'secret_key', None) or str(uuid.uuid4())

def index(path=None):
  return flask.render_template('@pihub/core/index.html')


def init():
  if not config.debug or os.getenv('WERKZEUG_RUN_MAIN', '') == 'true':
    # Ensure that all components are loaded.
    print('Loading components ...')
    config.loader.load_components(config.components)

    # Assert that all database schemas are up-to-date.
    print('Checking component database_revision consistency ...')
    error = False
    InstalledComponent = database.temporary_binding()[1]
    with database.session:
      for name, comp, have_rev, curr_rev in database.component_revisions(InstalledComponent):
        if curr_rev is None: continue  # component not installed
        if have_rev is not None and have_rev != curr_rev:
          print('ERROR {} database schema is not up-to-date.'.format(name))
    if error:
      exit(1)

    # Connect to the database and bind all delayed entities.
    print('Connecting database and binding entities ...')
    database.bind()

    # Initialize all components.
    print('Initializing components ...')
    config.loader.call_if_exists('init_component')

    # Register all UI routes.
    print('Register UI routes ...')
    for route in config.ui_routes:
      app.add_url_rule(route, view_func=index)

  return app
