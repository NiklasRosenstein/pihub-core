"""
The PiHub application class.
"""

import flask
import middleware from './middleware'


class Application:
  """
  The central object for the PiHub application. Exposes the Flask application
  object and an interface for registering middlewares.
  """

  def __init__(self, config):
    self.config = config
    self.components = []
    self.middlewares = []
    self.flask = flask.Flask('pihub-core')
    self.flask.before_first_request(self.__before_first_request)
    self.flask.before_request(self.__before_request)
    self.flask.after_request(self.__after_request)

  def __before_first_request(self):
    for mw in self.middlewares:
      mw.before_first_request()

  def __before_request(self):
    for mw in self.middlewares:
      result = mw.before_request()
      if result is not None:
        return result

  def __after_request(self, response):
    for mw in self.middlewares:
      response = mw.after_request(response)
    return response

  def init_components(self):
    """
    Should be called before the application is started, otherwise components
    will not have a chance to register routes to the Flask application.
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
