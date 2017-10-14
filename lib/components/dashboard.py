"""
Dashboard component.
"""

import flask
import _comp from '../component'

bp = flask.Blueprint('@pihub/core:dashboard', '')

@bp.route('/')
def dashboard():
  return flask.render_template('pihub-core/dashboard.html')


class Dashboard(_comp.Component):

  def init_component(self, app):
    app.flask.register_blueprint(bp)


module.exports = Dashboard
