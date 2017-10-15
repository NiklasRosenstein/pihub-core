"""
Tool for executing database migrations.
"""

import os


class BaseRevisionHistory(object):
  """
  Abstract class for providing a database migration history.
  """

  def max_revision(self):
    raise NotImplementedError

  def execute_revision(self, index, db):
    raise NotImplementedError


class DirectoryRevsionHistory(BaseRevisionHistory):

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

  def execute_revision(self, index, db):
    filename = os.path.join(self.directory, self.revisions[index])
    with open(filename, 'r') as fp:
      code = compile(fp.read(), filename, 'exec')
    scope = {'__file__': filename, 'db': db}
    exec(code, scope)


class RevisionHistory(BaseRevisionHistory):

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

  def execute_revision(self, index, db):
    getattr(self, self._revisions[index])(db)


def migrate(db, history, current_revision, target_revision, dry=False):
  """
  Execute all revisions between *current_revision* and *target_revision*.
  """

  if target_revision < current_revision:
    raise ValueError('target_revision can not be lower than current_revision')
  if target_revision > history.max_revision():
    raise ValueError('target_revision exceeds history.max_revision()')

  for num in range(current_revision, target_revision + 1):
    history.execute_revision(index, db)
