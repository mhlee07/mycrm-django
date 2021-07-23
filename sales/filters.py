import django_filters
from .models import Order, Product


class OrderFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='order_date', lookup_expr='gt')
    end_date = django_filters.DateFilter(field_name='order_date', lookup_expr='lt')

    class Meta:
        model = Order
        fields = ['product', 'status', 'start_date', 'end_date']


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')

    class Meta:
        model = Product
        fields = ['name', 'stock', 'price__gt', 'price__lt']
