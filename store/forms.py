from django.forms import ModelForm, fields
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import *

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields ='__all__'
        exclude = ['user']

class ShopOwnerForm(ModelForm):
    class Meta:
        model = ShopOwner
        fields ='__all__'
        exclude = ['user']

class OrderForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'

class UpdateOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status',]

class ProductForm(ModelForm):
    name = forms.CharField(label='Product Name',widget=forms.TextInput(attrs={'placeholder': 'Product Name'}))
    price = forms.FloatField(label='Price',widget=forms.TextInput(attrs={'placeholder': 'Price'}))
    quantity = forms.CharField(label='Quantity',widget=forms.TextInput(attrs={'placeholder': 'Quantity'}))
    description = forms.CharField(max_length=2000,label='Description',widget=forms.Textarea(attrs={'placeholder': 'Description'}))
    category = forms.ModelMultipleChoiceField(
            queryset=Category.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True)
    color = forms.ModelMultipleChoiceField(
            queryset=Color.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True)
    size = forms.ModelMultipleChoiceField(
            queryset=Size.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True)
    
    class Meta:
        model = Product
        fields = '__all__'

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

class UpdateProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields =['email','first_name','last_name','password']

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'