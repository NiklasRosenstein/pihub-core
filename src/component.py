"""
Loads components and validates their structure. A component must be a Node.py
module that is requirable from the `@pihub/core` package. Every component must
define a `__component_meta__` dictionary that contains information such as the
component's database revision.

Note that a component can not declare database entities without defining its
`database_revision` member.

Example:

    __component_meta__ = {
      'database_revision': 42
    }
"""

class ComponentError(Exception):
  pass


def load_component(name, get_namespace=True):
  try:
    module = require.try_(name, exports=False)
  except require.TryResolveError:
    raise ComponentError('failed to require component {!r}'.format(name))
  if not isinstance(getattr(module.namespace, '__component_meta__', None), dict):
    raise ComponentError('component {!r} has no __component_meta__ key or '
        'it is not a dictionary.'.format(name))
  if get_namespace:
    return module.namespace
  return module
