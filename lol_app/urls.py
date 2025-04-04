from django.urls import path
from . import views

urlpatterns = [
    path('champions/', views.champion_list, name='champion_list'),
]
