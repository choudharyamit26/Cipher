import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizlok.settings')

app = Celery('quizlok')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'delete-message': {
        'task': 'src.tasks.expire_messages',
        'schedule': 10,
        # 'args': (1, 2)
    },
    'increase_coins': {
        'task': 'src.tasks.increase_coins',
        'schedule': crontab(hour=8, minute=53),
        # 'schedule': crontab(minute=11, hour='*/13'),
        # 'schedule': crontab(second=5),crontab(minute=0, hour='*/6')
        # 'schedule': 10,
        # 'args': (3, 4)
    }
}
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
