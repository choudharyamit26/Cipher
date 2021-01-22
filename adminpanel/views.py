from decimal import Decimal

from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import View, ListView, UpdateView, CreateView, DetailView, DeleteView

from .filters import TransactionFilter, UserFilter
from .forms import LoginForm, UpdateTnCForm, UserNotificationForm, UpdateContactusForm, UpdatePrivacyPolicyForm, \
    UpdateCoinForm, CreateCoinPlanForm
from .models import User, UserNotification, Payment, TermsandCondition, ContactUs, PrivacyPolicy, Settings, Coin
from src.models import Message, AppUser,AppNotification

from src.fcm_notification import send_another, send_to_one


user = get_user_model()


class Login(View):
    template_name = 'login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        print('Get--------Method ', self.request.COOKIES.get('cid1'))
        print('Get--------Method ', self.request.COOKIES.get('cid2'))
        print('Get--------Method ', self.request.COOKIES.get('cid3'))
        try:
            if self.request.COOKIES.get('cid1') and self.request.COOKIES.get('cid2') and self.request.COOKIES.get(
                    'cid3'):
                return render(self.request, 'login.html',
                              {'form': form, 'cookie1': self.request.COOKIES.get('cid1'),
                               'cookie2': self.request.COOKIES.get('cid2'),
                               'cookie3': self.request.COOKIES.get('cid3')})
            else:
                return render(self.request, 'login.html', {'form': form})
        except:
            return render(self.request, 'login.html', {'form': form})

        # return render(self.request, 'login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        email = self.request.POST['email']
        password = self.request.POST['password']
        remember_me = self.request.POST.get('remember_me' or None)
        print(email, password, remember_me)
        try:
            user_object = user.objects.get(email=email)
            if user_object.check_password(password):
                if user_object.is_superuser:
                    login(self.request, user_object)
                    messages.success(self.request, 'Logged in successfully')
                    # self.request.session['uid'] = self.request.POST['email']
                    if remember_me:
                        print('inside remember me')
                        cookie_age = 60 * 60 * 24
                        self.request.session.set_expiry(1209600)
                        response = HttpResponse()
                        response.set_cookie('cid1', self.request.POST['email'], max_age=cookie_age)
                        response.set_cookie('cid2', self.request.POST['password'], max_age=cookie_age)
                        response.set_cookie('cid3', self.request.POST['remember_me'], max_age=cookie_age)
                        return response
                    else:
                        self.request.session.set_expiry(0)
                    return redirect('adminpanel:dashboard')
                else:
                    messages.error(self.request, "You are not authorised")
                    # return render(self.request, 'login.html', {"status": 400})
                    return HttpResponseRedirect(self.request.path_info, status=403)
            else:
                messages.error(self.request, "Incorrect Password")
                # return render(request, 'login.html', {"status": 400})
                return HttpResponseRedirect(self.request.path_info, status=403)
                # return HttpResponseBadRequest()
        except Exception as e:
            print(e)
            messages.error(self.request, "Email doesn't exists")
            # return render(self.request, 'login.html', {"status": 400})
            return HttpResponseRedirect(self.request.path_info, status=403)


class PasswordResetConfirmView(View):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        user_id_b64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(user_id_b64).decode()
        user_object = user.objects.get(id=uid)
        token_generator = default_token_generator
        if token_generator.check_token(user_object, token):
            return render(request, 'password_reset_confirm.html')
        else:
            messages.error(request, "Link is Invalid")
            return render(request, 'password_reset_confirm.html')

    def post(self, request, *args, **kwargs):

        token = kwargs['token']
        user_id_b64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(user_id_b64).decode()
        user_object = user.objects.get(id=uid)
        token_generator = default_token_generator
        if not token_generator.check_token(user_object, token):
            messages.error(self.request, "Link is Invalid")
            return render(request, 'password_reset_confirm.html')

        password1 = self.request.POST.get('new_password1')
        password2 = self.request.POST.get('new_password2')

        if password1 != password2:
            messages.error(self.request, "Passwords do not match")
            return render(request, 'password_reset_confirm.html')
        elif len(password1) < 8:
            messages.error(
                self.request, "Password must be atleast 8 characters long")
            return render(request, 'password_reset_confirm.html')
        elif password1.isdigit() or password2.isdigit() or password1.isalpha() or password2.isalpha():
            messages.error(
                self.request, "Passwords must have a mix of numbers and characters")
            return render(request, 'password_reset_confirm.html')
        else:
            token = kwargs['token']
            user_id_b64 = kwargs['uidb64']
            uid = urlsafe_base64_decode(user_id_b64).decode()
            user_object = user.objects.get(id=uid)
            user_object.set_password(password1)
            user_object.save()
            return HttpResponseRedirect('/password-reset-complete/')


class PasswordResetView(View):
    template_name = 'password_reset.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'password_reset.html')

    def post(self, request, *args, **kwargs):
        user = get_user_model()
        email = request.POST.get('email')
        email_template = "password_reset_email.html"
        user_qs = user.objects.filter(email=email)
        if len(user_qs) == 0:
            messages.error(request, 'Email does not exists')
            return render(request, 'password_reset.html')

        elif len(user_qs) == 1:
            print('inside mail sending case')
            user_object = user_qs[0]
            email = user_object.email
            uid = urlsafe_base64_encode(force_bytes(user_object.id))
            token = default_token_generator.make_token(user_object)
            if request.is_secure():
                protocol = "https"
            else:
                protocol = "http"
            domain = request.META['HTTP_HOST']
            user = user_object
            site_name = "Quizlok"

            context = {
                "email": email,
                "uid": uid,
                "token": token,
                "protocol": protocol,
                "domain": domain,
                "user": user,
                "site_name": site_name
            }
            subject = "Reset Password Link"
            email_body = render_to_string(email_template, context)
            send_mail(subject, email_body, DEFAULT_FROM_EMAIL,
                      [email], fail_silently=False)
            print('sent email')
            return redirect('/password-reset-done/')
        else:

            user_object = user_qs[0]
            email = user_object.email
            uid = urlsafe_base64_encode(force_bytes(user_object.id))
            token = default_token_generator.make_token(user_object)
            if request.is_secure():
                protocol = "https"
            else:
                protocol = "http"
            domain = request.META['HTTP_HOST']
            user = user_object
            site_name = "Quizlok"

            context = {
                "email": email,
                "uid": uid,
                "token": token,
                "protocol": protocol,
                "domain": domain,
                "user": user,
                "site_name": site_name
            }

            subject = "Reset Password Link"
            email_body = render_to_string(email_template, context)
            send_mail(subject, email_body, DEFAULT_FROM_EMAIL,
                      [email], fail_silently=False)
            return redirect('/password-reset-done/')


class Dashboard(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard.html'
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        users_count = AppUser.objects.all().count()
        # orders_count = Payment.objects.filter(
        #     order__rejected_by_admin=False).exclude(order__status='Delivered').count()
        # revenue = Payment.objects.all()
        # total_revenue = Decimal(0)
        # cash = Decimal(0)
        # aisahawal = Decimal(0)
        # master_card = Decimal(0)
        # cash_obj = Payment.objects.filter(payment_method='cash')
        # aisahawal_obj = Payment.objects.filter(payment_method='aisa hawala')
        # master_card_obj = Payment.objects.filter(payment_method='master card')
        # for x in cash_obj:
        #     cash += x.amount
        #
        # for y in aisahawal_obj:
        #     aisahawal += y.amount
        #
        # for z in master_card_obj:
        #     master_card += z.amount
        # for amount in revenue:
        #     total_revenue += amount.amount
        opned_messages = []
        i = 0
        messages = Message.objects.all().count()
        sent_messages = Message.objects.all()
        for m in sent_messages:
            if m.read_by.exists():
                i += 1
            else:
                pass
                # opned_messages.append(m.id)
                # if m.id in opned_messages:
                #     pass
                # else:
                #     i += 1
        context = {
            'users_count': users_count,
            # 'orders_count': orders_count,
            'messages_sent': messages,
            'messages_opened': i,
            # 'cash': cash,
            # 'aisahawal': aisahawal,
            # 'master_card': master_card
        }
        return render(self.request, "dashboard.html", context)


class NotificationView(LoginRequiredMixin, ListView):
    model = UserNotification
    template_name = 'notification.html'
    login_url = 'adminpanel:login'


class UsersList(LoginRequiredMixin, ListView):
    paginate_by = 5
    model = User
    template_name = 'user-management.html'
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        qs = self.request.GET.get('qs')
        if qs:
            search = User.objects.filter(Q(first_name__icontains=qs) |
                                         Q(last_name__icontains=qs) |
                                         Q(id__icontains=qs) |
                                         Q(phone_number__icontains=qs))

            search_count = len(search)
            context = {
                'search': search,
            }
            if search:
                messages.info(self.request, str(
                    search_count) + ' matches found')
                return render(self.request, 'user-management.html', context)
            else:
                messages.info(self.request, 'No results found')
                return render(self.request, 'user-management.html', context)
        else:
            users = User.objects.all().exclude(is_superuser=True)
            myfilter = UserFilter(self.request.GET, queryset=users)
            users = myfilter.qs
            print(users.count())
            # for user in users:
            #     assigned_promocode = UserPromoCode.objects.get(user=user)
            paginator = Paginator(users, self.paginate_by)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'object_list': users,
                'myfilter': myfilter,
                'pages': page_obj,
                # 'assigned_promocode': assigned_promocode
            }
            return render(self.request, "user-management.html", context)


class TransactionView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'transaction-management.html'
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        qs = self.request.GET.get('qs')
        if qs:
            search = Payment.objects.filter(Q(payment_id__icontains=qs) |
                                            Q(payment_method__icontains=qs) |
                                            Q(amount__icontains=qs) |
                                            Q(order__id__icontains=qs) |
                                            Q(user__email__icontains=qs) |
                                            Q(created_at__icontains=qs))

            search_count = len(search)
            context = {
                'search': search,
            }
            if search:
                messages.info(self.request, str(
                    search_count) + ' matches found')
                return render(self.request, 'transaction-management.html', context)
            else:
                messages.info(self.request, 'No results found')
                return render(self.request, 'transaction-management.html', context)
        else:
            payment = Payment.objects.all()
            myfilter = TransactionFilter(self.request.GET, queryset=payment)
            payment = myfilter.qs
            # print(users.count())
            # for user in users:
            #     assigned_promocode = UserPromoCode.objects.get(user=user)
            # paginator = Paginator(users, self.paginate_by)
            # page_number = self.request.GET.get('page')
            # page_obj = paginator.get_page(page_number)
            context = {
                'object_list': payment,
                'myfilter': myfilter,
                # 'pages': page_obj,
                # 'assigned_promocode': assigned_promocode
            }
            return render(self.request, "transaction-management.html", context)


class TermsAndConditionView(LoginRequiredMixin, ListView):
    model = TermsandCondition
    template_name = 'content-management.html'
    context_object_name = 'term_condition'
    login_url = 'adminpanel:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contactus'] = ContactUs.objects.all()
        context['privacypolicy'] = PrivacyPolicy.objects.all()
        # context['promo'] = PromoCodeTermsAndCondition.objects.all()
        # context['faq'] = FAQ.objects.all().order_by('id')
        # print(FAQ.objects.all().order_by('id'))
        return context


class UpdateTermsAndCondition(LoginRequiredMixin, UpdateView):
    model = TermsandCondition
    template_name = 'update-termsandcondition.html'
    form_class = UpdateTnCForm
    success_url = reverse_lazy("adminpanel:terms-and-condition")
    login_url = 'adminpanel:login'


class SetAdminNotificationSetting(LoginRequiredMixin, View):
    model = Settings
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        user = self.request.user
        x = self.request.GET.get('notification' or None)
        print(x)
        try:
            if x == 'true':
                settingObj = Settings.objects.get(user=user)
                settingObj.notification = True
                settingObj.save()
                return HttpResponseRedirect('/change-password/')
            else:
                settingObj = Settings.objects.get(user=user)
                settingObj.notification = False
                settingObj.save()
                return HttpResponseRedirect('/change-password/')
        except Exception as e:
            print(e)


class GetAdminNotificationSetting(LoginRequiredMixin, View):
    model = Settings
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            settingObj = Settings.objects.get(user=user)
            x = settingObj.notification
            print('---------', x)
            if x:
                return HttpResponse(1)
            else:
                return HttpResponse('')
        except Exception as e:
            print(e)


class GetBlockedUnblockedUserSetting(LoginRequiredMixin, View):
    model = User
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            settingObj = User.objects.all().exclude(is_superuser=True)
            x = settingObj.notification
            print('---------', x)
            if x:
                return HttpResponse(1)
            else:
                return HttpResponse('')
        except Exception as e:
            print(e)


class SendNotification(LoginRequiredMixin, View):
    model = UserNotification
    form_class = UserNotificationForm
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        # users = User.objects.all().exclude(is_superuser=True)
        users = AppUser.objects.all()
        context = {
            "users": users
        }
        return render(self.request, 'send-notification.html', context)

    def post(self, request, *args, **kwargs):
        users_list = self.request.POST.getlist('to')
        print('From send notification --->>> ', users_list)
        title = self.request.POST['title']
        print(title)
        message = self.request.POST['body']
        print(message)
        for i in users_list:
            user = AppUser.objects.get(id=i)
            fcm_token = user.device_token
            print(fcm_token)
            AppNotification.objects.create(
                user=user,
                title=title,
                text=message,
                read=False
            )
            try:
                title = title
                body = message
                # respo = send_to_one(fcm_token, title, body)
                # print("FCM Response===============>0", respo)
                data_message = {"data": {"title": title,
                                         "body": message, "type": "adminNotification"}}
                print(title)
                print(message)
                respo = send_to_one(fcm_token, data_message)
                print(respo)
                # print("FCM Response===============>0", respo)
                message_type = "adminNotification"
                respo = send_another(fcm_token, title, message, message_type)
                print(title)
                print(message)
                print(respo)
                # fcm_token.send_message(data)
                # print("FCM Response===============>0", respo)
            except:
                pass
        messages.success(self.request, "Notification sent successfully")
        return HttpResponseRedirect(self.request.path_info)


class UpdateContactUsView(LoginRequiredMixin, UpdateView):
    model = ContactUs
    template_name = 'update-contactus.html'
    form_class = UpdateContactusForm
    success_url = reverse_lazy("adminpanel:terms-and-condition")
    login_url = 'adminpanel:login'


class UpdatePrivacyPolicyView(LoginRequiredMixin, UpdateView):
    login_url = 'adminpanel:login'
    model = PrivacyPolicy
    template_name = 'update-privacy-policy.html'
    form_class = UpdatePrivacyPolicyForm
    success_url = reverse_lazy("adminpanel:terms-and-condition")


class CreateCoinPlan(LoginRequiredMixin, CreateView):
    model = Coin
    login_url = 'adminpanel:login'
    template_name = 'create-coin.html'
    form_class = CreateCoinPlanForm
    success_url = reverse_lazy("adminpanel:coin-plan-list")

    def post(self, request, *args, **kwargs):
        number_of_coins = self.request.POST['number_of_coins']
        amount = self.request.POST['amount']
        Coin.objects.create(
            number_of_coins=number_of_coins,
            amount=amount
        )
        messages.info(self.request, 'New plan created successfully')
        return redirect("adminpanel:coin-plan-list")


class ListCoinPlan(LoginRequiredMixin, ListView):
    model = Coin
    login_url = 'adminpanel:login'
    template_name = 'coin-list.html'


class UpdateCoinPlan(LoginRequiredMixin, UpdateView):
    model = Coin
    login_url = 'adminpanel:login'
    template_name = 'update-coin.html'
    form_class = UpdateCoinForm
    success_url = reverse_lazy("adminpanel:coin-plan-list")

    def post(self, request, *args, **kwargs):
        coin_obj = Coin.objects.get(id=kwargs['pk'])
        coin_obj.number_of_coins = self.request.POST['number_of_coins']
        coin_obj.amount = self.request.POST['amount']
        coin_obj.save()
        messages.info(self.request, 'Plan updated successfully')
        return redirect("adminpanel:coin-plan-list")


class CoinPlanDetail(LoginRequiredMixin, DetailView):
    model = Coin
    login_url = 'adminpanel:login'
    template_name = 'coin-detail.html'


class NotificationCount(LoginRequiredMixin, ListView):
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        user = User.objects.get(email='quizlok52@gmail.com')
        print(user)
        count = UserNotification.objects.filter(
            to=user.id).filter(read=False).count()
        print(count)
        return HttpResponse(count)


class ReadNotifications(LoginRequiredMixin, ListView):
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        user = User.objects.get(email='quizlok52@gmail.com')
        notifications = UserNotification.objects.filter(
            to=user.id).filter(read=False)
        for obj in notifications:
            obj.read = True
            obj.save()
        return HttpResponse('Read all notifications')


class UserDetail(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user-details.html'
    login_url = 'adminpanel:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs.get('pk'))
        try:
            # address = Address.objects.filter(user=user).get(default_address=True)
            # if address:
            #     context['address'] = address
            context['promocode'] = UserPromoCode.objects.get(user=user)
        # else:
        except Exception as e:
            print(e)
            # pass
        return context


class UserDelete(LoginRequiredMixin, DeleteView):
    login_url = 'adminpanel:login'

    def get(self, request, *args, **kwargs):
        request_kwargs = kwargs
        object_id = request_kwargs['pk']
        UserObj = User.objects.get(id=object_id)
        UserObj.delete()
        messages.success(self.request, "User deleted successfully")
        return HttpResponseRedirect('/adminpanel/users-list/')


class BlockUnblockUser(View):
    model = User

    def get(self, request, *args, **kwargs):
        print(self.request.GET)
        print(args)
        print(kwargs)
        user_object = User.objects.get(id=kwargs['pk'])
        print(user_object)
        print(user_object.is_blocked)
        if user_object.is_blocked:
            user_object.is_blocked = False
            user_object.save()
        else:
            user_object.is_blocked = True
            user_object.save()
        messages.info(self.request, 'Blocked user successfully')
        return HttpResponseRedirect('/adminpanel/users-list/')


class CreateUser(View):

    def get(self, request, *args, **kwargs):
        User.objects.create(
            first_name='Test',
            last_name='User',
            email='testuser34@gmail.com',
            country_code='+91',
            phone_number='7678689355'
        )
        messages.info(self.request, 'User created')
        return redirect('adminpanel:users-list')
