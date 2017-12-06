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
import {load_component} from '../component'

parser = argparse.ArgumentParser(
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=textwrap.dedent('''
    Builds a JavaScript bundle from the components defined in the PiHub
    configuration file using Jinja2 and webpack.
  ''')
)
parser.add_argument(
  '--build-directory',
  default='build/src',
  help='The build directory to write the preprocessed JavaScript files to.'
)
parser.add_argument(
  '--bundle-directory',
  default='build/bundle',
  help='The output directory of the bundle built with webpack.'
)
parser.add_argument(
  '--install',
  action='store_true',
  help='Install JavaScript dependencies to build the bundle using Yarn.'
)
parser.add_argument('--no-sync', action='store_true')
parser.add_argument('--no-install', action='store_true')
parser.add_argument('--no-bundle', action='store_true')


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
  subprocess.call(command, shell=True, cwd=cwd)


def main(argv=None):
  args = parser.parse_args(argv)
  import config from '../config'

  # Determine distinct packages from components.
  packages = []
  dependencies = {}
  for comp in config.components:
    module = load_component(comp, get_namespace=False)
    package = module.package
    if package not in packages:
      packages.append(package)
    package_json = package.directory.joinpath('package.json')
    if package_json.is_file():
      with package_json.open() as fp:
        dependencies.update(json.load(fp).get('dependencies', {}))

  # Print info about packages.
  print('Loaded {} package(s) from {} componenent(s).'.format(
      len(packages), len(config.components)))
  print('Found {} React routes.'.format(len(config.react_routes)))

  # Install dependencies.
  if not args.no_install:
    print('Writing combined package.json')
    os.makedirs(args.build_directory, exist_ok=True)
    with open(os.path.join(args.build_directory, 'package.json'), 'w') as fp:
      json.dump({'dependencies': dependencies}, fp)
    print('Installing combined dependencies.')
    yarn('install', '--silent', cwd=args.build_directory)

  # Merge JavaScript codebase while preprocessing with Jinja2.
  if not args.no_sync:
    print('Merging JavaScript codebase.')
    copyfile = make_preprocessor(
      pihub=config,
      output_dir=os.path.abspath(args.bundle_directory),
      build_dir=os.path.abspath(args.build_directory)
    )
    os.makedirs(args.build_directory, exist_ok=True)
    for package in packages:
      www_dir = package.directory.joinpath('www')
      if www_dir.is_dir():
        copytree(str(www_dir), args.build_directory, copyfile=copyfile)

  # Build the bundle.
  if not args.no_bundle:
    print('Building bundle.')
    os.makedirs(args.bundle_directory, exist_ok=True)
    yarn('run', 'webpack', cwd=args.build_directory)


if require.main == module:
  sys.exit(main())
