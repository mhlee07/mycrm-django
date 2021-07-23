from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Customer, Product, Order


PRODUCT_CHOICES = Product.objects.all().values_list('name', 'name')
product_list = []
for item in PRODUCT_CHOICES:
    product_list.append(item)


class CustomerForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'inventory']


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['product'].disabled = True
        self.fields['quantity'].disabled = True

    class Meta:
        model = Order
        fields = ['product', 'quantity', 'status']
        widgets = {
            'product': forms.Select(choices=product_list),
        }


class UserCreationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    })
    )
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    })
    )
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Re-enter Password'
    })
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone', 'email', 'address']
