# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Champion
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
