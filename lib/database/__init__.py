"""
Interface for PiHub's database connection with Pony ORM.
"""

from pony.orm import *
from pony.orm import db_session as session
from pony.orm.core import EntityMeta
import {RevisionBoard} from './migrate'

db = Database()
Entity = db.Entity


class ComponentDatabaseRevision(Entity):
  """
  The PiHub application object uses this entity to store the revision number
  of components.
  """

  _table_ = 'pihub_core_component_revision'

  name = PrimaryKey(str)
  num = Required(int)

  @classmethod
  @session
  def get(cls, name):
    return EntityMeta.get(cls, name=name)

  @classmethod
  @session
  def set(cls, name, num):
    obj = cls.get(name=name)
    if obj:
      obj.version = version
    else:
      obj = cls(name=name, num=num)
