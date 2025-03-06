from django.db import models
from typing import List, Dict

class Summoner(models.Model):
    game_name: str = models.CharField(max_length=100)
    tag_line: str = models.CharField(max_length=100)
    puuid: str = models.CharField(max_length=100, unique=True)  # PUUID único
    mastery_points: int = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.game_name}#{self.tag_line}"

class Champion(models.Model):
    champion_id: str = models.CharField(max_length=100, unique=True)  # ID único para cada campeón
    name: str = models.CharField(max_length=100)
    title: str = models.CharField(max_length=100)
    blurb: str = models.TextField()
    tags: List[str] = models.JSONField()  # Guardar una lista de etiquetas como JSON
    stats: Dict[str, float] = models.JSONField()  # Guardar las estadísticas como un diccionario JSON

    def __str__(self) -> str:
        return self.name

class Item(models.Model):
    item_id: str = models.CharField(max_length=100, unique=True)  # ID único para cada ítem
    name: str = models.CharField(max_length=100)
    description: str = models.TextField()
    price: int = models.IntegerField()
    image: str = models.URLField()  # Almacenamos la URL de la imagen en vez de la imagen misma

    def __str__(self) -> str:
        return self.name
