from django.contrib import admin
from .models import AdministrativeDocument


@admin.register(AdministrativeDocument)
class AdministrativeDocumentAdmin(admin.ModelAdmin):
    list_display = ('type', 'numero', 'titre', 'date_enregistrement')
    list_filter = ('type', 'date_enregistrement')
    search_fields = ('numero', 'titre', 'description')
    date_hierarchy = 'date_enregistrement'
    readonly_fields = ('date_creation',)
