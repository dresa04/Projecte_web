# lol_app/views.py

import logging
import requests
from datetime import datetime
from typing import Dict, Any

from django.shortcuts            import render, redirect, get_object_or_404
from django.http                 import HttpRequest, HttpResponse, JsonResponse
from django.conf                 import settings
from django.contrib.auth         import login
from django.contrib.auth.forms   import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http   import require_POST, require_http_methods
from django.views.decorators.csrf   import csrf_exempt

from .models import Champion, Review, UserLOL, Match, MatchChampion

logger = logging.getLogger(__name__)

# Constantes para Riot API
RIOT_ACCOUNT_API_BASE_URL   = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/'
RIOT_SUMMONER_API_BASE_URL  = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/'
RIOT_API_KEY                = settings.RIOT_API_KEY


# 1) Home público (sin login)
def public_home(request: HttpRequest) -> HttpResponse:
    return render(request, 'homes/home.html')


# 2) Registro de usuario
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


# 3) Login/Logout usan las vistas genéricas de django.contrib.auth


# 4) Lista de campeones (público)
def champion_list(request: HttpRequest) -> HttpResponse:
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    try:
        versions = requests.get(version_url, timeout=5)
        versions.raise_for_status()
        latest_version = versions.json()[0]
    except requests.RequestException:
        return render(request, 'homes/champion_list.html', {'error': 'No se pudo obtener la versión.'})

    champions_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    try:
        resp = requests.get(champions_url, timeout=5)
        resp.raise_for_status()
        data = resp.json().get('data', {})
        for cid, champ in data.items():
            Champion.objects.update_or_create(
                champion_id=cid,
                defaults={
                    'name': champ['name'],
                    'role': champ['tags'][0] if champ['tags'] else 'Unknown',
                    'image_url': f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ['id']}_0.jpg",
                }
            )
    except requests.RequestException:
        return render(request, 'homes/champion_list.html', {'error': 'No se pudo obtener la lista de campeones.'})

    champions = Champion.objects.all()
    return render(request, 'homes/champion_list.html', {'champions': champions})


# 5) Home privado (requiere login)
@login_required
def home(request: HttpRequest) -> HttpResponse:
    reviews = Review.objects.filter(from_user=request.user)
    return render(request, 'homes/home2.html', {'reviews': reviews})


# 6) Crear reseña: formulario
@login_required
def review_create_form(request):
    return render(request, 'review_create.html')


# 7) Crear reseña: POST
@require_POST
@login_required
def create_review(request):
    player_id = request.POST.get('player_id_input','').strip()
    title     = request.POST.get('title','').strip()
    body      = request.POST.get('body','').strip()
    match_id  = request.POST.get('match_id','').strip()

    if not (player_id and title and body):
        return redirect('review_create_form')

    # --- Lógica de Riot API para puuid, summoner, match etc. ---
    # (copia aquí tu bloque de código original tal cual)

    # Finalmente:
    review = Review.objects.create(
        title=title,
        body=body,
        to_user=userlol,
        from_user=request.user,
        match=match
    )
    return redirect('home')


# 8) API: validar summoner
@csrf_exempt
@require_http_methods(["POST"])
def validate_summoner(request):
    # (copia aquí tu bloque original de validate_summoner)
    # y devuelve JsonResponse(...)
    pass


# 9) API: obtener matches
@csrf_exempt
@require_http_methods(["POST"])
def get_matches_for_player(request):
    # (copia aquí tu bloque original de get_matches_for_player)
    pass


# 10) Listado para actualizar reseña
@login_required
def review_update_list(request):
    reviews = Review.objects.filter(from_user=request.user).order_by('-timestamp')
    return render(request, 'review_update/review_update_list.html', {'reviews': reviews})


# 11) Editar reseña
@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk, from_user=request.user)
    if request.method == 'POST':
        review.title = request.POST.get('title','')
        review.body  = request.POST.get('body','')
        review.save()
        return redirect('review_update_list')
    return render(request, 'review_update/review_update.html', {'review': review})


# 12) Listado para eliminar reseña
@login_required
def review_delete_list(request):
    reviews = Review.objects.filter(from_user=request.user)
    return render(request, 'review_delete/review_delete_list.html', {'reviews': reviews})


# 13) Borrar reseña (POST)
@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Review.all_objects, pk=pk, from_user=request.user)
    review.delete()
    return redirect('review_delete_list')


# 14) Confirmar borrado
@login_required
def review_confirm_delete(request, pk):
    review = get_object_or_404(Review.all_objects, pk=pk, from_user=request.user)
    if request.method == 'POST':
        review.delete()
        return redirect('review_delete_list')
    return render(request, 'review_delete/review_confirm_delete.html', {'review': review})
