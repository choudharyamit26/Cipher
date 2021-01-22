from celery.schedules import crontab
# from celery.task import periodic_task
from celery import shared_task
from django.utils import timezone
from .models import Message, AppNotification, AppUser
import datetime
import pytz

utc = pytz.UTC


# @periodic_task(run_every=crontab(seconds='*/5'))
@shared_task
def expire_messages():
    # Query all the foos in our database
    messages = Message.objects.filter(is_missed=False)

    # Iterate through them
    for message in messages:

        # If the expiration date is bigger than now delete it
        # if message.created_at.replace(tzinfo=None) < datetime.datetime.now() - datetime.timedelta(seconds=5):
        if datetime.datetime.now() > message.created_at.replace(tzinfo=None) + datetime.timedelta(
                hours=message.validity):
            print('inside periodic task function')
            print(message.id)
            message.is_missed = True
            message.save()
            receivers = message.receiver.all()
            try:
                for receiver in receivers:
                    notification = AppNotification.objects.create(
                        user=AppUser.objects.get(phone_number=receiver),
                        text='Message Expired',
                        date_sent=message.created_at,
                        mode=message.mode,
                        date_expired=datetime.datetime.now(),
                        # sent_to=[x.username for x in receivers]
                    )
                    for users in receivers:
                        notification.sent_to.add(users)
            except Exception as e:
                print('Exception from cron job ---->>> ', e)
            # log deletion
    return "completed expiring messages at {}".format(timezone.now())


def increase_coins():
    pass