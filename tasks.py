#!/usr/bin/python
# -*- coding: utf-8 -*-

# SERVICE COMMANDS:
# celery -A tasks worker --loglevel=INFO
# celery -A tasks beat -l INFO
# celery -A tasks flower --port=5555

from celery import Celery
from celery.schedules import crontab
from modules.parsers import ParserFabric

Fabric = ParserFabric()
app = Celery('tasks',
             backend='rpc://',
             broker='pyamqp://guest@localhost//')
app.conf.timezone = 'Asia/Bangkok'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes everyday
    for portion in range(20):
        sender.add_periodic_task(
            crontab(hour=2, minute=15),
            parse_data.s(portion),
            name=f'daily parsing: {portion}',
        )


@app.task
def parse_data(portion):
    ids = Fabric.parsers_ids()
    for parser_id in ids:
        Fabric.spawn(parser_id).fetch_vacancies_portion(portion)
