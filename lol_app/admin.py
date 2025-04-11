from django.contrib import admin
from .models import Review, Champion, Match, UserLOL, MatchChampion

admin.site.register(Review)
admin.site.register(Champion)
admin.site.register(Match)
admin.site.register(UserLOL)
admin.site.register(MatchChampion)

