from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    body = models.TextField()
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review #{self.review_id} for {self.to_user.username} - {self.title}"

from django.db import models

class Champion(models.Model):
    champion_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, default="Unknown")  # Asegúrate de tener este campo
    role = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name  # Para que se use el nombre del campeón en el admin



class Match(models.Model):
    """
    Represents a League of Legends match.
    """
    match_id = models.CharField(max_length=100, unique=True)  # Riot API match ID
    date_played = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()  # Match duration
    players = models.ManyToManyField(User, related_name="matches")  # Relación muchos a muchos con usuarios
    champions = models.ManyToManyField(Champion, through="MatchChampion")  # Relación muchos a muchos con campeones

    def __str__(self):
        return f"Match {self.match_id} - {self.date_played.date()}"


class MatchChampion(models.Model):
    """
    Intermediary model to represent the relationship between Match and Champion.
    """
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)  # Jugador que usa el campeón
    kills = models.PositiveIntegerField(default=0)  # Ejemplo: estadísticas de la partida
    deaths = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('match', 'champion', 'player')  # Asegura que un jugador no repita campeón en una misma partida

    def __str__(self):
        return f"{self.player.username} played {self.champion.name} in match {self.match.match_id}"




