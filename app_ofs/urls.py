# my_login_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus', views.aboutus, name='aboutus'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register, name = 'register'),
    path('dashboard', views.user_dashboard, name = 'dashboard'),

    path('forecast/', views.forecast, name='forecast'),
    path('logout/', views.logout_view, name='logout'),
    path('category' , views.get_category, name = 'category'),
    path('addnewproduct', views.addnewproduct, name = 'addnewproduct'),
    path('inventory', views.inventory, name = 'inventory'),
    path('staff', views.staff, name = 'staff'),
    path('addStaff', views.addStaff, name = 'addStaff'),
    path('deactivatedStaff', views.deactivatedStaff, name = 'deactivatedStaff'),
    path('editStaff', views.editStaff, name='editStaff'),
    path('delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('reactivate_staff/<int:staff_id>/', views.reactivate_staff, name='reactivate_staff'),
    path('category/', views.add_category, name = 'addCategory'),
    path('editcategory/', views.edit_category, name = 'editCategory'),
    path('products' , views.getProduct, name = 'products'),
    path('product_category', views.get_categories_list, name = 'product_category'),
    path('order_product_name', views.get_product_list, name = 'order_product_name'),
    path('products/', views.addProduct, name = 'addProduct'),
    path('editproduct/', views.editProduct, name='editProduct'),
    path('delete_product/<str:product_id>/', views.delete_product, name='delete_product'),
    path('productStatistics/', views.productStatistics, name='productStatistics'),
    # path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.getOrder, name = 'orders'),
    path('addorder/', views.addOrder, name = 'addOrder'),
    path('editOrder/', views.editOrder, name='editOrder'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('getCompletedOrder/', views.getCompletedOrder, name='getCompletedOrder'),
    path('getCompletedOrder/', views.getCompletedOrder, name='getCompletedOrder'),
    path('getCancelledOrder/', views.getCancelledOrder, name='getCancelledOrder'),
    path('orderFilter/', views.order_filter, name='orderFilter'),
    # path('inventory/', views.getItems, name='inventory'),
    path('addItems/', views.addItems, name='addItems'),
    path('editItems/', views.editItems, name='editItems'),
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('changepassword/', views.changepassword, name='changepassword'),
    path('inventorylist/<str:category_name>/', views.inventorylist, name='inventorylist'),
    path('inventoryhistory/<str:category_name>/', views.inventoryhistory, name='inventoryhistory'),
    path('get-products/', views.get_products, name='get_products'),
    # path('update_product_dropdown/', views.update_product_dropdown, name='update_product_dropdown'),        
    path('get-products-by-category/', views.get_products_by_category, name='get_products_by_category'),
    # path('get-products/', views.get_products, name='get_products'),

]
