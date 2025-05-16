# views.py
import logging, requests
from datetime import datetime
from typing import Dict, Any

from django.shortcuts    import render, redirect, get_object_or_404
from django.http         import HttpRequest, HttpResponse, JsonResponse
from django.conf         import settings
from django.contrib.auth import login
from django.contrib.auth.forms      import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http   import require_POST, require_http_methods
from django.views.decorators.csrf   import csrf_exempt

from .models import Champion, Review, UserLOL, Match, MatchChampion

logger = logging.getLogger(__name__)

# — Constantes de la API Riot —
RIOT_ACCOUNT_API_BASE_URL   = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/'
RIOT_SUMMONER_API_BASE_URL = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/'
RIOT_API_KEY = settings.RIOT_API_KEY

def public_home(request: HttpRequest) -> HttpResponse:
    return render(request, 'homes/home.html')

@login_required
def home(request: HttpRequest) -> HttpResponse:
    reviews = Review.objects.filter(from_user=request.user)
    return render(request, 'homes/home2.html', {'reviews': reviews})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def champion_list(request: HttpRequest) -> HttpResponse:
    # … lógica para descargar/updatear campeones …
    champions = Champion.objects.all()
    return render(request, 'homes/champion_list.html', {'champions': champions})

@login_required
def review_update_list(request):
    reviews = Review.objects.filter(from_user=request.user).order_by('-timestamp')
    return render(request, 'review_update/review_update_list.html', {'reviews': reviews})

@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk, from_user=request.user)
    if request.method == 'POST':
        review.title = request.POST['title']
        review.body  = request.POST['body']
        review.save()
        return redirect('review_update_list')
    return render(request, 'review_update/review_update.html', {'review': review})

@login_required
def review_delete_list(request):
    reviews = Review.objects.filter(from_user=request.user)
    return render(request, 'review_delete/review_delete_list.html', {'reviews': reviews})

@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Review.all_objects, pk=pk, from_user=request.user)
    review.delete()
    return redirect('review_delete_list')

@login_required
def review_confirm_delete(request, pk):
    review = get_object_or_404(Review.all_objects, pk=pk, from_user=request.user)
    if request.method == 'POST':
        review.delete()
        return redirect('review_delete_list')
    return render(request, 'review_delete/review_confirm_delete.html', {'review': review})

# — Resto de endpoints (create_review, validate_summoner, get_matches_for_player) sin cambios de template —
