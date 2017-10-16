"""
Checks your network performance using Speedtest.net.

# Configuration

In a dictionary named `speedtest`:

`trigger`:
  An #apscheduler.triggers.base.BaseTrigger instance.

`interval`:
  A dictionary as keyword arguments for the #apscheduler.triggers.interval
  trigger type.

`cron`:
  A dictionary as keyword arguments for the #apscheduler.triggers.cron
  trigger type. If nothing is configured, the Cron trigger will be used
  executing every hour.

`show_in_dashboard`:
  Show the collected speedtest data on the dashboard. Requires the
  `@pihub/core:dashboard` component.
"""

from apscheduler.triggers import interval, cron
from plotly.tools import make_subplots
from plotly.offline import plot
from plotly.graph_objs import Scattergl
import dateutil.tz
import datetime
import flask
import pyspeedtest
import {Component} from '@pihub/core/component'
import db from '@pihub/core/database'
import Dashboard from '@pihub/core/../components/dashboard'

default_config = {
  'cron': {'minute': '*/15'},
  'show_in_dashboard': True
}


class SpeedtestRecording(db.Entity):
  _table_ = 'pihub_core_speedtest_recording'

  # UTC Times
  date_start = db.Required(datetime.datetime)
  date_end = db.Required(datetime.datetime)
  ping = db.Required(float)
  down = db.Required(float)
  up = db.Required(float)


class Speedtest(Component, Dashboard.Section):

  def init_component(self, app):
    self.config = getattr(app.config, 'speedtest', default_config)
    if 'trigger' in self.config:
      trigger = config['trigger']
    elif 'interval' in self.config:
      trigger = interval.IntervalTrigger(**self.config['interval'])
    elif 'cron' in self.config:
      trigger = cron.CronTrigger(**self.config['cron'])
    else:
      raise ValueError('config.speedtest missing trigger information')

    app.scheduler.add_job(self.perform_speedtest, trigger)

    if self.config.get('show_in_dashboard'):
      dashboard = app.get_component('@pihub/core:dashboard')
      dashboard.sections.append(self)

  def perform_speedtest(self):
    begin = datetime.datetime.utcnow()
    st = pyspeedtest.SpeedTest()
    ping = st.ping()
    down = st.download()
    up = st.upload()
    end = datetime.datetime.utcnow()
    with db.session():
      SpeedtestRecording(date_start=begin, date_end=end, ping=ping, down=down, up=up)

  @db.session
  def render_dashboard_section(self):
    if not self.config.get('show_in_dashboard', True):
      return None
    records = list(SpeedtestRecording.select())
    tzutc = dateutil.tz.tzutc()
    tznow = dateutil.tz.gettz(self.app.config.timezone)
    dates = [r.date_start.replace(tzinfo=tzutc).astimezone(tznow) for r in records]
    fig = make_subplots(rows=1, cols=2, print_grid=False)
    fig.append_trace(
      Scattergl(
        x = dates,
        y = [r.down for r in records],
        name = 'Download'
      ),
      1, 1
    )
    fig.append_trace(
      Scattergl(
        x = dates,
        y = [r.up for r in records],
        name = 'Upload'
      ),
      1, 1
    )
    fig.append_trace(
      Scattergl(
        x = dates,
        y = [r.ping for r in records],
        name = 'Ping'
      ),
      1, 2
    )
    return flask.render_template('pihub-core/dashboard-section.html',
      title='Speedtest', content=plot(fig, output_type='div'))


module.exports = Speedtest
