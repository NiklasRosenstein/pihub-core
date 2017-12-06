"""
The PiHub Flask application.
"""

import flask
import os
import uuid
import config from './config'

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
