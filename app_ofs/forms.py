from django import forms
from .models import category, products
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class RegisterForm(UserCreationForm):
    
    class Meta:

        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email' ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            # 'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            # 'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            }
        
        
        # fields = '__all__' # to display all the fields on the dom.

class CategoryForm(forms.ModelForm):
    class Meta:
        model = category
        fields = ['category_id', 'category']

class ProductForm(forms.ModelForm):
    class Meta:
        model = products
        fields = ['product_id', 'product_name', 'product_description']