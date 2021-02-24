from .views import CreateUser, LoginView, SendOtpTwilio, ForgetPasswordAPIView, Logout, ComposeMessage, InboxView, \
    ReadingMessage, UpdateProfilePic, VerifyOtp, CustomMessage, VerifyForgetPasswordOtp, UsersList, AddToFavourites, \
    GetFavourites, GetNotificationList, ResetPasswordAPIView, DeleteUserAccount, TermsAndConditionView, \
    UpdateUserNameView, UpdateNotificationSettings, GetUserNotificationSetting, GetUserCoins, RemoveFavourite, \
    DeleteAllNotification, UnreadNotificationCount, UpdateNotificationStatus, MessageTime, GetNumberOfHitInDay, \
    GetUserProfilePic, RemoveMissedMessages,GetAttemptNumber
from django.urls import path

app_name = 'src'

urlpatterns = [
    path('user-create-otp/', CreateUser.as_view(), name='user-create-otp'),
    path('user-create-verify-otp/', VerifyOtp.as_view(), name='user-create-verify-otp'),
    path('users-list/', UsersList.as_view(), name='users-list'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='login'),
    path('forget-password-otp/', ForgetPasswordAPIView.as_view(), name='forget-password-otp'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('verify-forget-password-otp/', VerifyForgetPasswordOtp.as_view(), name='verify-forget-password-otp'),
    path('compose-message/', ComposeMessage.as_view(), name='compose-message'),
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('read-message/', ReadingMessage.as_view(), name='read-message'),
    path('update-profile-pic/<int:pk>/', UpdateProfilePic.as_view(), name='update-profile-pic'),
    path('send-otp/', SendOtpTwilio.as_view(), name='send-otp'),
    path('add-to-fav/', AddToFavourites.as_view(), name='add-to-fav'),
    path('remove-from-fav/', RemoveFavourite.as_view(), name='remove-from-fav'),
    path('fav-list/', GetFavourites.as_view(), name='fav-list'),
    path('custom-message/', CustomMessage.as_view(), name='custom-message'),
    path('notification-list/', GetNotificationList.as_view(), name='notification-list'),
    path('delete-notification-list/', DeleteAllNotification.as_view(), name='delete-notification-list'),
    path('notification-count/', UnreadNotificationCount.as_view(), name='notification-count'),
    path('update-notification/', UpdateNotificationStatus.as_view(), name='update-notification'),
    path('delete-user/', DeleteUserAccount.as_view(), name='delete-user'),
    path('terms-and-condition/', TermsAndConditionView.as_view(), name='terms-and-condition'),
    path('update-username/', UpdateUserNameView.as_view(), name='update-username'),
    path('update-notification-setting/', UpdateNotificationSettings.as_view(), name='update-notification-setting'),
    path('get-notification-setting/', GetUserNotificationSetting.as_view(), name='get-notification-setting'),
    path('get-user-coins/', GetUserCoins.as_view(), name='get-user-coins'),
    path('get-message-time/', MessageTime.as_view(), name='get-message-time'),
    path('number-of-hits/', GetNumberOfHitInDay.as_view(), name='number-of-hits'),
    path('get-profile-pic/', GetUserProfilePic.as_view(), name='get-profile-pic'),
    path('remove-missed-messages/', RemoveMissedMessages.as_view(), name='remove-missed-messages'),
    path('get-attempt-number/', GetAttemptNumber.as_view(), name='get-attempt-number'),
]
