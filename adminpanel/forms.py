from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth.models import User

from .models import TermsandCondition, UserNotification, ContactUs, PrivacyPolicy, Coin


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['email', 'password', 'remember_me']


class UpdateTnCForm(forms.ModelForm):
    conditions = forms.CharField(widget=CKEditorWidget())

    # conditions_in_arabic = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = TermsandCondition
        fields = ('conditions',)


class UserNotificationForm(forms.ModelForm):
    class Meta:
        model = UserNotification
        fields = ('to', 'body')


class UpdateContactusForm(forms.ModelForm):
    # phone_number = forms.CharField(widget=CKEditorWidget())
    phone_number = forms.CharField()
    # email = forms.CharField(widget=CKEditorWidget())
    email = forms.EmailField()

    class Meta:
        model = ContactUs
        fields = ('phone_number', 'email')


class UpdatePrivacyPolicyForm(forms.ModelForm):
    policy = forms.CharField(widget=CKEditorWidget())

    # policy_in_arabic = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = PrivacyPolicy
        fields = ('policy',)


class UpdateCoinForm(forms.ModelForm):
    class Meta:
        model = Coin
        fields = ('number_of_coins', 'amount')


class CreateCoinPlanForm(forms.ModelForm):
    class Meta:
        model = Coin
        fields = ('number_of_coins', 'amount')
