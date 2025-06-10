from django.shortcuts import render
from companies.models import Company
from administration_docs.models import AdministrativeDocument

def home_view(request):
    """
    Vue de la page d'accueil principale de l'application
    Affiche les statistiques et les raccourcis vers les fonctionnalités principales
    """
    # Récupérer quelques statistiques pour le tableau de bord
    stats = {
        'total_companies': Company.objects.count(),
        'total_documents': AdministrativeDocument.objects.count(),
        'recent_documents': AdministrativeDocument.objects.order_by('-date_enregistrement')[:5],
        # Précharger les soumissions de documents pour optimiser le calcul du pourcentage de complétion
        'recent_companies': Company.objects.prefetch_related('submissions').order_by('-date_creation')[:5]
    }
    
    # Compter les documents par type
    doc_types = {
        'decrets': AdministrativeDocument.objects.filter(type=AdministrativeDocument.DECRET).count(),
        'arretes': AdministrativeDocument.objects.filter(type=AdministrativeDocument.ARRETE).count(),
        'notes': AdministrativeDocument.objects.filter(type=AdministrativeDocument.NOTE).count(),
    }
    
    context = {
        'stats': stats,
        'doc_types': doc_types,
    }
    
    return render(request, 'home.html', context)
