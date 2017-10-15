"""
The PiHub application class.
"""

import flask
import db from './database'


class Application:
  """
  The central object for the PiHub application. Exposes the Flask application
  object and an interface for registering middlewares.

  The application object will always export itself under the name `pihub`
  into the #flask.g object.
  """

  def __init__(self, config):
    self.config = config
    self.components = []
    self.middlewares = []
    self.flask = flask.Flask(
      'pihub-core',
      template_folder=str(module.directory.parent.joinpath('templates')),
      static_folder=str(module.directory.parent.joinpath('static'))
    )
    self.flask.config['SECRET_KEY'] = config.secret_key
    self.flask.before_first_request(self.__before_first_request)
    self.flask.before_request(self.__before_request)
    self.flask.after_request(self.__after_request)

  def __before_first_request(self):
    for mw in self.middlewares:
      mw.before_first_request()

  def __before_request(self):
    flask.g.pihub = self
    for mw in self.middlewares:
      result = mw.before_request()
      if result is not None:
        return result

  def __after_request(self, response):
    for mw in self.middlewares:
      response = mw.after_request(response)
    return response

  @db.session
  def upgrade_database_revisions(self):
    for comp in self.components:
      rev = db.ComponentDatabaseRevision.get(comp.name)
      history = comp.get_database_revisions()
      if history is not None and history.max_revisions() != rev.num:
        print('Upgrading component:', comp.name)
        migrate(db.db, comp.get_database_revision_history(), rev.num, num)
      db.ComponentDatabaseRevision.set(comp.name, num)

  @db.session
  def check_database_revisions(self):
    ok = True
    for comp in self.components:
      rev = db.ComponentDatabaseRevision.get(name=comp.name)
      history = comp.get_database_revisions()
      if history is not None and history.max_revisions() != rev.num:
        ok = False
        print('error: component {!r} database revision is not up to date '
              '({} is not {})'.format(rev.num, num))
    return ok

  @db.session
  def init_components(self):
    """
    Should be called before the application is started, otherwise components
    will not have a chance to register routes to the Flask application.

    This function will also execute any outstanding database upgrades.
    """

    for comp in self.components:
      if not comp.initialized:
        comp.initialized = True
        comp.init_component(self)

  def find_component(self, comp_name, initialize=True):
    """
    Finds the first component with the specified *comp_name* and returns it.
    Returns #None if no component could be found. If *initialize* is #True,
    it will be ensured that the Component is initialized before it is returned.
    """

    for comp in self.components:
      if comp.name == comp_name:
        if initialize and not comp.initialized:
          comp.initialized = True
          comp.init_component(self)
        return comp
    return None

  def get_component(self, comp_name, initialized=True):
    """
    Like #find_component(), but raises a #ComponentNotFoundError instead of
    returning #None.
    """

    comp = self.find_component(comp_name, initialized)
    if comp is None:
      raise ComponentNotFoundError(comp_name)
    return comp


class ComponentNotFoundError(Exception):
  pass
