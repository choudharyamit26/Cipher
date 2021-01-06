from celery.schedules import crontab
# from celery.task import periodic_task
from celery import shared_task
from django.utils import timezone
from .models import Message
import datetime
import pytz

utc = pytz.UTC


# @periodic_task(run_every=crontab(seconds='*/5'))
@shared_task
def delete_old_foos():
    # Query all the foos in our database
    foos = Message.objects.all()

    # Iterate through them
    for foo in foos:

        # If the expiration date is bigger than now delete it
        if foo.created_at.replace(tzinfo=None) < datetime.datetime.now() - datetime.timedelta(seconds=5):
            print('inside periodic task function')
            print(foo.id)
            foo.delete()
            # log deletion
    return "completed deleting foos at {}".format(timezone.now())
