"""
The dashboard component.
"""

import collections
import flask
import {app, config} from '@pihub/core'

__component_meta__ = {}

config.react_routes.append('@pihub/core/components/dashboard')
