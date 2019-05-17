#!/usr/bin/python
# -*- coding: utf-8 -*-

from celery import Celery
from celery.schedules import crontab
import parsers

app = Celery('tasks',
             backend='rpc://',
             broker='pyamqp://guest@localhost//')

app.conf.timezone = 'Asia/Bangkok'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
    # # Calls test('world') every 30 seconds
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every day
    for portion in range(20):
        sender.add_periodic_task(
            crontab(hour=4, minute=40),
            parse_data.s(portion),
            name=f'daily parsing: {portion}',
        )


@app.task
def test(arg):
    print(arg)


@app.task
def parse_data(portion):
    hh_parser = parsers.HhParser()
    hh_parser.fetch_vacancies_portion(portion)
