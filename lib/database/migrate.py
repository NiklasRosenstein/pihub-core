"""
Tool for executing database migrations.
"""

import os


class MigrationError(Exception):
  pass


class Migrator(object):

  def __init__(self, db, dry=False):
    if target_revision < current_revision:
      raise ValueError('target_revision must be >= current_revision')
    self.db = db
    self.dry = dry

  def _check_collection(self, collection):
    if collection not in self.db.collection_names():
      print('    warning: Database has no collection "{}"'.format(collection))

  def add_field(self, collection, field, value):
    """
    Adds a field to a collection with the specified default value if the
    field does not already exist.
    """
    print('  Adding field "{}" to collection "{}" with value "{}"'.format(
        field, collection, value))
    self._check_collection(collection)
    if self.dry:
      print('    Skipped (dry run)')
    else:
      result = self.db[collection].update({}, {'$set': {field: value}})
      print('    {}'.format(result))

  def delete_field(self, collection, field):
    """
    Removes a field from all documents in a collection.
    """

    print('  Deleting field "{}" of collection "{}"'.format(field, collection))
    self._check_collection(collection)
    if self.dry:
      print('    Skipped (dry run)')
    else:
      result = self.db[collection].update({}, {'$unset': {field: 1}})
      print('    {}'.format(result))

  def update_collection(self, collection):
    """
    Decorator for a function that will be for all documents in the
    specified *collection*.
    """

    def decorator(func):
      print('  Updating collection "{}" with {}()'.format(collection, func.__name__))
      self._check_collection(collection)
      for obj in self.db[collection].find({}):
        func(obj)
        if not self.dry:
          self.db[collection].save(obj)
      if self.dry:
        print('    Objects not saved (dry run)')
    return decorator


class RevisionHistory(object):
  """
  Abstract class for providing a database migration history.
  """

  def max_revision(self):
    raise NotImplementedError

  def execute_revision(self, migrator, index):
    raise NotImplementedError


class DirectoryRevsionHistory(RevisionHistory):

  def __init__(self, directory):
    self.directory = directory
    self.revisions = sorted(x for x in os.listdir(self.directory) if x.endswith('.py'))
    for i, name in enumerate(self.revisions):
      try:
        v = int(name[:-3])
      except ValueError:
        raise ValueError('invalid revision name: {!r}'.format(name))
      if (i+1) != v:
        raise ValueError('missing revision: {!r}'.format(i))

  def max_revision(self):
    return len(self.revisions)

  def execute_revision(self, migrator, index):
    filename = os.path.join(self.directory, self.revisions[index])
    with open(filename, 'r') as fp:
      code = compile(fp.read(), filename, 'exec')
    scope = {'__file__': filename, 'migrator': self}
    exec(code, scope)


class RevisionBoard(RevisionHistory):

  def __init__(self):
    self._revisions = []
    for k in sorted(dir(self)):
      if k.startswith('rev_'):
        try:
          num = int(k[4:])
        except ValueError:
          raise ValueError('invalid revision method name: {!r}'.format(k))
        if num != (len(self._revisions) + 1):
          raise ValueError('invalid revision method name or order: {!r}'.format(k))
        self._revisions.append(k)

  def max_revision(self):
    return self._max_revision

  def execute_revision(self, migrator, index):
    getattr(self, self._revisions[index])(migrator, index)


def migrate(db, history, current_revision, target_revision, dry=False):
  """
  Execute all revisions between *current_revision* and *target_revision*.
  """

  if target_revision < current_revision:
    raise ValueError('target_revision can not be lower than current_revision')
  if target_revision > history.max_revision():
    raise ValueError('target_revision exceeds history.max_revision()')

  migrate = Migrator(db, dry=dry)
  for num in range(current_revision, target_revision + 1):
    history.execute_revision(migrate, index)
