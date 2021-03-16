from celery.schedules import crontab
# from celery.task import periodic_task
from celery import shared_task
from django.utils import timezone

from .fcm_notification import send_another, send_to_one
from .models import Message, AppNotification, AppUser, UserCoins, HitInADay
import datetime
import pytz

utc = pytz.UTC


# @periodic_task(run_every=crontab('minute=0, hour='*/6'))
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
                    print('From Celery Missed Messages', receiver)
                    print('-----------From missed messages', AppUser.objects.get(id=receiver.id))
                    notification = AppNotification.objects.create(
                        user=AppUser.objects.get(id=receiver.id),
                        text='Message Expired',
                        date_sent=message.created_at,
                        mode=message.mode,
                        date_expired=datetime.datetime.now(),
                        # sent_to=[x.username for x in receivers]
                    )
                    for users in receivers:
                        notification.sent_to.add(users)
                    fcm_token = AppUser.objects.get(id=receiver.id).sender.device_token
                    try:
                        data_message = {"data": {"title": "Message Missed",
                                                 "body": 'Message Expired',
                                                 "type": "messageExpired"}}
                        # data_message = json.dumps(data_message)
                        title = "Message Missed"
                        body = 'Message Expired'
                        message_type = "messageExpired"
                        respo = send_another(
                            fcm_token, title, body, message_type)
                        # respo = send_to_one(fcm_token, data_message)
                        print("FCM Response===============>0", respo)
                        # title = "Profile Update"
                        # body = "Your profile has been updated successfully"
                        # respo = send_to_one(fcm_token, title, body)
                        # print("FCM Response===============>0", respo)
                    except:
                        pass
            except Exception as e:
                print('Exception from cron job ---->>> ', e)
            # log deletion
    return "completed expiring messages at {}".format(timezone.now())


# @periodic_task(run_every=crontab(minute=0, hour='*/6'))
@shared_task
def increase_coins():
    app_users = AppUser.objects.all()
    # today = timezone.now().today()
    for user in app_users:
        user_coins = UserCoins.objects.get(user=user)
        print(user_coins.number_of_coins)
        if user_coins.number_of_coins < 50:
            user_coins.number_of_coins += 1
            user_coins.save()
    return "running increase coins function"


@shared_task
def delete_message_from_database():
    messages = Message.objects.all()
    for message in messages:
        print(message.created_at)
        if datetime.datetime.now() > message.created_at.replace(tzinfo=None) + datetime.timedelta(hours=24 * 30):
            message.delete()
    return "deleting messages from database"
