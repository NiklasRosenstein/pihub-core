"""
PiHub's database connection is based on Pony.ORM. New entities introduced by
components should be prefixed with the component name to avoid name collisions.
"""

from pony.orm.core import Database, db_session as session
import os
import pony.orm.core
import types
import {load_component} from './component'
import config from './config'
import utils from './utils'

config.setdefault('database', {
  'provider': 'sqlite',
  'filename': os.path.abspath('pihub.sqlite'),
  'create_db': True
})

__component_meta__ = {
  'database_revision': 1
}

pony.orm.sql_debug(True)


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
  real entity after #bind_entity() has been called.
  """

  __subclasses = []
  __entity = None
  __reconstructibles = None

  def __init_subclass__(cls, module=None, **kwargs):
    if module is not None:
      cls.__module__ = module
    else:
      module = cls.__module__
    component = load_component(module)
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
      raise RuntimeError('{}.bind_entity() not called'.format(cls.__name__))
    return cls.__entity(*a, **kw)

  @classmethod
  def bind_entity(cls, entity_class, temporary=False):
    """
    Generate a real #db.Entity from this #DelayedEntity. If the real entity
    has already been created, that entity is returned instead of creating a
    new class.

    Note that binding the entity non-temporarily will replace all members
    that represent Pony.ORM attributes (here replaced by #utils.Reconstructible
    instances) with the actual attributes.

    An entity can be bound multiple times, a #temporary binding will not bind
    the generated Pony.ORM entity with the #DeclaredEntity subclass.
    """

    if cls is DelayedEntity:
      msg = 'DelayedEntity.bind_entity() must be called on a subclass.'
      raise RuntimeError(msg)

    if not temporary and cls.__entity:
      return cls.__entity

    data = vars(cls).copy()
    for key, value in cls.__reconstructibles.items():
      data[key] = value = value.reconstruct()
      if not temporary:
        setattr(cls, key, value)

    bases = []
    for base in cls.__bases__:
      if issubclass(base, DelayedEntity) and base is not DelayedEntity:
        bases.append(base.bind_entity(entity_class, temporary))
    if not bases:
      bases.append(entity_class)

    entity = type(cls.__name__, tuple(bases), data)

    # Replace references to `cls` in function closures with the entity class.
    # This is to allow #super() to function correctly in the created Entity.
    for key in data.keys():
      value = getattr(entity, key)
      if not isinstance(value, types.FunctionType) or not value.__closure__:
        continue
      try:
        closure = utils.closure_replace_cell_contents(value.__closure__, cls, entity)
      except ValueError:
        # The closure does not contain a reference to `cls`.
        pass
      else:
        value = utils.copy_function(value, closure=closure)
        setattr(entity, key, value)

    if not temporary:
      cls.__entity = entity
    return entity


class InstalledComponent(DelayedEntity):
  """
  Stores the database revision number of a PiHub component in the database.

  Note that the migration process must happen before other components are
  loaded as otherwise `db.generate_mapping()` will raise an error because the
  database table schema does not match the entity declaration.
  """

  component = PrimaryKey(str)
  revision = Required(int)


def do_component_migration():
  """
  Performs the migration of loaded components and those the defined entities.
  This will create a new Pony #Database object that will bind to the
  configured database and perform the migration.
  """

  db = Database()
  db.bind(**config.database)
  InstalledComponentEntity = InstalledComponent.bind_entity(db.Entity, temporary=True)
  db.generate_mapping(create_tables=True)

  # Get a unique list of components that use the database connection (ordered).
  components = []
  for entity in DelayedEntity._DelayedEntity__subclasses:
    if entity.__module__ not in components:
      components.append(entity.__module__)

  print('Found {} component{} with declared entities.'.format(
      len(components), 's' if len(components) != 1 else ''))
  print('Running migrations.')

  def error(msg):
    print(msg, 'ERROR')
    raise RuntimeError(msg)

  def migrate_comp(comp):
    module = load_component(component)
    revision = module.__component_meta__.get('database_revision', None)
    if not isinstance(revision, int):
      msg = 'Component {} defines no or an invalid database_revision.'.format(component)
      error(msg)

    have = InstalledComponentEntity.get(component=component)
    if not have:
      print('  NEW {}'.format(component))
      have = InstalledComponentEntity(component=component, revision=revision)
    else:
      if have.revision != revision:
        print('  UPGRADE {} ({} -> {})'.format(component, have.revision, revision))
        if not hasattr(module, 'do_migration'):
          error('Component {} defines no do_migration().'.format(component))
        raise NotImplementedError('MIGRATION NOT IMPLEMENTED')  # TODO
        have.revision = revision

  with session:
    for component in components:
      migrate_comp(component)

  print('Migration complete.')


def initialize():
  print('Initializing database connection.')
  db.bind(**config.database)
  entities = DelayedEntity._DelayedEntity__subclasses
  print('Binding {} entities to database.'.format(len(entities)))
  for entity in entities:
    entity.bind_entity(db.Entity)
  db.generate_mapping(create_tables=True)


db = Database()
