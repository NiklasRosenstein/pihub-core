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

import collections


class ComponentError(Exception):
  pass


class ComponentLoader:

  def __init__(self):
    self.component_modules = collections.OrderedDict()

  @property
  def components(self):
    return ((k, v.namespace) for k, v in self.component_modules.items())

  def get_component(self, name, get_namespace=True):
    module = self.component_modules[name]
    if get_namespace:
      return module.namespace
    return module

  def load_component(self, name, get_namespace=True):
    if name in self.component_modules:
      module = self.component_modules[name]
    else:
      try:
        module = require.try_(name, exports=False)
      except require.TryResolveError:
        raise ComponentError('failed to require component {!r}'.format(name))
      if not isinstance(getattr(module.namespace, '__component_meta__', None), dict):
        raise ComponentError('component {!r} has no __component_meta__ key or '
            'it is not a dictionary.'.format(name))
      for dependency in module.namespace.__component_meta__.get('requires', []):
        self.load_component(dependency)
      self.component_modules[name] = module
    if get_namespace:
      return module.namespace
    return module

  def load_components(self, components):
    return [self.load_component(x) for x in components]

  def call_if_exists(self, __method_name, *args, **kwargs):
    for comp in self.components:
      if hasattr(comp, __method_name):
        getattr(comp, __method_name)(*args, **kwargs)
