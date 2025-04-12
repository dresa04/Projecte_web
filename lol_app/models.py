from django.db import models
from django.contrib.auth.models import User


class Champion(models.Model):
    """
    Represents a champion from the game League of Legends.

    Attributes:
        champion_id (str): Unique identifier for the champion.
        name (str): Name of the champion.
        role (str): Primary role of the champion (e.g., "Fighter", "Mage").
        image_url (str): URL of the champion's image.
    """
    champion_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, default="Unknown")
    role = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        """
        Returns a string representation of the champion.

        Returns:
            str: Name of the champion.
        """
        return self.name


class UserLOL(models.Model):
    """
    Represents a user registered in the application.

    Attributes:
        user_id (int): Unique identifier for the user.
        username (str): Unique username.
        email (str): Unique email address of the user.
        main (Champion): User's main champion.
    """
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    main = models.ForeignKey(Champion, on_delete=models.SET_NULL, null=True, related_name="mained_by")

    def __str__(self):
        """
        Returns a string representation of the user.

        Returns:
            str: Username.
        """
        return self.username


class Review(models.Model):
    """
    Represents a review written by a user about another user.

    Attributes:
        review_id (int): Unique identifier for the review.
        title (str): Title of the review.
        body (str): Content of the review.
        to_user (UserLOL): User to whom the review is directed.
        timestamp (datetime): Date and time when the review was created.
    """
    review_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    body = models.TextField()
    to_user = models.ForeignKey(UserLOL, on_delete=models.CASCADE, related_name="reviews_received")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the review.

        Returns:
            str: Review title and the user it is addressed to.
        """
        return f"Review #{self.review_id} for {self.to_user.username} - {self.title}"


class Match(models.Model):
    """
    Represents a match played in the game.

    Attributes:
        match_id (str): Unique identifier for the match.
        date_played (datetime): Date and time when the match was played.
        duration_minutes (int): Duration of the match in minutes.
        players (QuerySet[UserLOL]): Players who participated in the match.
        champions (QuerySet[Champion]): Champions used in the match.
    """
    match_id = models.CharField(max_length=100, unique=True)
    date_played = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    players = models.ManyToManyField(UserLOL, through="MatchChampion", related_name="matches")
    champions = models.ManyToManyField(Champion, through="MatchChampion")

    def __str__(self):
        """
        Returns a string representation of the match.

        Returns:
            str: Match identifier and date played.
        """
        return f"Match {self.match_id} - {self.date_played.date()}"


class MatchChampion(models.Model):
    """
    Represents the relationship between a match, a player, and a champion.

    Attributes:
        match (Match): Match in which the player participated.
        player (UserLOL): Player who participated in the match.
        champion (Champion): Champion used by the player in the match.
        kills (int): Number of kills by the player.
        deaths (int): Number of deaths of the player.
        assists (int): Number of assists by the player.
    """
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(UserLOL, on_delete=models.CASCADE)
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE)
    kills = models.PositiveIntegerField(default=0)
    deaths = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)

    class Meta:
        """
        Metadata for the MatchChampion model.

        Attributes:
            unique_together (list): Uniqueness constraints to avoid duplicates.
        """
        unique_together = [
            ('match', 'player'),   # A player can only appear once per match.
            ('match', 'champion')  # A champion can only appear once per match.
        ]

    def __str__(self):
        """
        Returns a string representation of the relationship.

        Returns:
            str: Information about the player, champion, and match.
        """
        return f"{self.player.username} played {self.champion.name} in match {self.match.match_id}"
