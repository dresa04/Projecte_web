from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from lol_app import views as lol_views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, password change...
    path("admin/", admin.site.urls),
    path("", lol_views.home, name="home"),  # Página pública inicial
    path("lol_app/", include("lol_app.urls")),  # Rutas de tu app
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="registration/logged_out.html"), name="logout"),
    path("register/", lol_views.register, name="register"),
]
