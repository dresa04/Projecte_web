from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Champion, Review, UserLOL, Match, MatchChampion
import requests
from typing import Dict, Any
from django.http import HttpRequest, HttpResponse
from datetime import datetime

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Use csrf_exempt for simplicity in API endpoint,
# but be aware of implications or use csrf_protect
# and pass CSRF token with JS.
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

# Base URL for Riot Account V1 API (Global)
RIOT_ACCOUNT_API_BASE_URL = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/'  # Note: Americas is the region for Account-V1
# Base URL for LoL Summoner V4 API (Regional)
# You need to determine the correct regional endpoint (e.g., 'euw1', 'na1', 'kr', etc.)
# based on the user's input or a default. For EUW, it's 'euw1'.
RIOT_SUMMONER_API_BASE_URL = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/'

RIOT_API_KEY = settings.RIOT_API_KEY


def home(request):
    return render(request, 'home.html')


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
    version_url: str = "https://ddragon.leagueoflegends.com/api/versions.json"

    try:
        versions: requests.Response = requests.get(version_url, timeout=5)
        versions.raise_for_status()
        latest_version: str = versions.json()[0]
    except requests.RequestException:
        return render(request, "champion_list.html", {"error": "Could not fetch the game version."})

    champions_url: str = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"

    try:
        response: requests.Response = requests.get(champions_url, timeout=5)
        response.raise_for_status()
        champions_data: Dict[str, Dict[str, Any]] = response.json().get("data", {})

        for champ_id, champ in champions_data.items():
            name = champ["name"]
            role = champ["tags"][0] if champ["tags"] else "Unknown"
            image_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ['id']}_0.jpg"

            Champion.objects.update_or_create(
                champion_id=champ_id,
                defaults={
                    "name": name,
                    "role": role,
                    "image_url": image_url,
                }
            )

        champions = Champion.objects.all()
        return render(request, "champion_list.html", {"champions": champions})

    except requests.RequestException:
        return render(request, "champion_list.html", {"error": "Could not fetch the champion list."})


@login_required
def home(request: HttpRequest) -> HttpResponse:
    """
    Displays the main page with a list of all reviews.
    Requires user to be logged in.
    """
    reviews = Review.objects.all()  # omite las borradas
    # o para sólo tus reseñas:
    reviews = Review.objects.filter(from_user=request.user)
    context = {
        'reviews': reviews
    }
    return render(request, 'home2.html', context)


@login_required
def review_update_list(request):
    reviews = Review.objects.filter(from_user=request.user)
    return render(request, "review_update_list.html", {"reviews": reviews})


@login_required
def review_delete_list(request):
    reviews = Review.objects.filter(from_user=request.user)
    return render(request, "review_delete_list.html", {"reviews": reviews})


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect


@require_POST
@login_required
def create_review(request):
    player_id_input = request.POST.get('player_id_input', '')
    match_id = request.POST.get('match_id', '')
    title = request.POST.get('title')
    body = request.POST.get('body')

    if not (player_id_input and title and body):
        return redirect('review_create_form')

    # Parse the Riot ID
    try:
        game_name, tag_line = player_id_input.split('#')
    except ValueError:
        # Invalid format
        return render(request, 'review_create.html', {
            'form_error': 'Invalid Riot ID format',
            'submitted_player_id_input': player_id_input,
            'submitted_title': title,
            'submitted_body': body
        })

    # First, verify the summoner exists using the Riot API
    headers = {"X-Riot-Token": RIOT_API_KEY}

    try:
        # Get PUUID using Account V1 API
        account_api_url = f"{RIOT_ACCOUNT_API_BASE_URL}{game_name}/{tag_line}"
        account_response = requests.get(account_api_url, headers=headers)
        account_response.raise_for_status()

        account_data = account_response.json()
        puuid = account_data.get('puuid')
        api_game_name = account_data.get('gameName')
        api_tag_line = account_data.get('tagLine')

        if not puuid:
            return render(request, 'review_create.html', {
                'form_error': 'Could not find PUUID for this player',
                'submitted_player_id_input': player_id_input,
                'submitted_title': title,
                'submitted_body': body
            })

        # Get Summoner data using PUUID
        summoner_api_url = f"{RIOT_SUMMONER_API_BASE_URL}{puuid}"
        summoner_response = requests.get(summoner_api_url, headers=headers)
        summoner_response.raise_for_status()

        summoner_data = summoner_response.json()
        summoner_name = summoner_data.get('name')

        # Create or get the UserLOL object
        userlol, created = UserLOL.objects.get_or_create(
            username=f"{api_game_name}#{api_tag_line}",
            defaults={'email': f"{puuid}@lolreview.com", 'main': None}
        )

        # If a match ID was provided, get or create the match
        match = None
        if match_id:
            # Get match details using the Riot API
            REGION_MATCHES = "europe"
            match_detail_url = f"https://{REGION_MATCHES}.api.riotgames.com/lol/match/v5/matches/{match_id}"

            try:
                match_response = requests.get(match_detail_url, headers=headers)
                match_response.raise_for_status()
                match_data = match_response.json()

                match_info = match_data.get('info', {})
                game_duration = match_info.get('gameDuration', 0)
                game_start = match_info.get('gameStartTimestamp', 0)

                # Convert milliseconds timestamp to datetime
                date_played = datetime.fromtimestamp(game_start / 1000) if game_start else datetime.now()

                # Create or get the Match object
                match, match_created = Match.objects.get_or_create(
                    match_id=match_id,
                    defaults={
                        'date_played': date_played,
                        'duration_minutes': game_duration // 60,  # Convert seconds to minutes
                    }
                )

                # Find the participant data for our user
                for participant in match_info.get('participants', []):
                    if participant.get('puuid') == puuid:
                        champion_id = participant.get('championId')
                        kills = participant.get('kills', 0)
                        deaths = participant.get('deaths', 0)
                        assists = participant.get('assists', 0)

                        # Find the champion by ID
                        champion = None
                        try:
                            # First try to get champion by ID
                            champion = Champion.objects.get(champion_id=str(champion_id))
                        except Champion.DoesNotExist:
                            # If not found, use a default champion
                            champion, _ = Champion.objects.get_or_create(
                                champion_id="unknown",
                                defaults={"name": "Unknown Champion", "role": "Unknown"}
                            )

                        # Create the MatchChampion relationship if it doesn't exist
                        try:
                            mc, mc_created = MatchChampion.objects.get_or_create(
                                match=match,
                                player=userlol,
                                champion=champion,
                                defaults={
                                    'kills': kills,
                                    'deaths': deaths,
                                    'assists': assists
                                }
                            )
                        except Exception as e:
                            logger.error(f"Error creating MatchChampion: {e}")
                        break

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching match data: {e}")
                # Continue without match data if we can't fetch it

        # Create the review
        review = Review.objects.create(
            title=title,
            body=body,
            to_user=userlol,
            from_user=request.user,
            match=match
        )

        return redirect('home')

    except requests.exceptions.HTTPError as e:
        logger.error(f"Riot API HTTP Error: {e}")
        status = e.response.status_code if hasattr(e, 'response') else 500
        error_msg = "Player not found" if status == 404 else f"API error ({status})"

        return render(request, 'review_create.html', {
            'form_error': error_msg,
            'submitted_player_id_input': player_id_input,
            'submitted_title': title,
            'submitted_body': body
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"Riot API Request Exception: {e}")
        return render(request, 'review_create.html', {
            'form_error': 'Could not connect to Riot API',
            'submitted_player_id_input': player_id_input,
            'submitted_title': title,
            'submitted_body': body
        })

    except Exception as e:
        logger.error(f"Unexpected error in create_review: {e}", exc_info=True)
        return render(request, 'review_create.html', {
            'form_error': 'An unexpected error occurred',
            'submitted_player_id_input': player_id_input,
            'submitted_title': title,
            'submitted_body': body
        })


@login_required
def review_create_form(request):
    return render(request, 'review_create.html')


@csrf_exempt
@require_http_methods(["POST"])
def validate_summoner(request):
    """
    Looks up a player using Riot ID (Game Name + Tag Line) via Riot API.
    """
    game_name = request.POST.get('game_name', '').strip()
    tag_line = request.POST.get('tag_line', '').strip()

    if not game_name or not tag_line:
        return JsonResponse({'exists': False, 'message': 'Game Name and Tag Line are required.'}, status=400)

    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    try:
        # Step 1: Get PUUID using Account V1 API
        account_api_url = f"{RIOT_ACCOUNT_API_BASE_URL}{game_name}/{tag_line}"
        logger.info(f"Calling Account API: {account_api_url}")
        account_response = requests.get(account_api_url, headers=headers)
        account_response.raise_for_status()

        account_data = account_response.json()
        puuid = account_data.get('puuid')
        api_game_name = account_data.get('gameName')
        api_tag_line = account_data.get('tagLine')

        if not puuid:
            logger.error(f"PUUID not found in Account API response for {game_name}#{tag_line}")
            return JsonResponse({'exists': False, 'message': 'PUUID not found in API response.'}, status=500)

        # Step 2: Get Summoner Data using Summoner V4 API and PUUID
        summoner_api_url = f"{RIOT_SUMMONER_API_BASE_URL}{puuid}"
        logger.info(f"Calling Summoner API (by PUUID): {summoner_api_url}")
        summoner_response = requests.get(summoner_api_url, headers=headers)
        summoner_response.raise_for_status()

        summoner_data = summoner_response.json()

        # Return includes puuid now
        return JsonResponse({
            'exists': True,
            'gameName': api_game_name,
            'tagLine': api_tag_line,
            'summonerLevel': summoner_data.get('summonerLevel'),
            'puuid': puuid,
        })

    except requests.exceptions.HTTPError as e:
        logger.error(f"Riot API HTTP Error for {game_name}#{tag_line}: {e.response.status_code} - {e}")
        status = e.response.status_code
        if status == 404:
            message = f"Riot ID '{game_name}#{tag_line}' not found."
            return JsonResponse({'exists': False, 'message': message}, status=404)
        if status == 429:
            return JsonResponse({'exists': False, 'message': 'API rate limit exceeded. Try again shortly.'}, status=429)
        if status == 403:
            return JsonResponse({'exists': False, 'message': 'API key invalid or restricted.'}, status=403)
        return JsonResponse({'exists': False, 'message': f'An API error occurred ({status}).'}, status=status)

    except requests.exceptions.RequestException as e:
        logger.error(f"Riot API Request Exception for {game_name}#{tag_line}: {e}")
        return JsonResponse({'exists': False, 'message': 'Could not connect to Riot API.'}, status=500)

    except Exception as e:
        logger.error(f"Unexpected error in validate_summoner for {game_name}#{tag_line}: {e}", exc_info=True)
        return JsonResponse({'exists': False, 'message': 'An internal server error occurred.'}, status=500)


import logging
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def get_matches_for_player(request):
    puuid = request.POST.get('puuid', '').strip()
    if not puuid:
        return JsonResponse({'error': 'Missing puuid'}, status=400)

    # Ajusta la región según donde juegues
    REGION_MATCHES = "europe"  # o "americas", "asia", etc.
    match_list_url = (
        f"https://{REGION_MATCHES}.api.riotgames.com"
        f"/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5"
    )

    # 1) loguea PUUID y URL
    logger.info(f"[get_matches] puuid = {puuid}")
    logger.info(f"[get_matches] URL   = {match_list_url}")

    try:
        resp = requests.get(match_list_url,
                            headers={"X-Riot-Token": settings.RIOT_API_KEY},
                            timeout=5)
        resp.raise_for_status()
        match_ids = resp.json()

        matches = []
        for match_id in match_ids:
            detail_url = f"https://{REGION_MATCHES}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            logger.info(f"[get_matches] detail URL = {detail_url}")
            md = requests.get(detail_url,
                              headers={"X-Riot-Token": settings.RIOT_API_KEY},
                              timeout=5)
            md.raise_for_status()
            info = md.json().get("info", {})
            matches.append({
                'id': match_id,
                'gameMode': info.get('gameMode'),
                'duration': info.get('gameDuration'),
                'timestamp': info.get('gameStartTimestamp'),
            })

        logger.info(f"[get_matches] found {len(matches)} matches")
        return JsonResponse({'matches': matches})

    except Exception as e:
        # 2) Log completo de la excepción
        logger.error("[get_matches] Exception!", exc_info=True)
        # opcional: imprime también en stdout
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review

@login_required
def review_update_list(request):
    # Solo tus reseñas
    reviews = Review.objects.filter(from_user=request.user).order_by('-timestamp')
    return render(request, 'review_update_list.html', {'reviews': reviews})

@login_required
def review_update(request, pk):
    # Asegura que solo tú puedas editarla
    review = get_object_or_404(Review, pk=pk, from_user=request.user)

    if request.method == 'POST':
        # Actualiza campos
        review.title = request.POST.get('title')
        review.body  = request.POST.get('body')
        review.save()
        return redirect('review_update_list')

    return render(request, 'review_update.html', {'review': review})


@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Review.all_objects, pk=pk, from_user=request.user)
    review.delete()    # esto marca is_deleted=True
    return redirect('review_delete_list')

@login_required
def review_confirm_delete(request, pk):
    review = get_object_or_404(Review.all_objects, pk=pk, from_user=request.user)
    if request.method == 'POST':
        review.delete()
        return redirect('review_delete_list')
    return render(request, 'review_confirm_delete.html', {'review': review})

