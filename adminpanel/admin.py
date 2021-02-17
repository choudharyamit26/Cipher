from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import *
from src.models import *


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'),
         {'fields': (
             'first_name', 'last_name', 'profile_pic', 'country_code', 'phone_number', 'device_token', 'is_blocked',
             'remember_me')}),
        (_('Permissions'),
         {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important Dates'), {'fields': ('last_login',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'confirm_password')
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(ContactUs)
admin.site.register(TermsandCondition)
admin.site.register(PrivacyPolicy)
admin.site.register(Settings)
admin.site.register(Coin)
admin.site.register(UserContact)
admin.site.register(SecretKey)
admin.site.register(Message)
admin.site.register(Contact)
admin.site.register(AppUser)
admin.site.register(IncorrectAttempt)
admin.site.register(AppNotification)
admin.site.register(UserCoins)
admin.site.register(AppNotificationSetting)
admin.site.register(Favourites)
admin.site.register(UserNotification)
admin.site.register(HitInADay)
admin.site.register(UserOtp)
admin.site.register(UnRegisteredMessage)
