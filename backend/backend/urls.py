from usuarios.views import *
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('django/', admin.site.urls),

    path('dangan.api/', include('api.urls')),
]
