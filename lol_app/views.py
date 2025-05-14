# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Champion, Review
import requests
from typing import Dict, Any
from django.http import HttpRequest, HttpResponse

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
