"""
A component to regularly update a DuckDNS URL.
"""

__component_meta__ = {
  'requires': [
    '@pihub/core/components/scheduler'
  ]
}

import requests
import {config} from '@pihub/core'
import scheduler from '@pihub/core/components/scheduler'

config.setdefault('duckdns', {})
config.duckdns.setdefault('token', None)
config.duckdns.setdefault('domains', [])
config.duckdns.setdefault('interval', {'type': 'cron', 'hour': '*'})


API_URL = 'https://www.duckdns.org/update?domains={domains}&token={token}'


def init_component():
  if config.duckdns['token'] and config.duckdns['domains']:
    trigger = scheduler.trigger_from_config(config.duckdns['interval'])
    scheduler.schedule_job(do_duckdns_update, trigger)
  else:
    # TODO: Logging
    print('duckdns: note: no token or domains configured')


def do_duckdns_update():
  domains = config.duckdns['domains']
  token = config.duckdns['token']
  url = API_URL.format(domains=','.join(domains), token=str(token))
  response = requests.get(url)
  try:
    response.raise_for_status()
  except requests.HTTPError as e:
    # TODO: Logging
    print('duckdns: error:', e)
