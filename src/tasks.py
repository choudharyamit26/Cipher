from celery.schedules import crontab
# from celery.task import periodic_task
from celery import shared_task
from django.utils import timezone

from .fcm_notification import send_another, send_to_one
from .models import Message, AppNotification, AppUser, UserCoins, HitInADay, AppNotificationSetting, HurryNotification
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
            receivers = message.correct_attempts_by.all()
            try:
                for receiver in receivers:
                    print('From Celery Missed Messages', receiver)
                    print('-----------From missed messages', AppUser.objects.get(id=receiver.id))
                    # notification = AppNotification.objects.create(
                    #     user=AppUser.objects.get(id=receiver.id),
                    #     text='Message Expired',
                    #     date_sent=message.created_at,
                    #     mode=message.mode,
                    #     date_expired=datetime.datetime.now(),
                    #     # sent_to=[x.username for x in receivers]
                    # )
                    # for users in receivers:
                    #     notification.sent_to.add(users)
                    fcm_token = AppUser.objects.get(id=receiver.id).device_token
                    if AppNotificationSetting.objects.get(user=AppUser.objects.get(id=receiver.id)).on:
                        try:
                            if AppUser.objects.get(id=receiver.id).device_type == 'android':
                                timezone.activate(pytz.timezone(receiver.user_timezone))
                                ct = timezone.localtime(timezone.now())
                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=receiver.id),
                                    text='Message Expired',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    date_expired=ct,
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                data_message = {"title": "MESSAGE EXPIRED",
                                                "body": 'Message Expired' + ' Message Sent: ' + str(
                                                    ct.strftime("%B %d, %Y.")) + ' @ ' + str(
                                                    ct.strftime("%I:%-M%p")) + ' ' + str(
                                                    message.mode) + ':' + str(", ".join(
                                                    [x.username for x in message.correct_attempts_by.all()])),
                                                "type": "messageExpired", "sound": "notifications.mp3"}
                                respo = send_to_one(fcm_token, data_message)
                            else:
                                # data_message = json.dumps(data_message)
                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=receiver.id),
                                    text='Message Expired',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    # date_expired=datetime.datetime.now(),
                                    date_expired=ct,
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                title = "MESSAGE EXPIRED"
                                body = 'Message Expired' + ' Message Sent: ' + str(
                                    ct.strftime("%B %d, %Y.")) + ' @ ' + str(
                                    ct.strftime("%I:%-M%p")) + ' ' + str(
                                    message.mode) + ':' + str(", ".join(
                                    [x.username for x in message.correct_attempts_by.all()]))
                                message_type = "messageExpired"
                                sound = 'notifications.mp3'
                                respo = send_another(
                                    fcm_token, title, body, message_type, sound)
                                print("FCM Response===============>0", respo)
                                # title = "Profile Update"
                                # body = "Your profile has been updated successfully"
                                # respo = send_to_one(fcm_token, title, body)
                                # print("FCM Response===============>0", respo)
                        except:
                            pass
                    else:
                        pass
                sender_fcm_token = AppUser.objects.get(id=message.sender.id).device_token
                if AppNotificationSetting.objects.get(user=AppUser.objects.get(id=message.sender.id)).on:
                    try:
                        if AppUser.objects.get(id=message.sender.id).device_type == 'android':
                            timezone.activate(pytz.timezone(message.sender.user_timezone))
                            ct = timezone.localtime(timezone.now())
                            if len(message.read_by.all()) > 0:
                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=message.sender.id),
                                    text='Message Expired',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    # date_expired=datetime.datetime.now(),
                                    date_expired=ct,
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                data_message = {"title": "MESSAGE EXPIRED",
                                                "body": 'Your message expired and only ' + str(", ".join(
                                                    [x.username for x in
                                                     message.read_by.all()])) + ' read it in time.' + ' Message Sent: ' + str(
                                                    message.created_at.strftime("%B %d, %Y.")) + ' @ ' + str(
                                                    ct.strftime("%I:%-M%p")) + ' ' + str(
                                                    message.mode) + ':' + str(", ".join(
                                                    [x.username for x in message.correct_attempts_by.all()])),
                                                "type": "messageExpired", "sound": "notifications.mp3"}
                                respo = send_to_one(sender_fcm_token, data_message)
                            else:
                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=message.sender.id),
                                    text='Message Expired',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    # date_expired=datetime.datetime.now(),
                                    date_expired=ct,
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                data_message = {"title": "MESSAGE EXPIRED",
                                                "body": 'Your message expired and no one' + ' read it in time.' + ' Message Sent: ' + str(
                                                    message.created_at.strftime("%B %d, %Y.")) + ' @ ' + str(
                                                    ct.strftime("%I:%-M%p")) + ' ' + str(
                                                    message.mode) + ':' + str(", ".join(
                                                    [x.username for x in message.correct_attempts_by.all()])),
                                                "type": "messageExpired", "sound": "notifications.mp3"}
                                respo = send_to_one(sender_fcm_token, data_message)
                        else:
                            if len(message.read_by.all()) > 0:
                                timezone.activate(pytz.timezone(message.sender.user_timezone))
                                ct = timezone.localtime(timezone.now())
                                # data_message = json.dumps(data_message)
                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=message.sender.id),
                                    text='Message Expired',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    # date_expired=datetime.datetime.now(),
                                    date_expired=ct,
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                title = "MESSAGE EXPIRED"
                                body = 'Your message expired and only ' + str(", ".join(
                                    [x.username for x in
                                     message.read_by.all()])) + ' read it in time.' + ' Message Sent: ' + str(
                                    message.created_at.strftime("%B %d, %Y.")) + ' @ ' + str(
                                    ct.strftime("%I:%-M%p")) + ' ' + str(
                                    message.mode) + ':' + str(", ".join(
                                    [x.username for x in message.correct_attempts_by.all()]))
                                message_type = "messageExpired"
                                sound = 'notifications.mp3'
                                respo = send_another(
                                    sender_fcm_token, title, body, message_type, sound)
                                print("FCM Response===============>0", respo)
                            else:
                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=message.sender.id),
                                    text='Message Expired',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    # date_expired=datetime.datetime.now(),
                                    date_expired=ct,
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                title = "MESSAGE EXPIRED"
                                body = 'Your message expired and no one ' + ' read it in time.' + ' Message Sent: ' + str(
                                    message.created_at.strftime("%B %d, %Y.")) + ' @ ' + str(
                                    ct.strftime("%I:%-M%p")) + ' ' + str(
                                    message.mode) + ':' + str(", ".join(
                                    [x.username for x in message.correct_attempts_by.all()]))
                                message_type = "messageExpired"
                                sound = 'notifications.mp3'
                                respo = send_another(
                                    sender_fcm_token, title, body, message_type, sound)
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
        if user_coins.number_of_coins < 5:
            user_coins.number_of_coins += 1
            user_coins.save()
    return "running increase coins function"


@shared_task
def send_hurry_notification():
    messages = Message.objects.filter(is_missed=False)
    for message in messages:
        now_time = datetime.datetime.now()
        print(type(now_time))
        message_validity = message.created_at.replace(tzinfo=None) + datetime.timedelta(hours=message.validity)
        print(type(message_validity))
        receivers = message.correct_attempts_by.all()
        if (message_validity - now_time) < datetime.timedelta(minutes=11):
            for receiver in receivers:
                fcm_token = AppUser.objects.get(id=receiver.id).device_token
                try:
                    if not HurryNotification.objects.get(user=AppUser.objects.get(id=receiver.id),
                                                         message=Message.objects.get(id=message.id)).sent:
                        if AppNotificationSetting.objects.get(user=AppUser.objects.get(id=receiver.id)).on:
                            try:
                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=receiver.id),
                                    text=f'Act Fast! - Your message from {message.sender.username} is about to expire and be gone forever!',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    # date_expired=datetime.datetime.now(),
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                if AppUser.objects.get(id=receiver.id).device_type == 'android':
                                    data_message = {"title": "HURRY MESSAGE",
                                                    "body": f'Act Fast! - Your message from {message.sender.username} is about to expire and be gone forever!',
                                                    "type": "messageExpired", "sound": "notifications.mp3"}
                                    respo = send_to_one(fcm_token, data_message)
                                else:
                                    # data_message = json.dumps(data_message)

                                    notification = AppNotification.objects.create(
                                        user=AppUser.objects.get(id=receiver.id),
                                        text=f'Act Fast! - Your message from {message.sender.username} is about to expire and be gone forever!',
                                        date_sent=message.created_at,
                                        mode=message.mode,
                                        # date_expired=datetime.datetime.now(),
                                        # sent_to=[x.username for x in receivers]
                                    )
                                    for users in receivers:
                                        notification.sent_to.add(users)
                                    title = "HURRY MESSAGE"
                                    body = f'Act Fast! - Your message from {message.sender.username} is about to expire and be gone forever!'
                                    message_type = "messageExpired"
                                    sound = 'notifications.mp3'
                                    respo = send_another(
                                        fcm_token, title, body, message_type, sound)
                                    print("FCM Response===============>0", respo)
                                    # title = "Profile Update"
                                    # body = "Your profile has been updated successfully"
                                    # respo = send_to_one(fcm_token, title, body)
                                    # print("FCM Response===============>0", respo)
                            except:
                                pass
                    else:
                        pass
                except Exception as e:
                    HurryNotification.objects.create(user=AppUser.objects.get(id=receiver.id),
                                                     message=Message.objects.get(id=message.id), sent=True)
                    if AppNotificationSetting.objects.get(user=AppUser.objects.get(id=receiver.id)).on:
                        try:
                            if AppUser.objects.get(id=receiver.id).device_type == 'android':
                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=receiver.id),
                                    text=f'Act Fast! - Your message from {message.sender.username} is about to expire and be gone forever!',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    # date_expired=datetime.datetime.now(),
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                data_message = {"title": "HURRY MESSAGE",
                                                "body": f'Act Fast! - Your message from {message.sender.username} is about to expire and be gone forever!',
                                                "type": "messageExpired", "sound": "notifications.mp3"}
                                respo = send_to_one(fcm_token, data_message)
                            else:
                                # data_message = json.dumps(data_message)

                                notification = AppNotification.objects.create(
                                    user=AppUser.objects.get(id=receiver.id),
                                    text=f'Act Fast! - Your message from {message.sender.username} is about to expire and be gone forever!',
                                    date_sent=message.created_at,
                                    mode=message.mode,
                                    # date_expired=datetime.datetime.now(),
                                    # sent_to=[x.username for x in receivers]
                                )
                                for users in receivers:
                                    notification.sent_to.add(users)
                                title = "HURRY MESSAGE"
                                body = f'Act Fast! - Your message from {message.sender.username} is about to expire and be gone forever!'
                                message_type = "messageExpired"
                                sound = 'notifications.mp3'
                                respo = send_another(
                                    fcm_token, title, body, message_type, sound)
                                print("FCM Response===============>0", respo)
                                # title = "Profile Update"
                                # body = "Your profile has been updated successfully"
                                # respo = send_to_one(fcm_token, title, body)
                                # print("FCM Response===============>0", respo)
                        except:
                            pass
    return "sending notification"


@shared_task
def delete_message_from_database():
    messages = Message.objects.all()
    for message in messages:
        print(message.created_at)
        if datetime.datetime.now() > message.created_at.replace(tzinfo=None) + datetime.timedelta(hours=24 * 30):
            message.delete()
    return "deleting messages from database"
