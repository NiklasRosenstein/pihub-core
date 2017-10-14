"""
Dashboard component.

# Documentation

## bp

The #flask.Blueprint object for the dashboard component.

## flask.request.dashboard

The #Dashboard instance that is currently in use to handle the request.
"""

import collections
import flask
import base from './base'

NAME = '@pihub/core:dashboard'
bp = flask.Blueprint(NAME, '')


@bp.route('/')
def dashboard():
  dashboard = flask.g.pihub.find_component(NAME)
  return flask.render_template('pihub-core/dashboard.html',
    dashboard=dashboard)


class Dashboard(base.Component):

  MenuItem = collections.namedtuple('MenuItem', 'name url')

  def __init__(self):
    self.left_menu = [self.MenuItem('PiHub', '/')]
    self.right_menu = []

  def init_component(self, app):
    app.flask.register_blueprint(bp)


module.exports = Dashboard
