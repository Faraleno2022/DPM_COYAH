from django.contrib import admin
from .models import Company, RequiredDocument, DocumentSubmission


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation')
    search_fields = ('nom',)


@admin.register(RequiredDocument)
class RequiredDocumentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom', 'description')


@admin.register(DocumentSubmission)
class DocumentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('company', 'document', 'date_submission')
    list_filter = ('company', 'document', 'date_submission')
    date_hierarchy = 'date_submission'
    search_fields = ('company__nom', 'document__nom')
    readonly_fields = ('date_submission',)
