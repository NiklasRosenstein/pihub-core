"""
Show RSS feeds.

# Configuration

The configuration `rss_feeds` must be a list of dictionaries that specify
the Rss URL and update interval.

```python
rss_feeds = [
  {
    'url': 'https://www.mvg.de/Tickerrss/CreateRssClass',
    'update_interval': {'minutes': 10}
  }
]
```
"""

from apscheduler.triggers import interval
from functools import partial
import feedparser
import flask
import threading
import {Component} from '@pihub/core/component'
import {Dashboard} from '@pihub/core/../components/dashboard'


class RssFeeds(Component):

  class RssSection(Dashboard.Section):

    data = None

    def render_dashboard_section(self):
      if not self.data:
        return 'nothing to show'
      return flask.render_template('pihub-core/rss_feed.html', data=self.data)

  def init_component(self, app):
    dashboard = app.get_component('@pihub/core:dashboard')

    self._lock = threading.RLock()
    self._feeds = {}
    for feed in getattr(app.config, 'rss_feeds', []):
      feed['section'] = self.RssSection()
      trigger = interval.IntervalTrigger(**feed['update_interval'])
      app.scheduler.add_job(partial(self.update, feed), trigger)
      dashboard.sections.append(feed['section'])
      self.update(feed)

  def update(self, feed):
    feed['section'].data = feedparser.parse(feed['url'])


module.exports = RssFeeds
