from django.shortcuts import render
from .models import Champion
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from typing import Dict, Any
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import requests
from .models import Champion
from typing import Dict, Any
from django.http import HttpRequest, HttpResponse


# views.py


def champion_list(request: HttpRequest) -> HttpResponse:
    """
        Retrieves the list of League of Legends champions using the Riot API
        and stores the data in the database if they are not already registered.

        :param request: Django HttpRequest object.
        :return: HttpResponse with the list of champions rendered in 'champion_list.html'.
    """

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

        # Processem els dades dels campions i els guardem a la base de dades
        for champ_id, champ in champions_data.items():
            name = champ["name"]
            role = champ["tags"][0] if champ["tags"] else "Unknown"  # Agafem el primer tag com a rol
            image_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ['id']}_0.jpg"

            # Actualitzem o creem el campió a la base de dades
            Champion.objects.update_or_create(
                champion_id=champ_id,  # Usar el ID del campeón como identificador único
                defaults={
                    "name": name,
                    "role": role,
                    "image_url": image_url,
                }
            )

        # Obtenim la llista de campions de la base de dades per mostrar-los
        champions = Champion.objects.all()

        return render(request, "champion_list.html", {"champions": champions})

    except requests.RequestException:
        return render(request, "champion_list.html", {"error": "Could not fetch the champion list."})






def register(request):
    """
    Handles the registration of new users.

    If the request is POST, it validates the user creation form. If it's valid,
    saves the user, logs them in automatically, and redirects to the home page.
    If the request is not POST, it displays an empty registration form.

    :param request: Django HttpRequest object.
    :return: HttpResponse with the registration page or a redirect to the home page.
"""

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # iniciar sesión automáticamente después del registro
            return redirect('home')  # o donde quieras redirigir
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def home(request):
    form = AuthenticationForm()
    return render(request, 'home.html', {'form': form})
