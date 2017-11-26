"""
Base class for PiHub components.
"""

class Component:
  """
  Components are anything that extend the PiHub application. Every component
  should be associated with a unique #name member that can be used by other
  components.

  A component's #initialized member is set by the PiHub right before the
  #init_component() method is called.
  """

  app = None
  name = None
  initialized = False

  def init_component(self, app):
    """
    Called to initialize the component. Other components can be retrieved
    from inside this method using #Application.find_component().
    """

    pass

  def get_database_revisions(self):
    """
    Return a #BaseRevisionHistory object that tells the highest revision
    number (with #max_revisions()) and can upgrade the database.
    """

    return None



def load_component(name, hooks=None):
  """
  Loads a PiHub component by name and returns a new instance of it. The *name*
  must be of the format `package:component` where `package` is a Node.py
  package name and `component` the name of a component configured in the
  package's manifest.

  If the #Component object that is being returned has no #Component.name
  associated with it, the specified *name* will be assigned to it.
  """

  if hooks is not None and name in hooks:
    comp = hooks[name]
    if isinstance(comp, type):
      comp = comp()
  else:
    package_name, _, comp_name = name.partition(':')
    package = require(package_name, exports=False).package

    if 'pihub-components' not in package.payload:
      raise RuntimeError('package {!r} has no pihub-components configuration'.format(package_name))
    if comp_name not in package.payload['pihub-components']:
      raise RuntimeError('package {!r} has no component {!r}'.format(package_name, comp_name))

    module_name = package.payload['pihub-components'][comp_name]
    comp = package.require(module_name)()

  if not comp.name:
    comp.name = name
  return comp
