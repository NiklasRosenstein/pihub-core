"""
This component installs a middleware to require user-authentication for all
URLs but the ones that are explcitly whitelisted in the PiHub configuration.
"""

import datetime
import flask
import fnmatch
import uuid
import {app, config, database} from '@pihub/core'

__component_meta__ = {
  'requires': ['@pihub/core/database'],
  'database_revision': 1
}

config.setdefault('auth', {})
config.auth.setdefault('password', 'alpine')
config.auth.setdefault('token_timeout', {'hours': 2})
config.auth.setdefault('exclude', ['/auth/*', '/static/*'])
config.auth.setdefault('session_variable', 'pihub_auth_token')


class AuthToken(database.DelayedEntity):

  token = database.PrimaryKey(str)
  expires_on = database.Optional(datetime.datetime)
  remote_addr = database.Required(str)

  def __init__(self, token=None, expires_on=None, remote_addr=None):
    if token is None:
      token = str(uuid.uuid4())
    if expires_on is None:
      tdelta = datetime.timedelta(**config.auth['token_timeout'])
      expires_on = datetime.datetime.utcnow() + tdelta
    if remote_addr is None:
      remote_addr = flask.request.remote_addr
    super().__init__(token=token, expires_on=expires_on, remote_addr=remote_addr)

  @classmethod
  def get_unexpired(cls, token):
    if not token:
      return None
    obj = cls.get(token=token)
    if obj is None:
      return False
    if obj.expires_on and obj.expires_on < datetime.datetime.utcnow():
      obj.delete()
      return None
    return obj


@app.route('/auth/signin', methods=['GET', 'POST'])
@database.session
def auth_signin():
  if flask.request.method == 'POST':
    password = flask.request.form.get('password')
    if config.auth['password'] == password:
      token = AuthToken()
      flask.session[config.auth['session_variable']] = token.token
      return flask.redirect(flask.url_for('index'))
    return flask.Response('Wrong password.', status=403, mimetype='text/plain')
  if AuthToken.get_unexpired(flask.session.get(config.auth['session_variable'])):
    return flask.redirect(flask.url_for('index'))
  return flask.render_template('@pihub/core/index.html')


@app.route('/auth/signout', methods=['GET'])
@database.session
def auth_signout():
  token = AuthToken.get_unexpired(flask.session.pop(config.auth['session_variable'], None))
  if token:
    token.delete()
  return flask.redirect(flask.url_for('auth_signin'))


@app.before_request
@database.session
def auth_middleware():
  for pattern in config.auth['exclude']:
    if fnmatch.fnmatch(flask.request.path, pattern):
      return None  # No auth required
  token = AuthToken.get_unexpired(flask.session.get(config.auth['session_variable']))
  if not token:
    return flask.redirect(flask.url_for('auth_signin'))
  return None
