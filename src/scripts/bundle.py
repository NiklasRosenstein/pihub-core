"""
Builds a JavaScript bundle from the components defined in the PiHub
configuration file. The following steps will be performed:

1. Render all files from the www/ directory of all components and the
   `webpack.config.js` to the build directory using Jinja2.
2. Create a bundle using the `webpack` command.
"""

import argparse
import jinja2
import json
import os
import shutil
import subprocess
import sys
import textwrap
import config from '../config'
import {load_component} from '../component'

parser = argparse.ArgumentParser(
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=textwrap.dedent('''
    Orchestrates the JavaScript dependencies and the bundling process.
  ''')
)
parser.add_argument(
  '--build-directory',
  help='The build directory to write the preprocessed JavaScript files to. '
    'Defaults to the directory defined in the PiHub configuration (which in '
    'turn defaults to build/src). This is also the directory where '
    'JavaScript dependencies are installed to.'
)
parser.add_argument(
  '--bundle-directory',
  help='The output directory of the bundle built with webpack. Defaults to '
    'the directory defined in the PiHub configuration (which in turn '
    'defaults to build/bundle).'
)

subparsers = parser.add_subparsers(dest='command')

install_parser = subparsers.add_parser(
  'install',
  description=textwrap.dedent('''
    Install all JavaScript dependencies into the build directory.
    Requires yarn.
  ''')
)

build_parser = subparsers.add_parser(
  'build',
  description=textwrap.dedent('''
    Builds the JavaScript bundle with webpack. Ensure that you installed
    all dependencies beforehand.
  ''')
)
build_parser.add_argument(
  '--no-sync',
  action='store_true',
  help='Don\'t sync PiHub component JavaScript source files.'
)

add_parser = subparsers.add_parser(
  'add',
  description=textwrap.dedent('''
    Install one or more JavaScript dependencies into the build directorie's
    node_modules/. As it is the default behaviour of Yarn, the installed
    dependencies will be added to the `package.json` in the current working
    directory.
  ''')
)
add_parser.add_argument('yarn_add_args', nargs='...')


def copytree(src, dst, symlinks=False, ignore=None, copyfile=None):
  if copyfile is None:
    copyfile = shutil.copy2
  for item in os.listdir(src):
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if os.path.isdir(s):
      os.makedirs(d, exist_ok=True)
      copytree(s, d, symlinks, ignore, copyfile)
    else:
      copyfile(s, d)


def make_preprocessor(**context_vars):
  """
  Creates a Jinja2 Environment and returns a function that accepts a source
  and destination file. If the source is a .js or .jsx file, it will be
  preprocessed using the Jinja2 environment and the *context_vars*.
  """

  # Since JavaScript makes use of curly braces, we'll need to make
  # them a bit more unique to avoid possible Jinja2 syntax errors
  # with plain JavaScript code.
  env = jinja2.Environment(
    block_start_string = '{{%',
    block_end_string = '%}}',
    variable_start_string = '{{@',
    variable_end_string = '@}}',
    comment_start_string = '{{#',
    comment_end_string = '#}}'
  )
  env.filters['repr'] = repr

  def copyfile(src, dst):
    if src.endswith('.js') or src.endswith('.jsx'):
      with open(src, 'r') as fp:
        template = env.from_string(fp.read())
      with open(dst, 'w') as fp:
        fp.write(template.render(**context_vars))
    else:
      shutil.copy2(src, dst)

  return copyfile


def yarn(*argv, cwd=None):
  command = ['yarn'] + list(argv)
  print('$', ' '.join(command))
  return subprocess.call(command, shell=True, cwd=cwd)


def main(argv=None):
  args = parser.parse_args(argv)
  if not args.command:
    parser.print_usage()
    return 0

  if args.build_directory:
    config.build_directory = args.build_directory
  if args.bundle_directory:
    config.bundle_directory = args.bundle_directory

  if args.command == 'add':
    node_modules = os.path.join(config.build_directory, 'node_modules')
    argv = args.yarn_add_args + ['--modules-folder', node_modules, '--no-bin-links']
    return yarn('add', *argv)

  components = [load_component(comp, get_namespace=False)
      for comp in config.components]
  packages = set(x.package for x in components)
  dependencies = {}
  for package in packages:
    package_json = package.directory.joinpath('package.json')
    if package_json.is_file():
      with package_json.open() as fp:
        dependencies.update(json.load(fp).get('dependencies', {}))

  # Print info about packages.
  print('Loaded {} package(s) from {} componenent(s).'.format(len(packages), len(components)))
  print('Found {} React routes.'.format(len(config.react_routes)))

  if args.command == 'install':
    print('Writing combined package.json')
    os.makedirs(config.build_directory, exist_ok=True)
    with open(os.path.join(config.build_directory, 'package.json'), 'w') as fp:
      json.dump({'dependencies': dependencies}, fp)
    print('Installing combined dependencies.')
    return yarn('install', '--silent', cwd=config.build_directory)

  elif args.command == 'build':
    # Merge JavaScript codebase while preprocessing with Jinja2.
    if not args.no_sync:
      print('Merging JavaScript codebase.')
      copyfile = make_preprocessor(
        pihub=config,
        output_dir=os.path.abspath(config.bundle_directory),
        build_dir=os.path.abspath(config.build_directory)
      )
      os.makedirs(config.build_directory, exist_ok=True)
      for package in packages:
        www_dir = package.directory.joinpath('www')
        if www_dir.is_dir():
          copytree(str(www_dir), config.build_directory, copyfile=copyfile)

    os.makedirs(config.bundle_directory, exist_ok=True)
    return yarn('run', 'webpack', cwd=config.build_directory)

  else:
    raise RuntimeError('unexpected command: {}'.format(args.command))

if require.main == module:
  sys.exit(main())
