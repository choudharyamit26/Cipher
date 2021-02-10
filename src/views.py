import json
from random import randint

from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import AppUser, Message, IncorrectAttempt, Favourites, AppNotification, UserCoins, AppNotificationSetting, \
    HitInADay, UserOtp
from .serializers import UserCreateSerailizer, LoginSerializer, ForgetPasswordSerializer, ComposeMessageSerializer, \
    SecretKeySerializer, ReadMessageSerializer, ProfilePicSerializer, OtpSeralizer, VerifyOtpSeralizer, \
    VerifyForgetPasswordOtpSerializer, AddToFavouritesSerializer, ResetPasswordSerializer, UpdateUserNameSerializer, \
    UpdateNotificationSettingsSerializer, RemoveFavouritesSerializer
from adminpanel.models import User, TermsandCondition, UserNotification
from authy.api import AuthyApiClient
from twilio.rest import Client
from .fcm_notification import send_to_one, send_another

# Production key from authy app in twilio

authy_api = AuthyApiClient('SpLBdknBezXVTlD6s2gxbXgH4NzqUDcv')


class CreateUser(APIView):
    '''
    Enter username,country code,phone number and password to register
    username : String,
    country code : Integer,
    phone number : Integer,
    password : String,
    '''
    model = AppUser
    serializer_class = UserCreateSerailizer

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerailizer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            confirm_password = serializer.validated_data['confirm_password']
            try:
                print('inside try block------')
                app_user = AppUser.objects.get(phone_number=int(str(country_code)+str(phone_number)))
                print(app_user)
                if app_user:
                    return Response(
                        {'message': "User already registered with this number", "status": HTTP_400_BAD_REQUEST})
                elif password == confirm_password:
                    otp = randint(1000, 9999)
                    account_sid = 'AC1f8847272f073322f7b0c073e120ad7a'
                    auth_token = '1fe5e97d3658f655c5ff73949213a801'
                    client = Client(account_sid, auth_token)
                    client.messages.create(
                        body=str(otp),
                        from_='+19722993983',
                        to='+' + str(str(int(country_code)) + phone_number)
                    )
                    UserOtp.objects.create(
                        phone_number=str(phone_number),
                        otp=str(otp)
                    )
                    # request = authy_api.phones.verification_start(phone_number, country_code, via='sms', locale='en')
                    # if request.content['success']:
                    #     return Response({'success': True, 'message': request.content['message'], 'status': HTTP_200_OK})
                    # else:
                    #     return Response({
                    #         'success': False,
                    #         'message': request.content['message'],
                    #         'status': HTTP_400_BAD_REQUEST})
                else:
                    return Response(
                        {'message': "Password and Confirm Password do not match", "status": HTTP_400_BAD_REQUEST})
                    # user = AppUser.objects.create(
                    #     username=username,
                    #     country_code=country_code,
                    #     phone_number=phone_number,
                    # )
                    # us_obj = User.objects.create(phone_number=phone_number, email=str(phone_number) + '@email.com')
                    # token = Token.objects.get_or_create(user=us_obj)
                    # return Response({'data': serializer.data, 'token': token[0].key, 'status': HTTP_200_OK})
            except Exception as e:
                print(e)
                if password == confirm_password:
                    otp = randint(1000, 9999)
                    account_sid = 'AC1f8847272f073322f7b0c073e120ad7a'
                    auth_token = '1fe5e97d3658f655c5ff73949213a801'
                    client = Client(account_sid, auth_token)
                    client.messages.create(
                        body='Your quizlok verification code is: ' + str(otp),
                        from_='+19722993983',
                        to='+' + str(str(int(country_code)) + str(phone_number))
                    )
                    UserOtp.objects.create(
                        phone_number=str(phone_number),
                        otp=str(otp)
                    )
                    return Response(
                        {'success': True, 'message': f'Text message sent to +{country_code} {phone_number}.',
                         'status': HTTP_200_OK})
                # request = authy_api.phones.verification_start(phone_number, country_code, via='sms', locale='en')
                # if request.content['success']:
                #     return Response({'success': True, 'message': request.content['message'], 'status': HTTP_200_OK})
                # else:
                #     return Response({
                #         'success': False,
                #         'message': request.content['message'],
                #         'status': HTTP_400_BAD_REQUEST})
                else:
                    return Response(
                        {'message': "Password and Confirm Password do not match", "status": HTTP_400_BAD_REQUEST})
                # user = AppUser.objects.create(
                #     username=username,
                #     country_code=country_code,
                #     phone_number=phone_number,
                #     password=password
                # )
                # # user.set_password(password)
                # # user.save()
                # us_obj = User.objects.create(phone_number=phone_number, email=str(phone_number) + '.email.com')
                # us_obj.set_password(password)
                # us_obj.save()
                # token = Token.objects.get_or_create(user=us_obj)
                # return Response({'data': serializer.data, 'token': token[0].key, 'status': HTTP_200_OK})
        else:
            return Response({'error': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class LoginView(ObtainAuthToken):
    '''
    Enter country code,phone number and password to login
    country code : Integer,
    Phone Number : Integer,
    Password : String
    '''
    serializer_class = LoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        country_code = self.request.data['country_code']
        phone_number = self.request.data['phone_number']
        password = self.request.data['password']
        device_token = self.request.data['device_token']
        x = {}
        try:
            # user = User.objects.get(phone_number=phone_number)
            # if user:
            #     token = Token.objects.get_or_create(user=user)
            #     print(token)
            #     print(token[0].key)
            #     return Response({'token': token[0].key, 'id': user.id, 'status': HTTP_200_OK})
            userObj = User.objects.get(phone_number=phone_number)
            user_id = AppUser.objects.get(phone_number=int(str(country_code) + str(phone_number)))
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>', '+' + user_id.country_code)
            if ('+' + user_id.country_code) == country_code:
                check_pass = userObj.check_password(password)
                if check_pass:
                    # request.user.auth_token.delete()
                    try:
                        existing_token = Token.objects.get(user=userObj)
                        existing_token.delete()
                        token = Token.objects.get_or_create(user=userObj)
                        user_device_token = user_id.device_token
                        print('previous token ', user_device_token)
                        user_id.device_token = device_token
                        user_id.save(update_fields=['device_token'])
                        print('updated device token ', userObj.device_token)
                        token = token[0]
                        return Response({"token": token.key, "id": user_id.id, 'username': user_id.username,
                                         'country_code': user_id.country_code,
                                         'phone_number': user_id.phone_number, "status": HTTP_200_OK})
                    except Exception as e:
                        token = Token.objects.get_or_create(user=userObj)
                        user_device_token = user_id.device_token
                        print('previous token ', user_device_token)
                        user_id.device_token = device_token
                        user_id.save(update_fields=['device_token'])
                        print('updated device token ', userObj.device_token)
                        token = token[0]
                        return Response({"token": token.key, "id": user_id.id, 'username': user_id.username,
                                         'country_code': user_id.country_code,
                                         'phone_number': user_id.phone_number, "status": HTTP_200_OK})
                else:
                    return Response({"message": "Wrong password", "status": HTTP_400_BAD_REQUEST})
            else:
                return Response({"message": "Wrong country code", "status": HTTP_400_BAD_REQUEST})
        except Exception as e:
            x = {"Error": str(e)}
            return Response({'message': x['Error'], "status": HTTP_400_BAD_REQUEST})


@method_decorator(csrf_exempt, name='dispatch')
class ForgetPasswordAPIView(CreateAPIView):
    """
    Enter country code,phone number to get an otp to start forget password.
    Country Code : String,
    Phone Number : Integer,
    """
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ForgetPasswordSerializer(data=self.request.data)
        data = self.request.data
        if serializer.is_valid():
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            # password = serializer.validated_data['password']
            # confirm_password = data['confirm_password']
            try:
                user = User.objects.get(phone_number=phone_number)
                otp = randint(1000, 9999)
                account_sid = 'AC1f8847272f073322f7b0c073e120ad7a'
                auth_token = '1fe5e97d3658f655c5ff73949213a801'
                client = Client(account_sid, auth_token)
                client.messages.create(
                    body='Your quizlok verification code is: ' + str(otp),
                    from_='+19722993983',
                    to='+' + str(str(int(country_code)) + str(phone_number))
                )
                UserOtp.objects.create(
                    phone_number=str(phone_number),
                    otp=str(otp)
                )
                return Response({'success': True, 'message': f'Text message sent to +{country_code} {phone_number}.',
                                 'status': HTTP_200_OK})
            except Exception as e:
                print(e)
                x = {'error': str(e)}
                return Response({"message": x['error'], "status": HTTP_400_BAD_REQUEST})
        else:
            return Response({"message": serializer.errors, "status": HTTP_400_BAD_REQUEST})


@method_decorator(csrf_exempt, name='dispatch')
class VerifyForgetPasswordOtp(CreateAPIView):
    """
    Verify forget password otp and reset password
    otp:Integer
    country_code:Integer
    phone_number:Integer
    """
    serializer_class = VerifyForgetPasswordOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = VerifyForgetPasswordOtpSerializer(data=self.request.data)
        if serializer.is_valid():
            input_otp = serializer.validated_data['otp']
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            try:
                otp = UserOtp.objects.filter(phone_number=phone_number).last()
                print(otp.otp)
                print(otp)
                if int(otp.otp) == int(input_otp):
                    for otp in UserOtp.objects.filter(phone_number=phone_number):
                        otp.delete()
                    return Response({'success': True, 'msg': 'Verification code is correct.', 'status': HTTP_200_OK})
                else:
                    return Response(
                        {'success': False, 'msg': 'Verification code is incorrect.', 'status': HTTP_400_BAD_REQUEST})
            except Exception as e:
                print(e)
                return Response({'message': 'No pending verification found.', 'status': HTTP_400_BAD_REQUEST})

        # check = authy_api.phones.verification_check(phone_number, country_code, otp)
        # if check.ok():
        #     return Response({'success': True, 'msg': check.content['message'], 'status': HTTP_200_OK})
        # else:
        #     return Response({'success': False, 'msg': check.content['message'], 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordAPIView(CreateAPIView):
    """
    Forget password api.
    Enter country code and phone number to reset password.
    """
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        data = self.request.data
        # country_code = data['country_code']
        serializer = ResetPasswordSerializer(data=self.request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            confirm_password = serializer.validated_data['confirm_password']
            try:
                user = User.objects.get(phone_number=phone_number)
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    return Response({"message": "Password updated successfully", "status": HTTP_200_OK})
                else:
                    return Response(
                        {"message": "Password and Confirm password did not match", "status": HTTP_400_BAD_REQUEST})
            except Exception as e:
                x = {'error': str(e)}
                return Response({"message": x['error'], "status": HTTP_400_BAD_REQUEST})
        else:
            return Response({'error': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class ComposeMessage(CreateAPIView):
    """
    Compose message for users
    text:string,
    validity:integer,
    attachment:filetype,
    receiver:array,
    mode:string,
    ques:string,
    ans:string,
    ques_attachment:filetype
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ComposeMessageSerializer
    model = Message

    def post(self, request, *args, **kwargs):
        user = self.request.user
        print(user)
        print('Request Data----->>', self.request.data['receiver'])
        print('Request Data----->>', self.request.data)
        print('Request Data----->>', type(self.request.data['receiver']))

        serializer = ComposeMessageSerializer(data=self.request.data)
        if serializer.is_valid():
            user_obj = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
            user_coins = UserCoins.objects.get(user=user_obj)
            print('Coins-----------', user_coins)
            if user_coins.number_of_coins > 0:
                sender = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
                text = serializer.validated_data['text']
                validity = serializer.validated_data['validity']
                # attachment = serializer.validated_data['attachment']
                attachment = ''
                receiver = serializer.validated_data['receiver']
                print(receiver)
                mode = serializer.validated_data['mode']
                ques = serializer.validated_data['ques']
                ans = serializer.validated_data['ans']
                # ques_attachment = serializer.validated_data['ques_attachment']
                # for x in json.loads(serializer.validated_data['receiver']):
                #     for x in serializer.validated_data['receiver']:
                #     print('>>>>>>>>>>>>>>>>>>>>>>>>>>>-----', x)
                if attachment:
                    msg_obj = Message.objects.create(
                        sender=sender,
                        text=text,
                        validity=validity,
                        # attachment=attachment,
                        mode=mode,
                        ques=ques,
                        ans=ans,
                        # ques_attachment=ques_attachment
                    )
                    for obj in json.loads(serializer.validated_data['receiver']):
                        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', obj)
                        try:
                            msg_obj.receiver.add(AppUser.objects.get(phone_number=obj))
                            fcm_token = AppUser.objects.get(phone_number=obj).device_token
                            AppNotification.objects.create(
                                user=AppUser.objects.get(phone_number=obj),
                                text='You have a new message'
                            )
                            print(AppNotificationSetting.objects.get(user=AppUser.objects.get(phone_number=obj)).on)
                            if AppNotificationSetting.objects.get(user=AppUser.objects.get(phone_number=obj)).on:
                                try:
                                    data_message = {"data": {"title": "New Message",
                                                             "body": "You have a new message",
                                                             "type": "NewMessage"}}
                                    # data_message = json.dumps(data_message)
                                    title = "New Message"
                                    body = "You have a new message"
                                    message_type = "NewMessage"
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
                            else:
                                pass
                        except:
                            account_sid = 'AC1f8847272f073322f7b0c073e120ad7a'
                            auth_token = '1fe5e97d3658f655c5ff73949213a801'
                            client = Client(account_sid, auth_token)
                            message = client.messages.create(
                                body="You received a secret message from {}. Click here to read it.https://quizlock.page.link/mVFa".format(
                                    sender.username),
                                from_='+19722993983',
                                to='+' + str(obj)
                            )
                    print([x for x in msg_obj.receiver.all()])
                    user_coins.number_of_coins -= 1
                    user_coins.save()
                    return Response({"message": "Message sent successfully", "status": HTTP_200_OK})
                else:
                    msg_obj = Message.objects.create(
                        sender=sender,
                        text=text,
                        validity=validity,
                        # attachment=attachment,
                        mode=mode,
                        ques=ques,
                        ans=ans,
                        # ques_attachment=ques_attachment
                    )
                    for obj in json.loads(serializer.validated_data['receiver']):
                        # for obj in serializer.validated_data['receiver']:
                        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', obj)
                        try:
                            print('inside try block')
                            # msg_obj.receiver.add(AppUser.objects.get(phone_number=obj))
                            u = AppUser.objects.get(phone_number=obj)
                            print(u)
                            msg_obj.receiver.add(u)
                            fcm_token = AppUser.objects.get(phone_number=obj).device_token
                            AppNotification.objects.create(
                                user=AppUser.objects.get(phone_number=obj),
                                text='You have a new message'
                            )
                            if AppNotificationSetting.objects.get(user=AppUser.objects.get(phone_number=obj)).on:
                                try:
                                    data_message = {"Notification": {"title": "New Message",
                                                                     "body": "You have a new message",
                                                                     "type": "NewMessage"}}
                                    # data_message = json.dumps(data_message)
                                    title = "New Message"
                                    body = "You have a new message"
                                    message_type = "NewMessage"
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
                            else:
                                pass
                            print([x for x in msg_obj.receiver.all()])
                        except:
                            account_sid = 'AC1f8847272f073322f7b0c073e120ad7a'
                            auth_token = '1fe5e97d3658f655c5ff73949213a801'
                            client = Client(account_sid, auth_token)
                            message = client.messages.create(
                                body="You received a secret message from {}. Click here to read it.https://quizlock.page.link/mVFa".format(
                                    sender.username),
                                from_='+19722993983',
                                to='+' + str(obj)
                            )
                    print([x for x in msg_obj.receiver.all()])
                    user_coins.number_of_coins -= 1
                    user_coins.save()
                    return Response({"message": "Message sent successfully", "status": HTTP_200_OK})
            else:
                return Response(
                    {"message": "You cannot send message.Insufficient coins", "status": HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class InboxView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Message
    queryset = Message.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user_obj = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        messages_obj = Message.objects.filter(receiver=app_user_obj.id)
        receivers = []
        messages_values = []
        for message in messages_obj:
            # print(message.receiver.all().exclude(id=app_user_obj.id))
            if message.attachment:
                messages_values.append(
                    {'id': message.id, 'sender_id': message.id, 'sender_name': message.sender.username,
                     'sender_country_code': message.sender.country_code,
                     'sender_profile_pic': message.sender.profile_pic.url,
                     'sender_phone_number': message.sender.phone_number, 'mode': message.mode, 'question': message.ques,
                     'answer': message.ans, 'created_at': message.created_at, 'missed': message.is_missed,
                     'message_text': message.text, 'message_attachment': message.attachment.url,
                     'validity': message.validity})
            else:
                messages_values.append(
                    {'id': message.id, 'sender_id': message.id, 'sender_name': message.sender.username,
                     'sender_country_code': message.sender.country_code,
                     'sender_profile_pic': message.sender.profile_pic.url,
                     'sender_phone_number': message.sender.phone_number, 'mode': message.mode, 'question': message.ques,
                     'answer': message.ans, 'created_at': message.created_at, 'missed': message.is_missed,
                     'message_text': message.text, 'message_attachment': '', 'validity': message.validity})

            receivers.append({"receiver": [
                {'receiver_id': x.id, 'name': x.username, 'country_code': x.country_code,
                 'phone_number': x.phone_number,
                 'profile_pic': x.profile_pic.url} for x in
                message.receiver.all().exclude(
                    id=app_user_obj.id)]})
        # print(receivers)
        final_data = []
        for x in zip(messages_values, receivers):
            final_data.append({'inboxData': {**x[0], **x[1]}})
        if messages_obj.count() > 0:
            # return Response({'data': [x for x in zip(messages_values, receivers)], 'status': HTTP_200_OK})
            return Response({'data': final_data, 'status': HTTP_200_OK})
        else:
            return Response({'message': 'No messages', 'status': HTTP_400_BAD_REQUEST})


class ReadingMessage(CreateAPIView):
    """
    Read messages
    message_id: Integer,
    ans:String
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ReadMessageSerializer
    model = Message

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = ReadMessageSerializer(data=self.request.data)
        if serializer.is_valid():
            app_user_obj = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
            message_id = serializer.validated_data['message_id']
            print(message_id)
            ans = serializer.validated_data['ans']
            try:
                message_obj = Message.objects.get(id=message_id)
                print(ans is message_obj.ans)
                print('Answer>>>', ans, type(ans))
                print('Original answer>>>', message_obj.ans, type(message_obj.ans))
                print('Message read by all', message_obj.read_by.all())
                print('Message read by count ', message_obj.read_by.count())
                if message_obj.mode == 'Race':
                    if message_obj.read_by.count() > 0:
                        print('Message read by all', message_obj.read_by.all())
                        print('Message read by count ', message_obj.read_by.count())
                        return Response(
                            {'message': 'You cannot read this message as it was in race mode and it was already read'})
                    else:
                        if ans == message_obj.ans:
                            message_obj.read_by.add(app_user_obj.id)
                            ###### Add notification to be sent to the sender
                            notification = AppNotification.objects.create(
                                user=message_obj.sender,
                                message=Message.objects.get(id=message_obj.id),
                                text=f'{app_user_obj.username} read your message',
                                # date_read=,
                                date_sent=message_obj.created_at,
                                mode=message_obj.mode,
                                # sent_to=sent_to.set([x.username for x in message_obj.receiver.all()])
                            )
                            # print('before sent_to.set')
                            # notification.sent_to.set([x.username for x in message_obj.receiver.all()])
                            for receiver in message_obj.receiver.all():
                                notification.sent_to.add(receiver)
                            fcm_token = message_obj.sender.device_token
                            try:
                                data_message = {"data": {"title": "Message Read",
                                                         "body": f'{app_user_obj.username} read your message',
                                                         "type": "messageRead"}}
                                # data_message = json.dumps(data_message)
                                title = "Message Read"
                                body = f'{app_user_obj.username} read your message'
                                message_type = "messageRead"
                                respo = send_another(
                                    fcm_token, title, body, message_type)
                                respo = send_to_one(fcm_token, data_message)
                                print("FCM Response===============>0", respo)
                                # title = "Profile Update"
                                # body = "Your profile has been updated successfully"
                                # respo = send_to_one(fcm_token, title, body)
                                # print("FCM Response===============>0", respo)
                            except:
                                pass
                            if message_obj.attachment:
                                # AppNotification.objects.create(
                                #     user=message_obj.sender,
                                #     text=f'{app_user_obj.username} read your message',
                                #     date_sent=message_obj.created_at,
                                #     mode=message_obj.mode
                                # )
                                return Response({"message": "Correct answer", 'message_text': message_obj.text,
                                                 'message_attachment': message_obj.attachment,
                                                 'sender_name': message_obj.sender.username, 'status': HTTP_200_OK})
                            else:
                                return Response(
                                    {"message": "Correct answer", 'message_text': message_obj.text,
                                     'sender_name': message_obj.sender.username, 'status': HTTP_200_OK})
                        else:
                            message_obj.incorrect_attempts_by.add(app_user_obj.id)
                            try:
                                incorrect_attempts = IncorrectAttempt.objects.filter(user=app_user_obj)
                                print([x.message_id.id for x in incorrect_attempts])
                                if incorrect_attempts:
                                    print('>>>>>>>>>', int(message_id) in [x.message_id.id for x in incorrect_attempts])
                                    if int(message_id) in [x.message_id.id for x in incorrect_attempts]:
                                        msg_obj = IncorrectAttempt.objects.get(message_id=message_id)
                                        if msg_obj.count < 3:
                                            msg_obj.count += 1
                                            msg_obj.save()
                                            msg_count = msg_obj.count
                                            left_attempts = 3 - msg_count
                                            return Response(
                                                {
                                                    'message': f'Incorrect answer. {left_attempts} attempts left out of 3 attempts',
                                                    'status': HTTP_400_BAD_REQUEST})
                                        else:
                                            return Response(
                                                {
                                                    'message': 'Sorry you can not see the message.You have given incorrect answer 3 times',
                                                    'status': HTTP_400_BAD_REQUEST})
                                    else:
                                        print('false case')
                                        try:
                                            IncorrectAttempt.objects.get(message_id=message_id)
                                            pass
                                        except Exception as e:
                                            IncorrectAttempt.objects.create(
                                                user=app_user_obj,
                                                message_id=Message.objects.get(id=message_id),
                                                count=1
                                            )
                                else:
                                    print('outer if')
                                    try:
                                        IncorrectAttempt.objects.get(message_id=message_id)
                                        pass
                                    except Exception as e:
                                        IncorrectAttempt.objects.create(
                                            user=app_user_obj,
                                            message_id=Message.objects.get(id=message_id),
                                            count=1
                                        )
                            except Exception as e:
                                print('inside except block', e)
                                try:
                                    IncorrectAttempt.objects.get(message_id=message_id)
                                    pass
                                except Exception as e:
                                    IncorrectAttempt.objects.create(
                                        user=app_user_obj,
                                        message_id=Message.objects.get(id=message_id),
                                        count=1
                                    )
                                # return Response({'message': 'Incorrect answer. 2 attempts left out of 3 attempts',
                                #                  'status': HTTP_400_BAD_REQUEST})

                            return Response({'message': 'Incorrect answer. 2 attempts left out of 3 attempts',
                                             'status': HTTP_400_BAD_REQUEST})
                else:
                    if ans == message_obj.ans:
                        message_obj.read_by.add(app_user_obj.id)
                        ###### Add notification to be sent to the sender
                        notification = AppNotification.objects.create(
                            user=message_obj.sender,
                            message=Message.objects.get(id=message_obj.id),
                            text=f'{app_user_obj.username} read your message',
                            # date_read=,
                            date_sent=message_obj.created_at,
                            mode=message_obj.mode,
                            # sent_to=[x.username for x in message_obj.receiver.all()]
                        )
                        # print('before second sent_to')
                        # notification.sent_to.set([x.username for x in message_obj.receiver.all()])
                        for receiver in message_obj.receiver.all():
                            notification.sent_to.add(receiver)
                        fcm_token = message_obj.sender.device_token
                        try:
                            data_message = {"data": {"title": "Message Read",
                                                     "body": f'{app_user_obj.username} read your message',
                                                     "type": "messageRead"}}
                            # data_message = json.dumps(data_message)
                            title = "Message Read"
                            body = f'{app_user_obj.username} read your message'
                            message_type = "messageRead"
                            respo = send_another(
                                fcm_token, title, body, message_type)
                            respo = send_to_one(fcm_token, data_message)
                            print("FCM Response===============>0", respo)
                            # title = "Profile Update"
                            # body = "Your profile has been updated successfully"
                            # respo = send_to_one(fcm_token, title, body)
                            # print("FCM Response===============>0", respo)
                        except:
                            pass
                        if message_obj.attachment:
                            return Response({"message": "Correct answer", 'message_text': message_obj.text,
                                             'message_attachment': message_obj.attachment,
                                             'sender_name': message_obj.sender.username, 'status': HTTP_200_OK})
                        else:
                            return Response(
                                {"message": "Correct answer", 'message_text': message_obj.text,
                                 'sender_name': message_obj.sender.username, 'status': HTTP_200_OK})
                    else:
                        message_obj.incorrect_attempts_by.add(app_user_obj.id)
                        try:
                            incorrect_attempts = IncorrectAttempt.objects.filter(user=app_user_obj)
                            print([x.message_id.id for x in incorrect_attempts])
                            if incorrect_attempts:
                                print('>>>>>>>>>', int(message_id) in [x.message_id.id for x in incorrect_attempts])
                                if int(message_id) in [x.message_id.id for x in incorrect_attempts]:
                                    msg_obj = IncorrectAttempt.objects.get(message_id=message_id)
                                    if msg_obj.count < 3:
                                        msg_obj.count += 1
                                        msg_obj.save()
                                        msg_count = msg_obj.count
                                        left_attempts = 3 - msg_count
                                        return Response(
                                            {
                                                'message': f'Incorrect answer. {left_attempts} attempts left out of 3 attempts',
                                                'status': HTTP_400_BAD_REQUEST})
                                    else:
                                        return Response(
                                            {
                                                'message': 'Sorry you can not see the message.You have given incorrect answer 3 times',
                                                'status': HTTP_400_BAD_REQUEST})
                                else:
                                    print('false case')
                                    try:
                                        IncorrectAttempt.objects.get(message_id=message_id)
                                        pass
                                    except Exception as e:
                                        IncorrectAttempt.objects.create(
                                            user=app_user_obj,
                                            message_id=Message.objects.get(id=message_id),
                                            count=1
                                        )
                            else:
                                print('outer if')
                                try:
                                    IncorrectAttempt.objects.get(message_id=message_id)
                                    pass
                                except Exception as e:
                                    IncorrectAttempt.objects.create(
                                        user=app_user_obj,
                                        message_id=Message.objects.get(id=message_id),
                                        count=1
                                    )
                        except Exception as e:
                            print('inside except block', e)
                            try:
                                IncorrectAttempt.objects.get(message_id=message_id)
                                pass
                            except Exception as e:
                                IncorrectAttempt.objects.create(
                                    user=app_user_obj,
                                    message_id=Message.objects.get(id=message_id),
                                    count=1
                                )
                            # return Response({'message': 'Incorrect answer. 2 attempts left out of 3 attempts',
                            #                  'status': HTTP_400_BAD_REQUEST})

                        return Response({'message': 'Incorrect answer. 2 attempts left out of 3 attempts',
                                         'status': HTTP_400_BAD_REQUEST})
            except Exception as e:
                x = {'error': str(e)}
                return Response({'message': x['error'], 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class UpdateProfilePic(UpdateAPIView):
    """
    Update profile pic
    profile_pic:file
    """
    model = AppUser
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfilePicSerializer
    queryset = AppUser.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        print(self.request.data)
        # app_user_obj = AppUser.objects.get(phone_number=user.phone_number)
        # profile_pic = request.data.get('profile_pic')
        # app_user_obj.profile_pic = profile_pic
        # app_user_obj.save()
        # Response({'message': 'Profile picture updated successfully', 'status': HTTP_200_OK})
        serializer = ProfilePicSerializer(data=self.request.data)
        if serializer.is_valid():
            app_user_obj = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
            profile_pic = serializer.validated_data['profile_pic']
            app_user_obj.profile_pic = profile_pic
            # app_user_obj.save()
            app_user_obj.save(update_fields=['profile_pic'])
            print('inside is valid')
            return Response(
                {'message': 'Profile picture updated successfully', 'status': HTTP_200_OK})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class SendOtpTwilio(APIView):
    serializer_class = OtpSeralizer

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        country_code = self.request.POST['country_code']
        phone_number = self.request.POST['phone_number']
        request = authy_api.phones.verification_start(phone_number, country_code, via='sms', locale='en')
        if request.content['success']:
            return Response({
                'success': True,
                'msg': request.content['message']},
                status=HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'msg': request.content['message']},
                status=HTTP_400_BAD_REQUEST)


class VerifyOtp(APIView):
    serializer_class = VerifyOtpSeralizer

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        serializer = VerifyOtpSeralizer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            verification_code = serializer.validated_data['verification_code']
            password = serializer.validated_data['password']
            device_token = serializer.validated_data['device_token']
            # check = authy_api.phones.verification_check(phone_number, country_code, verification_code)
            # if check.ok():
            try:
                otp = UserOtp.objects.filter(phone_number=phone_number).last()
                print(otp.otp)
                print(verification_code)
                if int(otp.otp) == int(verification_code):
                    user = AppUser.objects.create(
                        username=username,
                        country_code=country_code,
                        phone_number=str(country_code) + str(phone_number),
                        device_token=device_token,
                    )
                    us_obj = User.objects.create(country_code=country_code, phone_number=phone_number,
                                                 email=str(phone_number) + '@email.com')
                    us_obj.set_password(password)
                    us_obj.save()
                    # AppNotification.objects.create(
                    #     user=user,
                    #     on=True
                    # )
                    token = Token.objects.get_or_create(user=us_obj)
                    x = UserNotification.objects.create(
                        to=User.objects.get(email='quizlok52@gmail.com'),
                        title='User Creation',
                        body='New user has registered on the platform'
                    )
                    print(x)
                    for otp in UserOtp.objects.filter(phone_number=phone_number):
                        otp.delete()
                    return Response(
                        {'token': token[0].key, 'id': user.id, 'username': user.username,
                         'country_code': user.country_code,
                         'phone_number': user.phone_number, 'status': HTTP_200_OK})
                else:
                    return Response({'message': 'Incorrect Otp', 'status': HTTP_400_BAD_REQUEST})
                    # return Response({'success': True, 'msg': check.content['message']}, status=HTTP_200_OK)
            except Exception as e:
                print(e)
                x = {'error': str(e)}
                return Response({'success': False, 'msg': x['error']}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class UsersList(APIView):
    """
    List of registered users in the app
    """
    model = AppUser
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        users_list = AppUser.objects.all()
        if users_list.count() > 0:
            return Response({"data": users_list.values(), "status": HTTP_200_OK})
        else:
            return Response({'data': [], 'status': HTTP_200_OK})


class AddToFavourites(CreateAPIView):
    model = Favourites
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AddToFavouritesSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = AddToFavouritesSerializer(data=self.request.data)
        if serializer.is_valid():
            app_user_obj = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
            try:
                favourite = serializer.validated_data['favourite']
                for x in favourite:
                    favs = Favourites.objects.filter(user=app_user_obj)
                    favs_list = [x.favourite.id for x in favs]
                    print(favs_list)
                    if x in favs_list:
                        print('inside if case')
                        pass
                    else:
                        print('inside else case')
                        Favourites.objects.create(
                            user=app_user_obj,
                            favourite=AppUser.objects.get(id=x)
                        )
                return Response({'message': 'User added to favourites successfully', 'status': HTTP_200_OK})
            except Exception as e:
                print(e)
                x = {'error': str(e)}
                return Response({'message': x['error'], 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class GetFavourites(ListAPIView):
    model = Favourites
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        print(app_user)
        favourites = Favourites.objects.filter(user=app_user).distinct()
        print(favourites)
        data = []
        for fav in favourites:
            print(fav.favourite.id)
            if fav.favourite.id in data:
                pass
            else:
                data.append({'user_id': fav.favourite.id, 'username': fav.favourite.username,
                             'country_code': fav.favourite.country_code,
                             'phone_number': fav.favourite.phone_number, 'profile_pic': fav.favourite.profile_pic.url})
        return Response({'data': data, 'status': HTTP_200_OK})


class RemoveFavourite(CreateAPIView):
    model = Favourites
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RemoveFavouritesSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        favourites = Favourites.objects.filter(user=app_user)
        # print('Favourites-------------------', favourites)
        serializer = RemoveFavouritesSerializer(data=self.request.data)
        if serializer.is_valid():
            favourite = serializer.validated_data['favourite']
            # print('Input----------------', favourite.id)
            try:
                fav_list = [x.favourite.id for x in favourites]
                # print('fav_obj>>>>>>> ', Favourites.objects.get(favourite=favourite).id)
                # print('Fav List<<<<<<<<<<<<<<<<', fav_list)
                # print('-----------------',favourite in fav_list)
                # print(int(favourite) in fav_list)
                if (favourite.id) in fav_list:
                    fav_obj = Favourites.objects.filter(user=app_user).get(favourite=favourite)
                    # print(fav_obj.id)
                    # print(fav_obj.favourite.id)
                    fav_obj.delete()
                    return Response({'message': 'Removed from favourites successfully', 'status': HTTP_200_OK})
                else:
                    return Response({'message': 'Invalid user', 'status': HTTP_400_BAD_REQUEST})
            except Exception as e:
                x = {'error': str(e)}
                return Response({'error': x['error'], 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'error': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class GetNotificationList(ListAPIView):
    model = AppNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        notifications = AppNotification.objects.filter(user=app_user)
        receivers = []
        for message in notifications:
            # print(message.receiver.all().exclude(id=app_user_obj.id))
            receivers.append({"receiver": [
                {'receiver_id': x.id, 'name': x.username, 'country_code': x.country_code,
                 'phone_number': x.phone_number,
                 'profile_pic': x.profile_pic.url} for x in
                message.sent_to.all().exclude(
                    id=app_user.id)]})
        # return Response({'data': notifications.values(), 'status': HTTP_200_OK})
        # print('>>>>>>>>>>>>', [x for x in zip(notifications.values(), receivers)])
        final_data = []
        for x in zip(notifications.values(), receivers):
            final_data.append({'notifications': {**x[0], **x[1]}})
        return Response({'data': final_data, 'status': HTTP_200_OK})


class DeleteAllNotification(APIView):
    model = AppNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        notifications = AppNotification.objects.filter(user=app_user)
        if notifications.count() > 0:
            for notification in notifications:
                notification.delete()
            return Response({'message': 'Notifications deleted successfully', 'status': HTTP_200_OK})
        else:
            return Response({'message': 'No notification to be deleted', 'status': HTTP_400_BAD_REQUEST})


class UpdateNotificationStatus(APIView):
    model = AppNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        notifications = AppNotification.objects.filter(user=app_user).filter(read=False)
        if notifications.count() > 0:
            for notification in notifications:
                print(notification)
                notification.read = True
                notification.save()
            return Response({'message': 'Notifications read successfully', 'status': HTTP_200_OK})
        else:
            return Response({'message': 'No unread message found', 'status': HTTP_400_BAD_REQUEST})


class UnreadNotificationCount(APIView):
    model = AppNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        notifications_count = AppNotification.objects.filter(user=app_user).filter(read=False).count()
        print(notifications_count)
        return Response({'count': notifications_count, 'status': HTTP_200_OK})


class Logout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({"msg": "Logged out successfully", "status": HTTP_200_OK})


class DeleteUserAccount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            user = self.request.user
            print(user.country_code)
            print(user.phone_number)
            request.user.auth_token.delete()
            user_obj = User.objects.get(phone_number=user.phone_number)
            user_obj.delete()
            app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
            app_user.delete()
            return Response({'message': 'Account deleted successfully', 'status': HTTP_200_OK})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'error': x['error'], 'status': HTTP_400_BAD_REQUEST})


class TermsAndConditionView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        t_and_c = TermsandCondition.objects.all()[0]
        return Response({'data': t_and_c.conditions, 'status': HTTP_200_OK})


class UpdateUserNameView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UpdateUserNameSerializer

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UpdateUserNameSerializer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
            app_user.username = username
            app_user.save()
            return Response({'message': 'Username updates successfully', 'status': HTTP_200_OK})
        else:
            return Response({'error': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class UpdateNotificationSettings(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UpdateNotificationSettingsSerializer

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UpdateNotificationSettingsSerializer(data=self.request.data)
        if serializer.is_valid():
            on = serializer.validated_data['on']
            app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
            settings = AppNotificationSetting.objects.get(user=app_user)
            # on = str(on).capitalize()
            # settings.on = on.capitalize()
            settings.on = on
            settings.save()
            return Response({'message': 'Update notification successfully', 'status': HTTP_200_OK})
        else:
            return Response({'error': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class GetUserNotificationSetting(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        print('---------------------------', int(str(user.country_code) + str(user.phone_number)))
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        settings = AppNotificationSetting.objects.get(user=app_user)
        print(settings.on)
        return Response(
            {'message': 'Fetched user notification settings successfully', 'value': settings.on, 'status': HTTP_200_OK})


class GetUserCoins(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        coins = UserCoins.objects.get(user=app_user)
        return Response({'message': 'Fetched users coins successfully', 'coins': coins.number_of_coins,
                         'status': HTTP_200_OK})


class GetNumberOfHitInDay(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        try:
            today = timezone.now().today()
            hits = HitInADay.objects.filter(user=app_user)
            last_hit = None
            if hits.count() > 0:
                for x in hits:
                    if str(today.date()) == str(x.day.date()):
                        x.number += 1
                        x.save()
                        last_hit = x.number
                    else:
                        print('inside else')
            else:
                hits = HitInADay.objects.create(user=app_user, number=1)
            return Response({'message': 'successful hit', 'hit_count': last_hit, 'status': HTTP_200_OK})
        except Exception as e:
            x = {'error': str(e)}
            print(x['error'])
            hits = HitInADay.objects.create(user=app_user, number=1)
            return Response({'count': hits.number, 'status': HTTP_200_OK})


class CustomMessage(APIView):

    def get(self, request, *args, **kwargs):
        from twilio.rest import Client
        account_sid = 'AC1f8847272f073322f7b0c073e120ad7a'
        auth_token = '1fe5e97d3658f655c5ff73949213a801'
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="Test message from quizlok using twilio",
            from_='+19722993983',
            to='+918279623598'
        )
        print(message)
        return Response({'message': message.sid, 'status': HTTP_200_OK})


class GetUserProfilePic(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        print('Country code ', user.country_code)
        print('Phone number ', user.phone_number)
        print(int(str(user.country_code + str(user.phone_number))))
        app_user = AppUser.objects.get(phone_number=int(str(user.country_code) + str(user.phone_number)))
        print(app_user)
        return Response({'profile_pic': app_user.profile_pic.url, 'status': HTTP_200_OK})


class MessageTime(APIView):

    def get(self, request, *args, **kwargs):
        messages = Message.objects.filter(is_missed=False)
        for message in messages:
            print(message)
            import datetime
            if datetime.datetime.now() > message.created_at.replace(tzinfo=None) + datetime.timedelta(
                    hours=message.validity):
                print('inside periodic task function')
                print('Message id', message.id)
                print('datetime now ', datetime.datetime.now())
                print('message created_at ', message.created_at)
                print('message created_at+validity ',
                      message.created_at.replace(tzinfo=None) + datetime.timedelta(hours=message.validity))
                print('Receivers---------', message.receiver)
                print('Receivers---------', [x.username for x in message.receiver.all()])
                receivers = message.receiver.all()
                try:
                    for receiver in receivers:
                        AppNotification.objects.create(
                            user=AppUser.objects.get(phone_number=receiver),
                            text='Message Expired',
                            date_sent=message.created_at,
                            mode=message.mode,
                            date_expired=datetime.datetime.now(),
                            sent_to=[x.username for x in receivers]
                        )
                except Exception as e:
                    print('Exception-------', e)
        return Response({'fetched successfully'})
