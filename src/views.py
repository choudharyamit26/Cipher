from django.shortcuts import render
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
from .models import AppUser, Message, IncorrectAttempt, Favourites, AppNotification, UserCoins
from .serializers import UserCreateSerailizer, LoginSerializer, ForgetPasswordSerializer, ComposeMessageSerializer, \
    SecretKeySerializer, ReadMessageSerializer, ProfilePicSerializer, OtpSeralizer, VerifyOtpSeralizer, \
    VerifyForgetPasswordOtpSerializer, AddToFavouritesSerializer, ResetPasswordSerializer
from adminpanel.models import User
from authy.api import AuthyApiClient
from twilio.rest import Client

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
                app_user = AppUser.objects.get(phone_number=phone_number)
                print(app_user)
                if app_user:
                    return Response(
                        {'message': "User already registered with this number", "status": HTTP_400_BAD_REQUEST})
                elif password == confirm_password:
                    request = authy_api.phones.verification_start(phone_number, country_code, via='sms', locale='en')
                    if request.content['success']:
                        return Response({'success': True, 'message': request.content['message'], 'status': HTTP_200_OK})
                    else:
                        return Response({
                            'success': False,
                            'message': request.content['message'],
                            'status': HTTP_400_BAD_REQUEST})
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
                    request = authy_api.phones.verification_start(phone_number, country_code, via='sms', locale='en')
                    if request.content['success']:
                        return Response({'success': True, 'message': request.content['message'], 'status': HTTP_200_OK})
                    else:
                        return Response({
                            'success': False,
                            'message': request.content['message'],
                            'status': HTTP_400_BAD_REQUEST})
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
            user_id = AppUser.objects.get(phone_number=phone_number).id
            check_pass = userObj.check_password(password)
            if check_pass:
                token = Token.objects.get_or_create(user=userObj)
                user_device_token = userObj.device_token
                print('previous token ', user_device_token)
                userObj.device_token = device_token
                userObj.save(update_fields=['device_token'])
                print('updated device token ', userObj.device_token)
                token = token[0]
                return Response({"Token": token.key, "id": user_id, "status": HTTP_200_OK})
            else:
                return Response({"message": "Wrong password", "status": HTTP_400_BAD_REQUEST})
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
                request = authy_api.phones.verification_start(phone_number, country_code, via='sms', locale='en')
                if request.content['success']:
                    return Response({'success': True, 'message': request.content['message'], 'status': HTTP_200_OK})
                else:
                    return Response({
                        'success': False,
                        'message': request.content['message'],
                        'status': HTTP_400_BAD_REQUEST})

                # if password == confirm_password and country_code:
                #     user.set_password(password)
                #     user.save()
                #     return Response({"message": "Your Password has been updated Successfully.", "status": HTTP_200_OK})
                # else:
                #     return Response(
                #         {"message": "Password and Confirm password did not match", "status": HTTP_400_BAD_REQUEST})
            except Exception as e:
                print(e)
                return Response({"message": "User does not exists", "status": HTTP_400_BAD_REQUEST})
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
            otp = serializer.validated_data['otp']
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            check = authy_api.phones.verification_check(phone_number, country_code, otp)
            if check.ok():
                return Response({'success': True, 'msg': check.content['message'], 'status': HTTP_200_OK})
            else:
                return Response({'success': False, 'msg': check.content['message'], 'status': HTTP_400_BAD_REQUEST})
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


class Logout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    """
    Logout API
    """

    def get(self, request, *args, **kwargs):
        # user = self.request.user
        request.user.auth_token.delete()
        return Response({"msg": "Logged out successfully", "status": HTTP_200_OK})


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
        print(self.request.data)
        serializer = ComposeMessageSerializer(data=self.request.data)
        if serializer.is_valid():
            user_obj = AppUser.objects.get(phone_number=user.phone_number)
            user_coins = UserCoins.objects.get(user=user_obj)
            print('Coins-----------', user_coins)
            if user_coins.number_of_coins > 0:
                sender = AppUser.objects.get(phone_number=user.phone_number)
                text = serializer.validated_data['text']
                validity = serializer.validated_data['validity']
                attachment = serializer.validated_data['attachment']
                receiver = serializer.validated_data['receiver']
                print(receiver)
                mode = serializer.validated_data['mode']
                ques = serializer.validated_data['ques']
                ans = serializer.validated_data['ans']
                # ques_attachment = serializer.validated_data['ques_attachment']
                msg_obj = Message.objects.create(
                    sender=sender,
                    text=text,
                    validity=validity,
                    attachment=attachment,
                    mode=mode,
                    ques=ques,
                    ans=ans,
                    # ques_attachment=ques_attachment
                )
                for obj in receiver:
                    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', obj)
                    try:
                        msg_obj.receiver.add(AppUser.objects.get(phone_number=obj))
                    except:
                        account_sid = 'AC1f8847272f073322f7b0c073e120ad7a'
                        auth_token = '1fe5e97d3658f655c5ff73949213a801'
                        client = Client(account_sid, auth_token)
                        message = client.messages.create(
                            body="Test message from quizlok using twilio",
                            from_='+19722993983',
                            # to=str(obj)
                            to='+91' + str(obj)
                        )
                print([x for x in msg_obj.receiver.all()])
                return Response({"message": "Message sent successfully", "status": HTTP_200_OK})
            else:
                return Response({"message": "You cannot send message.Insufficient coins", "status": HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class InboxView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Message
    queryset = Message.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user_obj = AppUser.objects.get(phone_number=user.phone_number)
        messages_obj = Message.objects.filter(receiver=app_user_obj.id)
        receivers = []
        for message in messages_obj:
            # print(message.receiver.all().exclude(id=app_user_obj.id))
            receivers.append({"message_id": message.id, "receiver": [
                {'receiver_id': x.id, 'name': x.username, 'country_code': x.country_code,
                 'phone_number': x.phone_number,
                 'profile_pic': x.profile_pic.url} for x in
                message.receiver.all().exclude(
                    id=app_user_obj.id)]})
        print(receivers)
        if messages_obj.count() > 0:
            return Response({'data': messages_obj.values(), 'receivers': receivers, 'status': HTTP_200_OK})
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
            app_user_obj = AppUser.objects.get(phone_number=user.phone_number)
            message_id = serializer.validated_data['message_id']
            print(message_id)
            ans = serializer.validated_data['ans']
            try:
                message_obj = Message.objects.get(id=message_id)
                print(ans is message_obj.ans)
                print('Answer>>>', ans, type(ans))
                print('Original answer>>>', message_obj.ans, type(message_obj.ans))
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
                    )
                    for receiver in message_obj.receiver.all():
                        notification.sent_to.add(receiver)
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
            app_user_obj = AppUser.objects.get(phone_number=user.phone_number)
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
        serializer = VerifyOtpSeralizer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            country_code = serializer.validated_data['country_code']
            phone_number = serializer.validated_data['phone_number']
            verification_code = serializer.validated_data['verification_code']
            password = serializer.validated_data['password']
            check = authy_api.phones.verification_check(phone_number, country_code, verification_code)
            if check.ok():
                user = AppUser.objects.create(
                    username=username,
                    country_code=country_code,
                    phone_number=phone_number,
                )
                us_obj = User.objects.create(phone_number=phone_number, email=str(phone_number) + '@email.com')
                us_obj.set_password(password)
                us_obj.save()
                token = Token.objects.get_or_create(user=us_obj)
                return Response({'token': token[0].key, 'id': user.id, 'status': HTTP_200_OK})
                # return Response({'success': True, 'msg': check.content['message']}, status=HTTP_200_OK)
            else:
                return Response({'success': False, 'msg': check.content['message']}, status=HTTP_400_BAD_REQUEST)
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
            app_user_obj = AppUser.objects.get(phone_number=user.phone_number)
            try:
                favourite = serializer.validated_data['favourite']
                Favourites.objects.create(
                    user=app_user_obj,
                    favourite=favourite
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
        app_user = AppUser.objects.get(phone_number=user.phone_number)
        favourites = Favourites.objects.filter(user=app_user)
        data = []
        for fav in favourites:
            data.append({'user_id': fav.favourite.id, 'username': fav.favourite.username,
                         'country_code': fav.favourite.country_code,
                         'phone_number': fav.favourite.phone_number})
        return Response({'data': data, 'status': HTTP_200_OK})


class GetNotificationList(ListAPIView):
    model = AppNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        app_user = AppUser.objects.get(phone_number=user.phone_number)
        notifications = AppNotification.objects.filter(user=app_user)
        receivers = []
        # for message in notifications:
        #     # print(message.receiver.all().exclude(id=app_user_obj.id))
        #     receivers.append({"message_id": message.id, "receiver": [
        #         {'receiver_id': x.id, 'name': x.username, 'country_code': x.country_code,
        #          'phone_number': x.phone_number,
        #          'profile_pic': x.profile_pic.url} for x in
        #         message.sent_to.all().exclude(
        #             id=app_user.id)]})
        return Response({'data': notifications.values(), 'status': HTTP_200_OK})


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
