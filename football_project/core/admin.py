from django.contrib import admin
from .models import *

admin.site.register(Region)
admin.site.register(City)
admin.site.register(Category)

@admin.register(RegionAdmin)
class RegionAdminAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'region', 'user']

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'user']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'category', 'coach']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['player_id', 'last_name', 'first_name', 'position', 'team']
    search_fields = ['last_name', 'first_name', 'player_id']
    readonly_fields = ['player_id']

@admin.register(PlayerRequest)
class PlayerRequestAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'team', 'status', 'created_by', 'created_at']
    list_filter = ['status']

admin.site.register(Stadium)
admin.site.register(Competition)
admin.site.register(Match)
admin.site.register(News)
admin.site.register(NewsPhoto)
admin.site.register(TransferRequest)
admin.site.register(Document)
