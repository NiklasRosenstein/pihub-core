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
  'database_revision': 1
}

config.react_routes.append('@pihub/core/components/auth')
config.setdefault('auth', {})
config.auth.setdefault('password', 'alpine')
config.auth.setdefault('token_timeout', {'hours': 2})
config.auth.setdefault('exclude', ['/auth/*', '/static/*'])


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
  @database.session
  def has_unexpired_token(cls, token):
    obj = cls.get(token=token)
    if obj is None:
      return False
    if obj.expires_on and obj.expires_on < datetime.datetime.utcnow():
      obj.delete()
      return False
    return True


@app.route('/auth/signin', methods=['GET', 'POST'])
@database.session
def auth_signin():
  if flask.request.method == 'POST':
    password = flask.request.form.get('password')
    if config.auth['password'] == password:
      token = AuthToken()
      flask.session['token'] = token.token
      return flask.redirect(flask.url_for('index'))
    return flask.Response('Wrong password.', code=403, mime='text/plain')
  # Display the React app.
  return flask.render_template('@pihub/core/index.html')


@app.route('/auth/signout', methods=['GET'])
@database.session
def auth_signout():
  token_string = flask.session.pop('token', None)
  if token_string:
    auth_token = AuthToken.get(token=token_string)
    if auth_token:
      auth_token.delete()
  return flask.redirect(flask.url_for('auth_signin'))


@app.before_request
def auth_middleware():
  for pattern in config.auth['exclude']:
    if fnmatch.fnmatch(flask.request.path, pattern):
      return None  # No auth required
  token = flask.session.get('token')
  if not token or not AuthToken.has_unexpired_token(token):
    return flask.redirect(flask.url_for('auth_signout'))
  return None


def init_component():
  with database.session:
    #AuthToken(remote_addr='foo')
    print(AuthToken.get(token='foo'))
    pass

#right.append(Dashboard.MenuItem('Sign Out', '/signout', icon='sign out'))
