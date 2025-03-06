from django.shortcuts import render
import requests
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any

# Define the Riot API key
RIOT_API_KEY = "RGAPI-7e14a6d3-cfcc-496e-9640-7856ca4e8338"


def home(request: HttpRequest) -> HttpResponse:
    """
    Renderitza la pàgina principal de l'aplicació.

    :param request: Objecte HttpRequest de Django.
    :return: HttpResponse amb la plantilla renderitzada 'home.html'.
    """
    return render(request, 'home.html')


def item_list(request: HttpRequest) -> HttpResponse:
    """
    Obté la llista d'ítems del joc League of Legends mitjançant l'API de Riot.

    :param request: Objecte HttpRequest de Django.
    :return: HttpResponse amb la llista d'ítems renderitzada en 'items.html'.
    """
    version_url: str = "https://ddragon.leagueoflegends.com/api/versions.json"

    try:
        versions: requests.Response = requests.get(version_url, timeout=5)
        versions.raise_for_status()
        latest_version: str = versions.json()[0]
    except requests.RequestException:
        return render(request, "items.html", {"error": "Could not fetch the game version."})

    items_url: str = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/item.json"

    try:
        response: requests.Response = requests.get(items_url, timeout=5)
        response.raise_for_status()
        items_data: Dict[str, Dict[str, Any]] = response.json().get("data", {})

        items: list[Dict[str, str]] = []
        for item_id, item in items_data.items():
            items.append({
                "name": item["name"],
                "description": item["description"],
                "price": item["gold"]["total"],
                "image": f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/item/{item_id}.png"
            })

        return render(request, "items.html", {"items": items})
    except requests.RequestException:
        return render(request, "items.html", {"error": "Could not fetch the item list."})


def champion_list(request: HttpRequest) -> HttpResponse:
    """
    Obté la llista de campions del joc League of Legends mitjançant l'API de Riot.

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

        champions: list[Dict[str, Any]] = []
        for champ in champions_data.values():
            champions.append({
                "id": champ["id"],
                "title": champ["title"],
                "blurb": champ["blurb"],
                "info": champ["info"],
                "image": f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ['id']}_0.jpg",
                "tags": champ["tags"],
                "stats": champ["stats"],
            })

        return render(request, "champion_list.html", {"champions": champions})
    except requests.RequestException:
        return render(request, "champion_list.html", {"error": "Could not fetch the champion list."})


def summoner_detail(request: HttpRequest, summoner_name: str) -> HttpResponse:
    """
    Mostra la pàgina amb els detalls d'un invocador.

    :param request: Objecte HttpRequest de Django.
    :param summoner_name: Nom de l'invocador.
    :return: HttpResponse amb la plantilla 'puuid_form.html'.
    """
    return render(request, 'puuid_form.html', {'summoner_name': summoner_name})


def get_puuid(request: HttpRequest) -> HttpResponse:
    """
    Cerca el PUUID d'un jugador a partir del seu nom i tag mitjançant l'API de Riot.

    :param request: Objecte HttpRequest de Django.
    :return: HttpResponse amb la informació del PUUID renderitzada en 'puuid_result.html'.
    """
    if request.method == "POST":
        game_name: str = request.POST.get("gameName", "")
        tag_line: str = request.POST.get("tagLine", "")
        region: str = "europe"

        url_puuid: str = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        headers: Dict[str, str] = {"X-Riot-Token": RIOT_API_KEY}

        try:
            response_puuid: requests.Response = requests.get(url_puuid, headers=headers, timeout=5)
            response_puuid.raise_for_status()
            data_puuid: Dict[str, str] = response_puuid.json()

            puuid: str = data_puuid["puuid"]
            data_mastery: str = "Not available"

            return render(
                request,
                "puuid_result.html",
                {"puuid": puuid, "gameName": game_name, "tagLine": tag_line, "mastery_points": data_mastery}
            )
        except requests.RequestException:
            return render(request, "puuid_result.html", {"error": "Player not found or API error."})

    return render(request, "puuid_form.html")