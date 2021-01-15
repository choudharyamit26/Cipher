from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from .models import AppUser, Message, SecretKey, Favourites
from adminpanel.models import User

from django.contrib.auth import get_user_model, authenticate


class UserCreateSerailizer(serializers.ModelSerializer):
    username = serializers.CharField()
    country_code = serializers.IntegerField()
    phone_number = serializers.IntegerField()
    password = serializers.CharField(style={'input_type': 'password'})
    confirm_password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = AppUser
        fields = ('username', 'country_code', 'phone_number', 'password', 'confirm_password')


class LoginSerializer(serializers.Serializer):
    country_code = serializers.IntegerField()
    phone_number = serializers.IntegerField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        country_code = attrs.get('country_code')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=phone_number,
            password=password
        )
        attrs['user'] = user
        if user:
            attrs['user'] = user
            return attrs
        else:
            return Response("User does not exists", HTTP_400_BAD_REQUEST)


class ForgetPasswordSerializer(serializers.ModelSerializer):
    country_code = serializers.IntegerField()
    phone_number = serializers.IntegerField()

    # password = serializers.CharField(style={'input_type': 'password'})
    # confirm_password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('country_code', 'phone_number')
        # fields = ('country_code', 'phone_number', 'password', 'confirm_password')


class ResetPasswordSerializer(serializers.ModelSerializer):
    # country_code = serializers.IntegerField()
    phone_number = serializers.IntegerField()
    password = serializers.CharField(style={'input_type': 'password'})
    confirm_password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'confirm_password')


class VerifyForgetPasswordOtpSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    country_code = serializers.IntegerField()
    phone_number = serializers.IntegerField()


class ComposeMessageSerializer(serializers.ModelSerializer):
    receiver = serializers.ListField()

    # secret_key = SecretKeySerializer(many=True)

    class Meta:
        model = Message
        # fields = ('sender', 'receiver', 'text', 'attachment', 'validity', 'mode')
        # fields = '__all__'
        exclude = ('sender',)


class SecretKeySerializer(serializers.ModelSerializer):
    # message = ComposeMessageSerializer(many=True)

    class Meta:
        model = SecretKey
        fields = ('message', 'ques', 'ans', 'attachment')
        # fields = '__all__'


class ReadMessageSerializer(serializers.ModelSerializer):
    message_id = serializers.IntegerField()
    ans = serializers.CharField()

    class Meta:
        model = Message
        fields = ('message_id', 'ans')


class ProfilePicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ('profile_pic',)


class OtpSeralizer(serializers.ModelSerializer):
    phone_number = serializers.IntegerField()
    country_code = serializers.IntegerField()

    class Meta:
        model = AppUser
        fields = ('country_code', 'phone_number')


class VerifyOtpSeralizer(serializers.ModelSerializer):
    username = serializers.CharField()
    phone_number = serializers.IntegerField()
    country_code = serializers.IntegerField()
    verification_code = serializers.IntegerField()
    password = serializers.CharField()

    class Meta:
        model = AppUser
        fields = ('username', 'country_code', 'phone_number', 'verification_code', 'password')


class AddToFavouritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourites
        fields = ('favourite',)
