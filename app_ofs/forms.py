from django import forms
from .models import category, Product
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

# class CategoryForm(forms.ModelForm):
#     class Meta:
#         model = category
#         fields = ['category_id', 'category']
class ProductForm(forms.ModelForm):
    # added_on = forms.DateTimeField(required=False, widget=forms.HiddenInput())
    class Meta:
        model = Product
        fields = ['product_name', 'product_description']
        


    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')

        # Capitalize the first letter of product_name
        cleaned_data['product_name'] = product_name.capitalize() if product_name else None

        return cleaned_data
    


from django import forms

class CategoryForm(forms.Form):
    category_id = forms.CharField(required=False, widget=forms.HiddenInput())
    old_category_name = forms.CharField(max_length=50, required=False)
    category = forms.CharField(max_length=50, required=False)


class AddInventoryForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label=None)
    quantity = forms.IntegerField(min_value=0)
    price = forms.DecimalField(min_value=0)

class EditInventoryForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label=None)
    quantity = forms.IntegerField(min_value=0)
    price = forms.DecimalField(min_value=0)
    operation = forms.ChoiceField(choices=[('add', 'Add Quantity'), ('deduct', 'Deduct Quantity')])