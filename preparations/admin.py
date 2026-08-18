from django.contrib import admin
from .models import FichePreparation

@admin.register(FichePreparation)
class FichePreparationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'niveau', 'matiere', 'enseignant', 'date_creation')
    list_filter = ('niveau', 'matiere', 'date_creation')
    search_fields = ('titre', 'theme', 'enseignant__username')