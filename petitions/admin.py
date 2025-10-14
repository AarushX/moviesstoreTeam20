
from django.contrib import admin
from .models import Petition

@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie_name', 'created_by', 'created_at', 'vote_count']
    list_filter = ['created_at']
    search_fields = ['movie_name', 'created_by__username']
    readonly_fields = ['created_at']
