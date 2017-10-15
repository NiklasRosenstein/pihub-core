"""
This component installs a middleware for user authentication.
"""

__version__ = '1.0.0'

import datetime
import flask
import fnmatch
import uuid
import db from '../lib/database'
import {Component} from '../lib/component'
import {Middleware} from '../lib/middleware'

bp = flask.Blueprint('@pihub/core:auth', '')


@bp.route('/auth', methods=['GET', 'POST'])
@db.session
def auth():
  if flask.request.method == 'POST':
    password = flask.request.form.get('password')
    if flask.g.pihub.config.pihub_core_auth['password'] == password:
      token = AuthToken()
      flask.session['token'] = token.token
      return flask.redirect(flask.url_for('@pihub/core:dashboard.dashboard'))
    error = 'Wrong password.'
  else:
    error = None
  return flask.render_template('pihub-core/auth.html', error=error)


@bp.route('/signout', methods=['GET'])
@db.session
def signout():
  token = flask.session.pop('token', None)
  token = AuthToken.get(token=token)
  if token:
    token.delete()
  return flask.redirect(flask.url_for('@pihub/core:auth.auth'))


class AuthRevisionHistory(db.RevisionHistory):

  def rev_0001(self, db):
    db.execute("""
      ALTER TABLE pihub_core_auth_token
      ADD remote_addr TEXT NOT NULL
      DEFAULT ''
    """)


class AuthToken(db.Entity):
  _table_ = "pihub_core_auth_token"

  token = db.PrimaryKey(str)
  expires_on = db.Optional(datetime.datetime)
  #remote_addr = db.Required(str)

  def __init__(self, token=None, expires_on=None):
    if token is None:
      token = str(uuid.uuid4())
    if expires_on is None:
      # TODO: Configurability of standard token validity time
      expires_on = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    super().__init__(token=token, expires_on=expires_on)

  @classmethod
  @db.session
  def has_unexpired_token(cls, token):
    obj = cls.get(token=token)
    if obj is None:
      return False
    if obj.expires_on and obj.expires_on < datetime.datetime.utcnow():
      obj.delete()
      return False
    return True


class AuthMiddleware(Middleware):

  def __init__(self):
    self.exclude_from_auth = ['/auth', '/static/*']

  def before_request(self):
    for pattern in self.exclude_from_auth:
      if fnmatch.fnmatch(flask.request.path, pattern):
        return None  # No auth required
    token = flask.session.get('token')
    if not token or not AuthToken.has_unexpired_token(token):
      return flask.redirect(flask.url_for('@pihub/core:auth.auth'))
    return None


class AuthComponent(Component):

  def init_component(self, app):
    self.middleware = AuthMiddleware()
    app.middlewares.append(self.middleware)
    app.flask.register_blueprint(bp)

    dashboard = app.get_component('@pihub/core:dashboard')
    dashboard.right_menu.append(dashboard.MenuItem('Sign Out', '/signout'))

  def get_database_revisions(self):
    return None # return AuthRevisionHistory()


module.exports = AuthComponent
