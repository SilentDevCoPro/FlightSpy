from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['dump1090_collector'])


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
