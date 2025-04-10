from django.db import models
from django.contrib.auth.models import User

class UserLOL(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    main = models.ForeignKey(Champion, on_delete=models.SET_NULL, null=True, related_name="mained_by")

    def __str__(self):
        return self.username


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    body = models.TextField()
    to_user = models.ForeignKey(UserLOL, on_delete=models.CASCADE, related_name="reviews_received")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review #{self.review_id} for {self.to_user.username} - {self.title}"


class Champion(models.Model):
    champion_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, default="Unknown")
    role = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    match_id = models.CharField(max_length=100, unique=True)
    date_played = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    players = models.ManyToManyField(UserLOL, related_name="matches")
    champions = models.ManyToManyField(Champion, through="MatchChampion")

    def __str__(self):
        return f"Match {self.match_id} - {self.date_played.date()}"


class MatchChampion(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(UserLOL, on_delete=models.CASCADE)
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE)
    kills = models.PositiveIntegerField(default=0)
    deaths = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [
            ('match', 'player'),   # un jugador solo puede aparecer una vez por partida
            ('match', 'champion') # un campeón solo puede aparecer una vez por partida
        ]

    def __str__(self):
        return f"{self.player.username} played {self.champion.name} in match {self.match.match_id}"
