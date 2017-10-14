"""
Dashboard component.
"""

import flask
import base from './base'

bp = flask.Blueprint('@pihub/core:dashboard', '')


@bp.route('/')
def dashboard():
  return flask.render_template('pihub-core/dashboard.html')


class Dashboard(base.Component):

  def init_component(self, app):
    app.flask.register_blueprint(bp)


module.exports = Dashboard
