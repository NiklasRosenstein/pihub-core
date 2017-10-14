"""
This component installs a middleware for user authentication.
"""

import flask
import {Component} from './base'
import {Middleware} from '../middleware'

bp = flask.Blueprint('@pihub/core:auth', '')


@bp.route('/auth', methods=['GET', 'POST'])
def auth():
  if flask.request.method == 'POST':
    password = flask.request.form.get('password')
    flask.session['password'] = password
    if flask.g.pihub.config.auth['password'] == password:
      return flask.redirect(flask.url_for('@pihub/core:dashboard.dashboard'))
    error = 'Wrong password.'
  else:
    error = None
  return flask.render_template('pihub-core/auth.html', error=error)


class AuthMiddleware(Middleware):

  def before_request(self):
    if flask.request.path == '/auth': # TODO!
      return None
    password = flask.session.get('password')
    if flask.g.pihub.config.auth['password'] != password:
      return flask.redirect(flask.url_for('@pihub/core:auth.auth'))
    return None


class AuthComponent(Component):

  def init_component(self, app):
    app.middlewares.append(AuthMiddleware())
    app.flask.register_blueprint(bp)


module.exports = AuthComponent
