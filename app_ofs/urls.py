# my_login_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register, name = 'register'),
    path('dashboard', views.user_dashboard, name = 'dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('category' , views.category, name = 'category'),
    path('products' , views.products, name = 'products'),
    path('addnewproduct', views.addnewproduct, name = 'addnewproduct'),
    path('orders', views.orders, name = 'orders')

]
