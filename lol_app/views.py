from django.shortcuts import render
from .models import Champion

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Asegúrate de tener esta plantilla


# views.py
import requests
from typing import Dict, Any
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from .models import Champion

from django.shortcuts import render
import requests
from .models import Champion
from typing import Dict, Any
from django.http import HttpRequest, HttpResponse

def champion_list(request: HttpRequest) -> HttpResponse:
    """
    Obté la llista de campions del joc League of Legends mitjançant l'API de Riot
    i emmagatzema les dades a la base de dades si no estan ja registrades.

    :param request: Objecte HttpRequest de Django.
    :return: HttpResponse amb la llista de campions renderitzada en 'champion_list.html'.
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


