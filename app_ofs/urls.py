# my_login_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register, name = 'register'),
    path('dashboard', views.user_dashboard, name = 'dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('category' , views.getCategory, name = 'category'),
    # path('products' , views.products, name = 'products'),
    path('addnewproduct', views.addnewproduct, name = 'addnewproduct'),
    path('orders', views.orders, name = 'orders'),
    path('inventory', views.inventory, name = 'inventory'),
    path('category/', views.addCategory, name = 'addCategory'),
    path('category/', views.editCategory, name = 'editCategory'),
    # path('products/', views.get_categories_list, name='get_categories_list'),
    path('products/', views.addProduct, name = 'addProduct'),
    path('products' , views.getProduct, name = 'products'),
    path('products/', views.update_product, name='update_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.addOrder, name = 'addOrder'),






]
