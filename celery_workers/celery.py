from __future__ import absolute_import, unicode_literals

from celery import Celery

# Load conf
from celery_workers.celery_conf import service_bus_broker

app = Celery('celery_workers',
             broker=service_bus_broker,
             backend='rpc://',
             include=['celery_workers.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
