"""
Create a pihub.config.py from the default configuration.
"""

import argparse
import os
import sys
import {gen_secret} from './gen-secret'

parser = argparse.ArgumentParser()
parser.add_argument('--password', default='alpine')


def main():
  args = parser.parse_args()
  filename = 'pihub.config.py'
  if os.path.isfile(filename):
    print('error: {} already exists'.format(filename))
    return 1
  with module.package.directory.joinpath(filename + '.example').open() as src:
    code = src.read()
  code = code.replace('{secret key here}', gen_secret())
  code = code.replace('{password here}', args.password)
  with open(filename, 'w') as dst:
    dst.write(code)


if require.main == module:
  sys.exit(main())
