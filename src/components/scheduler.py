"""
This component provides an #apscheduler.BackgroundScheduler for anyone
that needs it.
"""

import json
import {app, config} from '@pihub/core'

config.setdefault('enable_scheduler_overview', True)

if config.enable_scheduler_overview:
  __component_meta__ = {
    'requires': [
      '@pihub/core/components/dashboard'
    ]
  }
else:
  __component_meta__ = {
    'web_module': None
  }

# TODO: Use GeventScheduler if PiHub is running with gunicorn and gevent?

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger as date
from apscheduler.triggers.cron import CronTrigger as cron
from apscheduler.triggers.interval import IntervalTrigger as interval

scheduler = BackgroundScheduler()

def schedule_func(*args, **kwargs):
  return scheduler.scheduled_job(*args, **kwargs)

def schedule_job(*args, **kwargs):
  return scheduler.add_job(*args, **kwargs)

def remove_job(*args, **kwargs):
  return scheduler.remove_job(*args, **kwargs)

def init_component():
  scheduler.start()


@app.route('/scheduler/jobs', methods=['GET'], endpoint='scheduler_jobs')
def __scheduler_jobs():
  jobs = []
  for job in scheduler.get_jobs():
    # TODO: The apscheduler docs say that these members exist on the Job ...
    next_run_time = getattr(job, 'next_run_time', None)
    if next_run_time:
      next_run_time = next_run_time.strftime('%F %T')
    jobs.append({
      'id': job.id,
      'name': job.name,
      'trigger': str(job.trigger),
      'executor': str(job.executor),
      'misfire_grace_time': getattr(job, 'misfire_grace_time', None),
      'max_instances': getattr(job, 'max_instances', None),
      'next_run_time': next_run_time
    })
  return json.dumps({
    'jobs': jobs,
  })


config.ui_routes.append('/scheduler')
