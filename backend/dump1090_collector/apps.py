from django.apps import AppConfig
import sys
import os


class Dump1090CollectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dump1090_collector'

    def ready(self):
        if self.is_celery_worker() and self.is_main_process():
            self.start_task()

    def is_celery_worker(self):
        # Check if running in Celery context
        return 'celery' in sys.argv[0] or os.environ.get('CELERY_WORKER_RUNNING') == '1'

    def is_main_process(self):
        # Prevent duplicate initialization in forked workers
        return os.environ.get('WORKER_MAIN_PID') == str(os.getpid())

    def start_task(self):
        from .tasks import poll_dump1090_task
        poll_dump1090_task.delay()
