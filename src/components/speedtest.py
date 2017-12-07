"""
Checks your network performance using Speedtest.net.
"""

__component_meta__ = {
  'requires': [
    '@pihub/core/components/dashboard',
    '@pihub/core/components/scheduler',
  ],
  'database_revision': 1
}

import dateutil.tz
import datetime
import json
import pyspeedtest

import {app, config, database} from '@pihub/core'
import scheduler from '@pihub/core/components/scheduler'

config.setdefault('timezone', None)
config.setdefault('speedtest', {})
config.speedtest.setdefault('interval', {'type': 'cron', 'minute': '*/15'})


def init_component():
  trigger = scheduler.trigger_from_config(config.speedtest['interval'])
  scheduler.schedule_job(do_speedtest, trigger)


def do_speedtest():
  start = datetime.datetime.utcnow()
  st = pyspeedtest.SpeedTest()
  host = st.host
  ping = st.ping()
  down = st.download()
  up = st.upload()
  end = datetime.datetime.utcnow()
  with database.session:
    SpeedtestRecording(start=start, end=end, host=host, ping=ping, down=down, up=up)


class SpeedtestRecording(database.DelayedEntity):
  start = database.Required(datetime.datetime)  # UTC
  end = database.Required(datetime.datetime)  # UTC
  host = database.Required(str)
  ping = database.Required(float)
  down = database.Required(float)
  up = database.Required(float)

  def to_json(self):
    return {
      'start': self.start.strftime('%F %T'),
      'end': self.end.strftime('%F %T'),
      'host': self.host,
      'ping': self.ping,
      'down': self.down,
      'up': self.up
    }


@app.route('/speedtest/data')
@database.session
def speedtest_data():
  # TODO: Max time to look back to.
  return json.dumps({
    'speedtests': [x.to_json() for x in SpeedtestRecording.select()]
  })


config.ui_routes.append('/speedtest')
