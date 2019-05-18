#!/usr/bin/python
# -*- coding: utf-8 -*-

# SERVICE COMMANDS:
# celery -A tasks worker --loglevel=debug
# celery -A tasks beat -l debug
# celery -A tasks flower --port=5555

from celery import Celery
from celery.schedules import crontab
from modules import parsers

app = Celery('tasks',
             backend='rpc://',
             broker='pyamqp://guest@localhost//')

app.conf.timezone = 'Asia/Bangkok'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes everyday
    for portion in range(20):
        sender.add_periodic_task(
            crontab(hour=17, minute=12),
            parse_data.s(portion),
            name=f'daily parsing: {portion}',
        )


@app.task
def parse_data(portion):
    hh_parser = parsers.HhParser()
    hh_parser.fetch_vacancies_portion(portion)
