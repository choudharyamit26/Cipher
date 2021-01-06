from .views import CreateUser, LoginView, SendOtpTwilio, ForgetPasswordAPIView, Logout, ComposeMessage, InboxView, \
    ReadingMessage, UpdateProfilePic, VerifyOtp, CustomMessage, VerifyForgetPasswordOtp, UsersList, AddToFavourites, \
    GetFavourites,GetNotificationList
from django.urls import path

app_name = 'src'

urlpatterns = [
    path('user-create-otp/', CreateUser.as_view(), name='user-create-otp'),
    path('user-create-verify-otp/', VerifyOtp.as_view(), name='user-create-verify-otp'),
    path('users-list/', UsersList.as_view(), name='users-list'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='login'),
    path('forget-password-otp/', ForgetPasswordAPIView.as_view(), name='forget-password-otp'),
    path('verify-forget-password-otp/', VerifyForgetPasswordOtp.as_view(), name='verify-forget-password-otp'),
    path('compose-message/', ComposeMessage.as_view(), name='compose-message'),
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('read-message/', ReadingMessage.as_view(), name='read-message'),
    path('update-profile-pic/<int:pk>/', UpdateProfilePic.as_view(), name='update-profile-pic'),
    path('send-otp/', SendOtpTwilio.as_view(), name='send-otp'),
    path('add-to-fav/', AddToFavourites.as_view(), name='add-to-fav'),
    path('fav-list/', GetFavourites.as_view(), name='fav-list'),
    path('custom-message/', CustomMessage.as_view(), name='custom-message'),
    path('notification-list/', GetNotificationList.as_view(), name='notification-list'),
]
