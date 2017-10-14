"""
This component installs a middleware for user authentication.
"""

import flask
import fnmatch
import {Component} from './base'
import {Middleware} from '../middleware'

bp = flask.Blueprint('@pihub/core:auth', '')


@bp.route('/auth', methods=['GET', 'POST'])
def auth():
  if flask.request.method == 'POST':
    password = flask.request.form.get('password')
    flask.session['password'] = password
    if flask.g.pihub.config.pihub_core_auth['password'] == password:
      return flask.redirect(flask.url_for('@pihub/core:dashboard.dashboard'))
    error = 'Wrong password.'
  else:
    error = None
  return flask.render_template('pihub-core/auth.html', error=error)


@bp.route('/signout', methods=['GET'])
def signout():
  flask.session.pop('password')
  return flask.redirect(flask.url_for('@pihub/core:auth.auth'))


class AuthMiddleware(Middleware):

  def __init__(self):
    self.exclude_from_auth = ['/auth']

  def before_request(self):
    for pattern in self.exclude_from_auth:
      if fnmatch.fnmatch(flask.request.path, pattern):
        return None  # No auth required
    password = flask.session.get('password')
    if flask.g.pihub.config.pihub_core_auth['password'] != password:
      return flask.redirect(flask.url_for('@pihub/core:auth.auth'))
    return None


class AuthComponent(Component):

  def init_component(self, app):
    self.middleware = AuthMiddleware()
    app.middlewares.append(self.middleware)
    app.flask.register_blueprint(bp)


module.exports = AuthComponent
