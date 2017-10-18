"""
A component to regularly update a DuckDNS URL.

# Configuration

A dictionary with the name `duckdns` may provide the following options:

* `token`: The DuckDNS token for your account.
* `domains`: A list of domain names to update.
* `trigger`: The trigger to update the DNS. Defaults to `interval(minutes=30)`.

# Example

```python
duckdns = {
  'token': 'Your duckdns token here',
  'domains': ['mydomain'],
  'trigger': cron(hour='*')
}
```
"""

from apscheduler.triggers.interval import IntervalTrigger as interval
import requests
import {Component} from '@pihub/core/component'


class DuckDns(Component):

  API_URL = 'https://www.duckdns.org/update?domains={domains}&token={token}'

  def init_component(self, app):
    config = getattr(app.config, 'duckdns', None)
    if config:
      self.token = config['token']
      self.domains = config['domains']
      app.scheduler.add_job(self.update, config['trigger'])
      self.update()
    else:
      print('warning: no duckdns config found')

  def update(self):
    url = self.API_URL.format(domains=','.join(self.domains), token=self.token)
    response = requests.get(url)
    try:
      response.raise_for_status()
    except requests.HTTPError as e:
      print('duckdns: error:', e)


module.exports = DuckDns
