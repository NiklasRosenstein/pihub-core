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
import base from '../lib/component'

NAME = '@pihub/core:dashboard'
bp = flask.Blueprint(NAME, '')


@bp.route('/')
def dashboard():
  dashboard = flask.g.pihub.find_component(NAME)
  return dashboard.render_page()


class MenuItem(object):

  def __init__(self, name, url, children=None, icon=None):
    self.name = name
    self.url = url
    self.children = children
    self.icon = icon


class DashboardSection(object):
  """
  Base class for sections that can are rendered on the dashboard page.
  """

  def extend_dashboard_menu(self, left, right):
    """
    Called whenever a dashboard page is rendered to determine items displayed
    in the menubar. *left* and *right* is a list of #MenuItem objects.
    """

    pass

  def render_dashboard_section(self):
    """
    Called to return an HTML string which contains the content of the section
    in the dashboard. May return #None to indicate that this #DashboardSection
    supports no inline-display section.
    """

    return None


class Dashboard(base.Component):

  MenuItem = MenuItem
  Section = DashboardSection

  def __init__(self):
    self.sections = []

  def init_component(self, app):
    app.flask.register_blueprint(bp)

  def render_page(self, main=None):
    """
    Renders the dashboard page. If *main* is specified, it must be a callable
    that returns the content of the dashboard's main content.
    """

    left = [MenuItem('Dashboard', flask.url_for(NAME + '.dashboard'), icon='home')]
    right = []
    for section in self.sections:
      section.extend_dashboard_menu(left, right)
    return flask.render_template('pihub-core/dashboard.html',
      dashboard=self, left_menu=left, right_menu=right, main=main)


module.exports = Dashboard
