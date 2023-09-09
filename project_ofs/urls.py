# my_login_project/urls.py
from django.contrib import admin
from django.urls import path, include  # Import the include function

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_ofs.urls')),  # Include app-specific URLs here
]
