from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('champions/', views.champion_list, name='champion_list'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('reviews/update/', views.review_update_list, name='review_update_list'),
    path('reviews/delete/', views.review_delete_list, name='review_delete_list'),
    path('api/validate-summoner/', views.validate_summoner, name='validate_summoner'),
    path('create-review/', views.create_review, name='create_review'),
    path('reviews/create/', views.review_create_form, name='review_create_form'),
    path('api/get-matches/', views.get_matches_for_player, name='get_matches'),
    path('reviews/update/', views.review_update_list, name='review_update_list'),
    path('reviews/update/<int:pk>/', views.review_update, name='review_update'),

]
