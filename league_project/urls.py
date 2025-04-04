from django.contrib import admin
from django.urls import path, include
from lol_app import views  # Importa las vistas de lol_app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Ruta para la página principal
    path('lol_app/', include('lol_app.urls')),  # Incluir las URLs de lol_app
]
