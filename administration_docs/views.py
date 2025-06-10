from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.db.models.expressions import RawSQL

from .models import AdministrativeDocument
from .forms import AdministrativeDocumentForm, DocumentFilterForm
from companies.models import Company, DocumentSubmission

class AdministrativeDocumentListView(ListView):
    """Vue pour afficher la liste des documents administratifs"""
    model = AdministrativeDocument
    context_object_name = 'documents'
    template_name = 'administration_docs/document_list.html'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = AdministrativeDocument.objects.all()
        
        # Filtrer par type de document
        doc_type = self.request.GET.get('type')
        if doc_type and doc_type in [choice[0] for choice in AdministrativeDocument.DOCUMENT_TYPES]:
            queryset = queryset.filter(type=doc_type)
        
        # Recherche textuelle
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(titre__icontains=search_query) | 
                Q(numero__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_types'] = AdministrativeDocument.DOCUMENT_TYPES
        
        # Conserver les paramètres de recherche
        context['current_type'] = self.request.GET.get('type', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        return context


class AdministrativeDocumentDetailView(DetailView):
    """Vue pour afficher les détails d'un document administratif"""
    model = AdministrativeDocument
    context_object_name = 'document'
    template_name = 'administration_docs/document_detail.html'


class AdministrativeDocumentCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer un nouveau document administratif"""
    model = AdministrativeDocument
    form_class = AdministrativeDocumentForm
    template_name = 'administration_docs/document_form.html'
    success_url = reverse_lazy('admin_doc_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un document administratif'
        
        # Préremplir le type de document depuis l'URL si disponible
        doc_type = self.request.GET.get('type')
        if doc_type and doc_type in [choice[0] for choice in AdministrativeDocument.DOCUMENT_TYPES]:
            context['initial_type'] = doc_type
        
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        doc_type = self.request.GET.get('type')
        if doc_type and doc_type in [choice[0] for choice in AdministrativeDocument.DOCUMENT_TYPES]:
            initial['type'] = doc_type
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, 'Document administratif créé avec succès!')
        return super().form_valid(form)


class AdministrativeDocumentUpdateView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier un document administratif"""
    model = AdministrativeDocument
    form_class = AdministrativeDocumentForm
    template_name = 'administration_docs/document_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le document administratif'
        return context
    
    def get_success_url(self):
        return reverse('admin_doc_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Document administratif modifié avec succès!')
        return super().form_valid(form)


class AdministrativeDocumentDeleteView(LoginRequiredMixin, DeleteView):
    """Vue pour supprimer un document administratif"""
    model = AdministrativeDocument
    template_name = 'administration_docs/document_confirm_delete.html'
    success_url = reverse_lazy('admin_doc_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document administratif supprimé avec succès!')
        return super().delete(request, *args, **kwargs)


# Vues filtrées par type de document
class DecretListView(AdministrativeDocumentListView):
    """Vue pour afficher uniquement les décrets"""
    
    def get_queryset(self):
        return AdministrativeDocument.objects.filter(type=AdministrativeDocument.DECRET)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des décrets'
        context['document_type'] = 'DECRET'
        return context


class ArreteListView(AdministrativeDocumentListView):
    """Vue pour afficher uniquement les arrêtés"""
    
    def get_queryset(self):
        return AdministrativeDocument.objects.filter(type=AdministrativeDocument.ARRETE)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des arrêtés'
        context['document_type'] = 'ARRETE'
        return context


class NoteServiceListView(AdministrativeDocumentListView):
    """Vue pour afficher uniquement les notes de service"""
    
    def get_queryset(self):
        return AdministrativeDocument.objects.filter(type=AdministrativeDocument.NOTE)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des notes de service'
        context['document_type'] = 'NOTE'
        return context


class RecentDocsWithCompaniesView(ListView):
    """Vue pour afficher les 25 documents administratifs les plus récents avec leurs sociétés correspondantes"""
    model = AdministrativeDocument
    context_object_name = 'documents'
    template_name = 'administration_docs/recent_docs_simplified.html'
    
    def get_queryset(self):
        # Récupérer le formulaire avec les données de filtrage (s'il y en a)
        form = DocumentFilterForm(self.request.GET or None)
        queryset = AdministrativeDocument.objects.all()
        
        # Appliquer les filtres si le formulaire est valide
        if form.is_valid():
            # Filtre par type de document
            if form.cleaned_data['type']:
                queryset = queryset.filter(type=form.cleaned_data['type'])
                
            # Filtre par mot-clé (dans le numéro, titre ou description)
            if form.cleaned_data['keyword']:
                keyword = form.cleaned_data['keyword']
                queryset = queryset.filter(
                    Q(numero__icontains=keyword) |
                    Q(titre__icontains=keyword) |
                    Q(description__icontains=keyword)
                )
                
            # Filtres par date
            if form.cleaned_data['date_min']:
                queryset = queryset.filter(date_enregistrement__gte=form.cleaned_data['date_min'])
                
            if form.cleaned_data['date_max']:
                queryset = queryset.filter(date_enregistrement__lte=form.cleaned_data['date_max'])
        
        # Trier par date la plus récente et limiter à 25 documents
        return queryset.order_by('-date_enregistrement')[:25]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '25 derniers documents avec sociétés'
        # Ajouter le formulaire de filtrage au contexte
        context['filter_form'] = DocumentFilterForm(self.request.GET or None)
        
        # Pour chaque document, rechercher les soumissions de documents qui pourraient y être liées
        # En pratique, on va chercher les soumissions de documents dont le nom contient le numéro
        # du document administratif, ce qui pourrait indiquer une relation
        for document in context['documents']:
            # Recherche de liens possibles entre ce document administratif et des soumissions
            # Par exemple, si le numéro du document apparaît dans un document soumis
            document_submissions = DocumentSubmission.objects.filter(
                Q(document__nom__icontains=document.numero) | 
                Q(document__description__icontains=document.numero)
            ).select_related('company')
            
            # Liste des sociétés uniques qui ont soumis un document potentiellement lié
            document.related_companies = list(set(sub.company for sub in document_submissions))
            
            # Si nous n'avons pas trouvé de sociétés liées par le numéro,
            # essayons de trouver par le titre du document
            if not document.related_companies:
                # Diviser le titre en mots-clés et chercher des correspondances
                keywords = document.titre.split()
                significant_keywords = [kw for kw in keywords if len(kw) > 3]
                
                if significant_keywords:
                    # Chercher des soumissions de documents contenant un des mots-clés significatifs
                    keyword_filter = Q()
                    for keyword in significant_keywords:
                        keyword_filter |= Q(document__nom__icontains=keyword)
                        keyword_filter |= Q(document__description__icontains=keyword)
                    
                    keyword_submissions = DocumentSubmission.objects.filter(
                        keyword_filter
                    ).select_related('company')
                    
                    # Ajouter ces sociétés à notre liste
                    document.related_companies.extend(
                        set(sub.company for sub in keyword_submissions) - 
                        set(document.related_companies)
                    )
                    
                    # Limiter à 5 sociétés maximum pour l'affichage
                    document.related_companies = document.related_companies[:5]
        
        return context
