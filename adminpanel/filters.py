import django_filters
from .models import User, Payment
from django_filters import DateFilter


class UserFilter(django_filters.FilterSet):
    from_date = DateFilter(field_name='created_at', lookup_expr='gte', label='From Date')
    to_date = DateFilter(field_name='created_at', lookup_expr='lte', label='To Date')

    class Meta:
        model = User
        fields = ('from_date', 'to_date')


class TransactionFilter(django_filters.FilterSet):
    from_date = DateFilter(field_name='created_at', lookup_expr='gte', label='From Date')
    to_date = DateFilter(field_name='created_at', lookup_expr='lte', label='To Date')

    class Meta:
        model = Payment
        fields = ('from_date', 'to_date')
