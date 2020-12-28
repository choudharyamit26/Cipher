from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import Login, Dashboard, NotificationView, UsersList, TransactionView, TermsAndConditionView, \
    UpdateTermsAndCondition, SetAdminNotificationSetting, GetAdminNotificationSetting, SendNotification, \
    UpdateContactUsView, UpdatePrivacyPolicyView, CreateCoinPlan, ListCoinPlan, UpdateCoinPlan, CoinPlanDetail, \
    NotificationCount, ReadNotifications, UserDetail, CreateUser, BlockUnblockUser, UserDelete

app_name = 'adminpanel'

urlpatterns = [
                  path('login/', Login.as_view(), name='login'),
                  path('dashboard/', Dashboard.as_view(), name='dashboard'),
                  path('notification/', NotificationView.as_view(), name='notification'),
                  path('users-list/', UsersList.as_view(), name='users-list'),
                  path('user-delete/<int:pk>/', UserDelete.as_view(), name='user-delete'),
                  path('block-unblock-user/<int:pk>/', BlockUnblockUser.as_view(), name='block-unblock-user'),
                  path('transaction/', TransactionView.as_view(), name='transaction'),
                  path('terms-and-condition/', TermsAndConditionView.as_view(), name='terms-and-condition'),
                  path('update-terms-and-condition/<int:pk>/', UpdateTermsAndCondition.as_view(),
                       name='update-terms-and-condition'),
                  path('notification-setting/', SetAdminNotificationSetting.as_view(),
                       name='notification-setting'),
                  path('get-notification-setting/', GetAdminNotificationSetting.as_view(),
                       name='get-notification-setting'),
                  path('send-notification/', SendNotification.as_view(),
                       name='send-notification'),
                  path('update-contact-us/<int:pk>/',
                       UpdateContactUsView.as_view(), name='update-contact-us'),
                  path('update-privacy-policy/<int:pk>/',
                       UpdatePrivacyPolicyView.as_view(), name='update-privacy-policy'),
                  path('create-coin-plan/', CreateCoinPlan.as_view(), name='create-coin-plan'),
                  path('coin-plan-list/', ListCoinPlan.as_view(), name='coin-plan-list'),
                  path('update-coin-plan/<int:pk>/', UpdateCoinPlan.as_view(), name='update-coin-plan'),
                  path('coin-plan-detail/<int:pk>/', CoinPlanDetail.as_view(), name='coin-plan-detail'),
                  path('user-detail/<int:pk>/', UserDetail.as_view(), name='user-detail'),
                  path('notification-count/', NotificationCount.as_view(),
                       name='notification-count'),
                  path('read-notification/', ReadNotifications.as_view(),
                       name='read-notification'),
                  path('user-create/', CreateUser.as_view(), name='user-create')
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL,
#                           document_root=settings.STATIC_ROOT)
