
import argparse
import textwrap
import sys
import database from '../database'

parser = argparse.ArgumentParser(
  description=textwrap.dedent('''
    Manage database schema migrations for installed components.
  ''')
)


def main():
  args = parser.parse_args()
  db, InstalledComponent = database.temporary_binding()
  with database.session:
    for name, comp, have_rev, curr_rev in database.component_revisions(InstalledComponent):
      if have_rev is None:
        print('NEW', name)
        InstalledComponent.set_revision(name, curr_rev)
      elif curr_rev is None:
        print('REMOVED', name)
      elif have_rev == curr_rev:
        print('KEEP', name)
      else:
        print('MIGRATE', name, '({} ==> {})'.format(have_rev, curr_rev))
        comp.execute_migration(have_rev, curr_rev)
        InstalledComponent.set_revision(name, curr_rev)


if require.main == module:
  sys.exit(main())
