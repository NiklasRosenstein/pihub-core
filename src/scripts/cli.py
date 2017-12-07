"""
PiHub CLI.
"""

import argparse
import sys
import nodepy

parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version=module.package.payload['version'])
parser.add_argument('command', choices={'addjs', 'bundle', 'migrate', 'server'})
parser.add_argument('argv', nargs='...')
args = parser.parse_args()

module = require.resolve('./' + args.command)
sys.argv = [sys.argv[0]] + args.argv
require.context.main_module = module
require.context.load_module(module)
