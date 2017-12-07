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

# TODO: Forward any and all supported routes to to the index.html.
@app.route('/')
def index(path=None):
  return flask.render_template('@pihub/core/index.html')


def init():
  # Ensure that all components are loaded.
  config.loader.load_components(config.components)

  # Assert that all database schemas are up-to-date.
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
  database.bind()

  # Initialize all components.
  config.loader.call_if_exists('init_component')

  return app
