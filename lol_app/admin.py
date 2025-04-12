from django.contrib import admin
from .models import Review, Champion, Match, UserLOL, MatchChampion

class MatchChampionInline(admin.TabularInline):
    model = MatchChampion
    extra = 1

class MatchAdmin(admin.ModelAdmin):
    inlines = [MatchChampionInline]

admin.site.register(Review)
admin.site.register(Champion)
admin.site.register(Match, MatchAdmin)
admin.site.register(UserLOL)
