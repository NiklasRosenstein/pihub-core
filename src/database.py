"""
PiHub's database connection is based on Pony.ORM. New entities introduced by
components should be prefixed with the component name to avoid name collisions.
"""

from pony.orm.core import Database, db_session as session
import os
import pony.orm.core
import types
import config from './config'
import utils from './utils'

config.setdefault('sql_debug', False)
config.setdefault('database', {
  'provider': 'sqlite',
  'filename': os.path.abspath('pihub.sqlite'),
  'create_db': True
})

__component_meta__ = {
  'web_module': None,
  'database_revision': 1
}

pony.orm.sql_debug(config.sql_debug)

PrimaryKey = utils.reconstructible(pony.orm.core.PrimaryKey)
Required = utils.reconstructible(pony.orm.core.Required)
Optional = utils.reconstructible(pony.orm.core.Optional)
Collection = utils.reconstructible(pony.orm.core.Collection)
Set = utils.reconstructible(pony.orm.core.Set)


class DelayedEntity(
    metaclass=utils.mixed_metaclass(
      utils.GetAttrMeta,
      utils.InitSubclassMeta,
      utils.InstanceCheckMeta)):
  """
  Placeholder for Pony.ORM entity declarations that will be generated at a
  designated point, when it is ensured that all migration steps have been
  performed.

  This class employs some magic so it can be used just like the Pony.ORM
  real entity after #create_database_entity() has been called.
  """

  __subclasses = []
  __entity = None
  __reconstructibles = None

  def __init_subclass__(cls, module=None, **kwargs):
    if module is not None:
      cls.__module__ = module
    else:
      module = cls.__module__
    component = config.loader.load_component(module)
    if not isinstance(component.__component_meta__.get('database_revision'), int):
      raise RuntimeError('component {!r} can not declare entities without '
          'specifying database_revision in __component_meta__ (note: must be '
          'an integer).'.format(module))
    super().__init_subclass__(**kwargs)
    cls.__subclasses.append(cls)
    cls.__reconstructibles = {}
    for key, value in vars(cls).items():
      if isinstance(value, utils.Reconstructible):
        cls.__reconstructibles[key] = value

  def __type_getattr__(cls, name):
    if cls.__entity is None:
      raise AttributeError(name)
    else:
      return getattr(cls.__entity, name)

  def __type_instancecheck__(cls, other):
    if cls.__entity is not None:
      return isinstance(other, cls.__entity)
    return False

  def __new__(cls, *a, **kw):
    if not cls.__entity:
      raise RuntimeError('no real entity bound to {}'.format(cls.__name__))
    return cls.__entity(*a, **kw)

  @classmethod
  def create_database_entity(cls, entity_base, bind=False):
    """
    Generate a real Pony ORM entity class from this #DelayedEntity and the
    *entity_base* base class. If *bind* is #True, the created class will be
    bound to the #DelayedEntity subclass.
    """

    if cls is DelayedEntity:
      msg = 'DelayedEntity.create_database_entity() must be called on a subclass.'
      raise RuntimeError(msg)

    if bind and cls.__entity:
      return cls.__entity

    data = vars(cls).copy()
    for key, value in cls.__reconstructibles.items():
      data[key] = value = value.reconstruct()
      if bind:
        setattr(cls, key, value)

    bases = []
    for base in cls.__bases__:
      if issubclass(base, DelayedEntity) and base is not DelayedEntity:
        base_entity = base.__entity
        if not base_entity:
          base_entity = base.create_database_entity(entity_base, bind=bind)
        bases.append(base_entity)
    if not bases:
      bases.append(entity_base)

    entity = type(cls.__name__, tuple(bases), data)
    entity.__name__ += '_Entity'
    entity.__qualname__ += '_Entity'

    # Update the closures in functions and methods that reference the
    # DelayedEntity subclass to instead reference the new entity class.
    for key in data.keys():
      value = getattr(entity, key)
      if isinstance(value, types.MethodType):
        try:
          func = utils.rebind_function_closure(value.__func__, cls, entity)
        except ValueError:  # cls does not appear in closure of function
          pass
        else:
          value = types.MethodType(func, value.__self__)
          setattr(entity, key, value)
      elif isinstance(value, types.FunctionType):
        try:
          value = utils.rebind_function_closure(value, cls, entity)
        except ValueError:  # cls does not appear in closure of function
          pass
        else:
          setattr(entity, key, value)

    if bind:
      cls.__entity = entity
    return entity

  @classmethod
  def delayed_entity_subclasses(cls):
    return cls.__subclasses


class InstalledComponent(DelayedEntity):
  """
  Stores the database revision number of a PiHub component in the database.

  Note that the migration process must happen before other components are
  loaded as otherwise `db.generate_mapping()` will raise an error because the
  database table schema does not match the entity declaration.
  """

  component = PrimaryKey(str)
  revision = Required(int)

  @classmethod
  def set_revision(cls, component, revision):
    have = cls.get(component=component)
    if have:
      have.revision = revision
    else:
      cls(component=component, revision=revision)


def temporary_binding():
  db = Database()
  db.bind(**config.database)
  InstalledComponentEntity = InstalledComponent.create_database_entity(db.Entity)
  db.generate_mapping(create_tables=True)
  return db, InstalledComponentEntity


def database_components():
  """
  Generator that returns a tuple of `(name, component)` for every component
  that uses the database.
  """

  seen = set()
  for entity in DelayedEntity.delayed_entity_subclasses():
    name = entity.__module__
    if name not in seen:
      seen.add(name)
      yield name, config.loader.get_component(name)


def component_revisions(InstalledComponent=InstalledComponent):
  """
  Yields `(name, component, have_revision, curr_revision)` for all currently
  and previously installed components.
  """

  result = []
  checked = set()

  config.loader.load_components(config.components)
  for name, component in database_components():
    checked.add(name)
    curr_revision = component.__component_meta__['database_revision']
    have = InstalledComponent.get(component=name)
    have_revision = have.revision if have else None
    yield (name, component, have_revision, curr_revision)
  for have in InstalledComponent.select():
    if have.component not in checked:
      yield (have.component, None, have.revision, None)


def bind():
  """
  Binds the global Pony database *db* to a provider from the database
  configuration and permanently binds all real entities for this database
  to the #DelayedEntity subclasses.
  """

  db.bind(**config.database)
  for cls in DelayedEntity.delayed_entity_subclasses():
    cls.create_database_entity(db.Entity, bind=True)
  db.generate_mapping(create_tables=True)


db = Database()
