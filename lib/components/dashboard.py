"""
Dashboard component.

# Documentation

## bp

The #flask.Blueprint object for the dashboard component.

## flask.request.dashboard

The #Dashboard instance that is currently in use to handle the request.
"""

import flask
import base from './base'
import middleware from '../middleware'

bp = flask.Blueprint('@pihub/core:dashboard', '')


@bp.route('/')
def dashboard():
  return flask.render_template('pihub-core/dashboard.html')


class Dashboard(base.Component):

  def init_component(self, app):
    app.middlewares.append(middleware.PublishRequestObject('dashboard', self))
    app.flask.register_blueprint(bp)


module.exports = Dashboard
