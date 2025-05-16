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


# 8) API: validar summoner
@csrf_exempt
@require_http_methods(["POST"])
def validate_summoner(request):
    """Validate a summoner's existence via Riot API and return their details."""
    game_name = request.POST.get('game_name', '').strip()
    tag_line = request.POST.get('tag_line', '').strip()

    if not game_name or not tag_line:
        return JsonResponse({'exists': False, 'message': 'Nombres incompletos'}, status=400)

    try:
        # 1. Get account info from Riot Account API
        account_url = f"{RIOT_ACCOUNT_API_BASE_URL}{game_name}/{tag_line}"
        response = requests.get(
            account_url,
            headers={'X-Riot-Token': RIOT_API_KEY},
            timeout=5
        )
        response.raise_for_status()
        account_data = response.json()

        puuid = account_data.get('puuid')
        if not puuid:
            return JsonResponse({'exists': False, 'message': 'No se encontró PUUID'}, status=404)

        # 2. Get summoner info using puuid
        summoner_url = f"{RIOT_SUMMONER_API_BASE_URL}{puuid}"
        summoner_response = requests.get(
            summoner_url,
            headers={'X-Riot-Token': RIOT_API_KEY},
            timeout=5
        )
        summoner_response.raise_for_status()
        summoner_data = summoner_response.json()

        # 3. Create or update UserLOL record
        userlol, created = UserLOL.objects.get_or_create(
            puuid=puuid,
            defaults={
                'game_name': account_data.get('gameName'),
                'tag_line': account_data.get('tagLine'),
                'summoner_id': summoner_data.get('id'),
                'summoner_level': summoner_data.get('summonerLevel', 0)
            }
        )

        if not created:
            # Update existing record
            userlol.game_name = account_data.get('gameName')
            userlol.tag_line = account_data.get('tagLine')
            userlol.summoner_level = summoner_data.get('summonerLevel', 0)
            userlol.save()

        # 4. Return success with user details
        return JsonResponse({
            'exists': True,
            'puuid': puuid,
            'gameName': userlol.game_name,
            'tagLine': userlol.tag_line,
            'summonerLevel': userlol.summoner_level
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"Riot API error: {str(e)}")
        return JsonResponse({
            'exists': False,
            'message': 'Error al consultar la API de Riot'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in validate_summoner: {str(e)}")
        return JsonResponse({
            'exists': False,
            'message': 'Error inesperado al procesar la solicitud'
        }, status=500)


# 9) API: obtener matches
@csrf_exempt
@require_http_methods(["POST"])
def get_matches_for_player(request):
    """Get recent matches for a player based on their puuid."""
    puuid = request.POST.get('puuid', '').strip()

    if not puuid:
        return JsonResponse({'error': 'PUUID requerido'}, status=400)

    try:
        # Get recent matches from Riot API (adjust region as needed)
        match_api_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        response = requests.get(
            match_api_url,
            params={'count': 5},  # Get last 5 matches
            headers={'X-Riot-Token': RIOT_API_KEY},
            timeout=10
        )
        response.raise_for_status()
        match_ids = response.json()

        matches_data = []
        for match_id in match_ids:
            # Check if match already exists in our database
            match_obj = Match.objects.filter(match_id=match_id).first()

            if not match_obj:
                # If not, get match details from Riot API
                match_detail_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
                match_response = requests.get(
                    match_detail_url,
                    headers={'X-Riot-Token': RIOT_API_KEY},
                    timeout=10
                )
                match_response.raise_for_status()
                match_detail = match_response.json()

                # Extract useful information
                match_info = match_detail.get('info', {})
                game_mode = match_info.get('gameMode', 'Unknown')
                duration = match_info.get('gameDuration', 0)
                game_start = match_info.get('gameStartTimestamp')

                # Create Match record
                match_obj = Match.objects.create(
                    match_id=match_id,
                    game_mode=game_mode,
                    duration=duration,
                    timestamp=datetime.fromtimestamp(game_start / 1000) if game_start else datetime.now(),
                )

                # Could also save participants/champions data if needed
                # for participant in match_info.get('participants', []):
                #     MatchChampion.objects.create(...)

            # Add to result list
            matches_data.append({
                'id': match_id,
                'gameMode': match_obj.game_mode,
                'duration': match_obj.duration,
                'timestamp': int(match_obj.timestamp.timestamp() * 1000)  # Convert to JS timestamp
            })

        return JsonResponse({'matches': matches_data})

    except requests.exceptions.RequestException as e:
        logger.error(f"Riot Match API error: {str(e)}")
        return JsonResponse({
            'error': 'Error al consultar la API de partidas de Riot',
            'matches': []
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in get_matches_for_player: {str(e)}")
        return JsonResponse({
            'error': 'Error inesperado al procesar las partidas',
            'matches': []
        }, status=500)


# Update your create_review function:
@require_POST
@login_required
def create_review(request):
    player_id = request.POST.get('player_id_input', '').strip()
    title = request.POST.get('title', '').strip()
    body = request.POST.get('body', '').strip()
    match_id = request.POST.get('match_id', '').strip()

    if not (player_id and title and body):
        context = {
            'form_error': 'Todos los campos son obligatorios',
            'submitted_player_id_input': player_id,
            'submitted_title': title,
            'submitted_body': body
        }
        return render(request, 'review_create.html', context)

    # Extract game_name and tag_line from player_id
    if '#' not in player_id:
        context = {
            'form_error': 'Formato de Riot ID inválido. Debe ser GameName#TagLine',
            'submitted_player_id_input': player_id,
            'submitted_title': title,
            'submitted_body': body
        }
        return render(request, 'review_create.html', context)

    game_name, tag_line = player_id.split('#', 1)

    try:
        # Find the UserLOL record
        userlol = UserLOL.objects.filter(
            game_name__iexact=game_name,
            tag_line__iexact=tag_line
        ).first()

        if not userlol:
            # Try to get from Riot API
            account_url = f"{RIOT_ACCOUNT_API_BASE_URL}{game_name}/{tag_line}"
            response = requests.get(
                account_url,
                headers={'X-Riot-Token': RIOT_API_KEY},
                timeout=5
            )
            response.raise_for_status()
            account_data = response.json()

            puuid = account_data.get('puuid')
            if not puuid:
                context = {
                    'form_error': 'Jugador no encontrado en Riot API',
                    'submitted_player_id_input': player_id,
                    'submitted_title': title,
                    'submitted_body': body
                }
                return render(request, 'review_create.html', context)

            # Create UserLOL record
            userlol = UserLOL.objects.create(
                puuid=puuid,
                game_name=account_data.get('gameName'),
                tag_line=account_data.get('tagLine')
            )

        # Look up match if provided
        match = None
        if match_id:
            match = Match.objects.filter(match_id=match_id).first()

        # Create review
        review = Review.objects.create(
            title=title,
            body=body,
            to_user=userlol,
            from_user=request.user,
            match=match
        )
        return redirect('home')

    except requests.exceptions.RequestException as e:
        logger.error(f"API error in create_review: {str(e)}")
        context = {
            'form_error': 'Error al consultar la API de Riot. Inténtalo más tarde.',
            'submitted_player_id_input': player_id,
            'submitted_title': title,
            'submitted_body': body
        }
        return render(request, 'review_create.html', context)
    except Exception as e:
        logger.error(f"Unexpected error in create_review: {str(e)}")
        context = {
            'form_error': 'Error inesperado al procesar la solicitud',
            'submitted_player_id_input': player_id,
            'submitted_title': title,
            'submitted_body': body
        }
        return render(request, 'review_create.html', context)
