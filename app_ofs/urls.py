# my_login_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name = 'register'),
    path('dashboard', views.user_dashboard, name = 'dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('category' , views.getCategory, name = 'category'),
    path('addnewproduct', views.addnewproduct, name = 'addnewproduct'),
    path('inventory', views.inventory, name = 'inventory'),
    path('category/', views.addCategory, name = 'addCategory'),
    path('editcategory/', views.editCategory, name = 'editCategory'),
    path('products' , views.getProduct, name = 'products'),
    path('product_category', views.get_categories_list, name = 'product_category'),
    path('order_product_name', views.get_product_list, name = 'order_product_name'),
    path('products/', views.addProduct, name = 'addProduct'),
    path('editproduct/', views.editProduct, name='editProduct'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.getOrder, name = 'orders'),
    path('addorder/', views.addOrder, name = 'addOrder'),
    path('editOrder/', views.editOrder, name='editOrder'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('getProductCategory/', views.getProductCategory, name='getProductCategory'),
    path('inventory/', views.getItems, name='inventory'),
    path('addItems/', views.addItems, name='addItems'),
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('changepassword/', views.changepassword, name='changepassword'),
    path('inventorylist/<str:category_name>/', views.inventorylist, name='inventorylist'),
]
