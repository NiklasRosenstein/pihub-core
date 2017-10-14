"""
Dashboard component.
"""

import _comp from '../component'


class Dashboard(_comp.Component):

  def init_component(self, app):
    app.flask.add_url_rule('/', 'dashboard', self.__dashboard)

  def __dashboard(self):
    return "Hello, World!"


module.exports = Dashboard
