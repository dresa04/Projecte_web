# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Champion, Review
import requests
from typing import Dict, Any
from django.http import HttpRequest, HttpResponse

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # Use csrf_exempt for simplicity in API endpoint,
                                                    # but be aware of implications or use csrf_protect
                                                    # and pass CSRF token with JS.
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

# Base URL for Riot Account V1 API (Global)
RIOT_ACCOUNT_API_BASE_URL = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/' # Note: Americas is the region for Account-V1
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
    reviews = Review.objects.select_related('from_user', 'to_user').all()
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
from .models import UserLOL, Review

@require_POST
@login_required
def create_review(request):
    summoner_name = request.POST.get('to_summoner_name')
    title = request.POST.get('title')
    body = request.POST.get('body')

    if not (summoner_name and title and body):
        return redirect('home')

    # Simula creación de UserLOL sin API
    userlol, _ = UserLOL.objects.get_or_create(
        username=summoner_name,
        defaults={'email': f'{summoner_name}@fake.com', 'main': None}
    )

    Review.objects.create(
        title=title,
        body=body,
        to_user=userlol,
        from_user=request.user
    )

    return redirect('home')


@csrf_exempt
@require_http_methods(["POST"])
def validate_summoner(request):
    """
    Looks up a player using Riot ID (Game Name + Tag Line) via Riot API.
    """
    game_name = request.POST.get('game_name', '').strip()
    tag_line = request.POST.get('tag_line', '').strip()
    # tag_line_region = request.POST.get('tag_line_region', 'euw') # Example if you add region selector

    if not game_name or not tag_line:
        return JsonResponse({'exists': False, 'message': 'Game Name and Tag Line are required.'}, status=400)

    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    try:
        # --- Step 1: Get PUUID using Account V1 API ---
        # Account V1 API is global, typically routed through 'americas' region gateway
        account_api_url = f"{RIOT_ACCOUNT_API_BASE_URL}{game_name}/{tag_line}"
        logger.info(f"Calling Account API: {account_api_url}")
        account_response = requests.get(account_api_url, headers=headers)
        account_response.raise_for_status() # Raise HTTPError for bad responses

        account_data = account_response.json()
        puuid = account_data.get('puuid')
        # Get exact gameName and tagLine from API response
        api_game_name = account_data.get('gameName')
        api_tag_line = account_data.get('tagLine')


        if not puuid:
             # Should not happen if raise_for_status didn't throw, but as a safeguard
             logger.error(f"PUUID not found in Account API response for {game_name}#{tag_line}")
             return JsonResponse({'exists': False, 'message': 'PUUID not found in API response.'}, status=500)

        # --- Step 2: Get Summoner Data using Summoner V4 API and PUUID ---
        # Summoner V4 API is regional. You need to select the correct region base URL.
        # For this example, hardcoding EUW1. You might need logic here.
        summoner_api_url = f"{RIOT_SUMMONER_API_BASE_URL}{puuid}"
        logger.info(f"Calling Summoner API (by PUUID): {summoner_api_url}")
        summoner_response = requests.get(summoner_api_url, headers=headers)
        summoner_response.raise_for_status() # Raise HTTPError again

        summoner_data = summoner_response.json()

        # If both calls succeeded, the player exists and we have their summoner data
        return JsonResponse({
            'exists': True,
            'gameName': api_game_name, # Use the exact casing from API
            'tagLine': api_tag_line, # Use the exact casing from API
            'summonerLevel': summoner_data.get('summonerLevel'),
            # You might want to return summonerId or puuid to store in your review model
            # 'puuid': puuid,
            # 'summonerId': summoner_data.get('id'),
        })

    except requests.exceptions.HTTPError as e:
        # Handle specific API errors
        logger.error(f"Riot API HTTP Error for {game_name}#{tag_line}: {e.response.status_code} - {e}")
        if e.response.status_code == 404:
            # 404 from Account API -> Riot ID not found
            # 404 from Summoner API -> PUUID not found in that region (less likely if Account API worked)
            message = f"Riot ID '{game_name}#{tag_line}' not found." # Default message
            # You might refine this based on which API call failed if needed
            return JsonResponse({'exists': False, 'message': message}, status=404)
        elif e.response.status_code == 429:
             logger.warning(f"Riot API Rate Limit Exceeded for {game_name}#{tag_line}")
             return JsonResponse({'exists': False, 'message': 'API rate limit exceeded. Try again shortly.'}, status=429)
        elif e.response.status_code == 403:
             logger.error(f"Riot API Forbidden for {game_name}#{tag_line} - Check API Key/Region: {e}")
             return JsonResponse({'exists': False, 'message': 'API key invalid or restricted.'}, status=403)
        else:
            logger.error(f"Unhandled Riot API HTTP Error for {game_name}#{tag_line}: {e.response.status_code}")
            return JsonResponse({'exists': False, 'message': f'An API error occurred ({e.response.status_code}).'}, status=e.response.status_code)

    except requests.exceptions.RequestException as e:
        # Network errors, timeouts, etc.
        logger.error(f"Riot API Request Exception for {game_name}#{tag_line}: {e}")
        return JsonResponse({'exists': False, 'message': 'Could not connect to Riot API.'}, status=500)

    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error in validate_summoner for {game_name}#{tag_line}: {e}", exc_info=True)
        return JsonResponse({'exists': False, 'message': 'An internal server error occurred.'}, status=500)



@login_required
def review_create_form(request):
        return render(request, 'review_create.html')
