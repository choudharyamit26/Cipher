from django.db import models
from django.utils import timezone
import datetime

MODE = (
    ('Direct', 'Direct'),
    ('Everybody', 'Everybody'),
    ('Race Mode', 'Race Mode')
)


class AppUser(models.Model):
    username = models.CharField(default='first name', max_length=100)
    country_code = models.CharField(default='+91', max_length=10)
    phone_number = models.CharField(default='', max_length=13)
    password = models.CharField(default='123456', max_length=100)
    profile_pic = models.ImageField(default='goku.jpg', null=True, blank=True)


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
    mode = models.CharField(default='', choices=MODE, max_length=100)
    ques = models.TextField(default='')
    ans = models.TextField(default='')
    ques_attachment = models.FileField(null=True, blank=True)
    incorrect_attempts_by = models.ManyToManyField(AppUser, related_name='incorrect_attempts', blank=True)
    correct_attempts_by = models.ManyToManyField(AppUser, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class IncorrectAttempt(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE)
    count = models.IntegerField()


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


class UserCoins(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    number_of_coins = models.IntegerField(default=5)

    # @property
    # def delete_object_periodically(self):
    #     # time = self.created_at + datetime.timedelta(seconds=5)
    #     if self.created_at < datetime.datetime.now()-datetime.timedelta(seconds=5):
    #         e = Message.objects.get(pk=self.pk)
    #         e.delete()
    #         return print(f'Deleted object with id {self.pk}')
    #     else:
    #         return print('inside else case')
