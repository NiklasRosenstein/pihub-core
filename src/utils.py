
import functools
import sys
import types


def make_cell(val=None):
  """
  Creates a new Python cell object.
  """

  x = val
  def closure():
    return x
  return closure.__closure__[0]


def closure_replace_cell_contents(closure, old, new):
  """
  Returns a new closure (a tuple of cells) that replaced *old* with *new*.
  If *old* does not occurr in the closure, a #ValueError is raised.
  """

  for i, cell in enumerate(closure):
    if cell.cell_contents == old:
      return closure[:i] + (make_cell(new),) + closure[i+1:]
  raise ValueError('closure does not contain value {!r}'.format(old))


def copy_function(f, code=None, globals=None, name=None, argdefs=None, closure=None):
  """
  Creates a copy of the function *f*, optionally overriding one of the
  functions members.
  """

  g = types.FunctionType(
    code or f.__code__,
    globals if globals is not None else f.__globals__,
    name = name or f.__name__,
    argdefs = argdefs if argdefs is not None else f.__defaults__,
    closure = closure if closure is not None else f.__closure__
  )
  g = functools.update_wrapper(g, f)
  g.__kwdefaults__ = f.__kwdefaults__
  return g


class Reconstructible:
  """
  Base class for reconstructible types.
  """


def reconstructible(type_, immediate=True):
  """
  Creates a new type that serves as a proxy for the specified *type_*. The
  arguments used to create an instance of the proxy are stored by the proxy,
  allowing to reconstruct a new instance of the real *type_*.

  If *immediate* is #True, create an instance of the proxy will also
  immediately create an instance of the *type_* for type-checking.
  """

  class new_type(Reconstructible):

    def __init__(self, *a, **kw):
      self.type = type_
      self.args = a
      self.kwargs = kw
      if immediate:
        self.value = type_(*a, **kw)
      else:
        self.value = None

    def reconstruct(self):
      return type_(*self.args, **self.kwargs)

  new_type.__name__ = 'Reconstructible' + type_.__name__
  return new_type


def mixed_metaclass(*classes):
  return type('NewMeta', classes, {})


class GetAttrMeta(type):
  """
  This metaclass allows to implement a type's `__getattr__()` as classmethod
  called `__type_getattr__()`. The instance method will automatically be
  converted to a classmethod.
  """

  def __new__(cls, name, bases, data):
    if '__type_getattr__' in data:
      data['__type_getattr__'] = classmethod(data['__type_getattr__'])
    return super(GetAttrMeta, cls).__new__(cls, name, bases, data)

  def __getattr__(self, name):
    return self.__type_getattr__(name)

  def __type_getattr__(self, name):
    raise AttributeError(name)


class InstanceCheckMeta(type):
  """
  This metaclass allows to implement a type's `__instancecheck__()` as
  classmethod called `__type_instancecheck__()`. The instance method will
  automatically be converted to a classmethod.
  """

  def __new__(cls, name, bases, data):
    if '__type_instancecheck__' in data:
      data['__type_instancecheck__'] = classmethod(data['__type_instancecheck__'])
    return super(InstanceCheckMeta, cls).__new__(cls, name, bases, data)

  def __instancecheck__(self, other):
    return self.__type_instancecheck__(other)

  def __type_instancecheck__(self, name):
    raise AttributeError(name)


class InitSubclassMeta(type):
  """
  This metaclass enables the `__init_subclass__()` from PEP 487 to Python
  versions below 3.6. One maybe important difference to consider is the
  additional stackframes introduced by this metaclass.

  This metaclass adds no new behaviour in Python 3.6 or higher.
  """

  # PEP 487 introduces __init_subclass__() in Python 3.6
  if sys.version < '3.6':
    def __new__(cls, name, bases, data):
      if '__init_subclass__' in data:
        data['__init_subclass__'] = classmethod(data['__init_subclass__'])
      sub_class = super(InitSubclassMeta, cls).__new__(cls, name, bases, data)
      sub_super = super(sub_class, sub_class)
      if hasattr(sub_super, '__init_subclass__'):
        sub_super.__init_subclass__()
      return sub_class
