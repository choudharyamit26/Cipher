from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime

MODE = (
    ('Direct', 'Direct'),
    ('Everybody', 'Everybody'),
    ('Race', 'Race')
)


class AppUser(models.Model):
    username = models.CharField(default='first name', max_length=100)
    country_code = models.CharField(default='+91', max_length=10)
    phone_number = models.CharField(default='', max_length=13)
    password = models.CharField(default='123456', max_length=100)
    profile_pic = models.ImageField(default='default_profile.png', null=True, blank=True)
    device_token = models.CharField(default='', max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    name = models.CharField(default='', max_length=300)
    number = models.IntegerField()


class UserContact(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    contacts = models.ManyToManyField(Contact)


class Message(models.Model):
    sender = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='message_sender')
    receiver = models.ManyToManyField(AppUser, related_name='message_receiver')
    read_by = models.ManyToManyField(AppUser, related_name='message_read_by', blank=True)
    text = models.TextField()
    attachment = models.FileField(null=True, blank=True)
    # number_of_tries = models.IntegerField()
    validity = models.IntegerField()
    mode = models.CharField(default='', max_length=100)
    ques = models.TextField(default='')
    ans = models.TextField(default='')
    # ques_attachment = models.FileField(null=True, blank=True)
    incorrect_attempts_by = models.ManyToManyField(AppUser, related_name='incorrect_attempts', blank=True)
    correct_attempts_by = models.ManyToManyField(AppUser, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_missed = models.BooleanField(default=False)


class UnRegisteredMessage(models.Model):
    phone_number = models.CharField(default='', max_length=20)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)


class IncorrectAttempt(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE)
    count = models.IntegerField()


class ReadMessage(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)


class SecretKey(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    ques = models.TextField()
    ans = models.TextField()
    attachment = models.FileField()
    # incorrect_attempts_by = models.ManyToManyField(AppUser, related_name='incorrect_attempts')
    # correct_attempts_by = models.ManyToManyField(AppUser)


class Favourites(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    favourite = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='favourite_user')


class AppNotification(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    title = models.CharField(default='', max_length=1000, null=True, blank=True)
    date_read = models.DateTimeField(auto_now_add=True)
    date_sent = models.DateField(null=True, blank=True)
    date_expired = models.DateField(null=True, blank=True)
    mode = models.CharField(default='', max_length=100)
    # on = models.BooleanField(default=True)
    read = models.BooleanField(default=False)
    sent_to = models.ManyToManyField(AppUser, related_name='sent_to')


class AppNotificationSetting(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    on = models.BooleanField(default=True)


class UserCoins(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    number_of_coins = models.IntegerField(default=5)


class HitInADay(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    day = models.DateTimeField(auto_now_add=True)
    number = models.IntegerField()


class UserOtp(models.Model):
    phone_number = models.CharField(max_length=100)
    otp = models.CharField(max_length=5)


class Transactions(models.Model):
    user = models.ForeignKey(AppUser, null=True, on_delete=models.SET_NULL)
    transaction_id = models.CharField(default='', max_length=256)
    coins = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=AppUser)
def user_coins(sender, instance, created, **kwargs):
    if created:
        user_id = instance.id
        user = AppUser.objects.get(id=user_id)
        UserCoins.objects.create(
            user=user,
            number_of_coins=5
        )
        AppNotificationSetting.objects.create(
            user=user,
            on=True
        )
    # @property
    # def delete_object_periodically(self):
    #     # time = self.created_at + datetime.timedelta(seconds=5)
    #     if self.created_at < datetime.datetime.now()-datetime.timedelta(seconds=5):
    #         e = Message.objects.get(pk=self.pk)
    #         e.delete()
    #         return print(f'Deleted object with id {self.pk}')
    #     else:
    #         return print('inside else case')
