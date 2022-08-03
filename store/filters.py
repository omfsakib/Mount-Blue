import django_filters
from django_filters import DateFilter, CharFilter,MultipleChoiceFilter
from django.forms import fields
from django import forms

from store.models import *

class ProductFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="date_created", lookup_expr='gte')
    end_date = DateFilter(field_name="date_created", lookup_expr='lte')
    start_price = CharFilter(field_name="price", lookup_expr='gte')
    end_price = CharFilter(field_name="price", lookup_expr='lte')
    category =  django_filters.ModelMultipleChoiceFilter(
            queryset=Category.objects.all(),
            widget=forms.CheckboxSelectMultiple)
    size =  django_filters.ModelMultipleChoiceFilter(
            queryset=Size.objects.all(),
            widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['img','date_created']

class OrderFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="date_created", lookup_expr='gte')
    end_date = DateFilter(field_name="date_created", lookup_expr='lte')

    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['customer', 'date_created']