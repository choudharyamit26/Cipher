from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ User model """
    first_name = models.CharField(default='first name', max_length=100)
    last_name = models.CharField(default='', max_length=100, null=True, blank=True)
    email = models.CharField(default='', max_length=255, unique=True)
    country_code = models.CharField(default='+91', max_length=10)
    phone_number = models.CharField(default='', max_length=13)
    profile_pic = models.ImageField(default='default_profile.png', null=True, blank=True)
    # social_type = models.CharField(default='', max_length=500, null=True, blank=True)9180
    # social_id = models.CharField(default='', max_length=200, null=True, blank=True)
    device_token = models.CharField(default='', max_length=500, null=True, blank=True)
    remember_me = models.BooleanField(default=False)
    password = models.CharField(default='123456', max_length=100)
    confirm_password = models.CharField(default='123456', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('-created_at',)


class UserNotification(models.Model):
    to = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(default='title', max_length=200)
    # title_in_arabic = models.CharField(default='title', max_length=200)
    body = models.CharField(default='body', max_length=200)
    # body_in_arabic = models.CharField(default='body', max_length=200)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(default='', max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=100)
    payment_method = models.CharField(default='', max_length=100)
    operation_id = models.CharField(default='', max_length=200)
    created_at = models.DateField()

    class Meta:
        # ordering = ('-created_at',)
        ordering = ['-created_at']


class ContactUs(models.Model):
    """Contact Us model"""
    phone_number = models.CharField(default='+9199999', max_length=13)
    email = models.EmailField(default='support@snapic.com', max_length=100)


class TermsandCondition(models.Model):
    """App's Terms and condition"""
    conditions = models.TextField()
    # conditions_in_arabic = models.TextField(default='')


class PrivacyPolicy(models.Model):
    """App's privacy policy"""
    policy = models.TextField()
    # policy_in_arabic = models.TextField(default='')


class Settings(models.Model):
    """User's Settings model"""
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    notification = models.BooleanField(default=True)
    # language = models.CharField(default='English', max_length=30)


class Coin(models.Model):
    number_of_coins = models.IntegerField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


@receiver(post_save, sender=User)
def setting(sender, instance, created, **kwargs):
    if created:
        user_id = instance.id
        user = User.objects.get(id=user_id)
        setting_obj = Settings.objects.create(
            user=user,
            notification=True,
            # language='English'
        )
        return setting_obj
