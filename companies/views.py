from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.core.mail import EmailMessage
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.conf import settings
from mimetypes import guess_type
import os

from .models import Company, RequiredDocument, DocumentSubmission, DocumentVersion, DPMGProfile
# Utiliser un alias pour éviter tout conflit potentiel avec DocumentVersionForm
from .forms import (
    CompanyForm, DocumentSubmissionForm, DocumentUpdateForm, MultiDocumentSubmissionForm,
    RequiredDocumentsForm, EmailDocumentForm, EmailDocumentsForm, 
    DocumentVersionForm as DocumentVersionFormStandard,
    DPMGRegistrationForm, DPMGProfileForm
)
from administration_docs.models import AdministrativeDocument


class CompanyListView(ListView):
    """Affiche la liste des sociétés"""
    model = Company
    context_object_name = 'companies'
    template_name = 'companies/company_list.html'
    
    def get_queryset(self):
        """Optimisation: préchargement des soumissions de documents pour le calcul du pourcentage de complétion"""
        return Company.objects.prefetch_related('submissions').all()


class CompanyDetailView(DetailView):
    """Affiche le détail d'une société"""
    model = Company
    context_object_name = 'company'
    template_name = 'companies/company_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        
        # Liste des documents soumis par cette société
        submitted_docs = DocumentSubmission.objects.filter(company=company)
        context['submitted_docs'] = submitted_docs
        
        # Récupérer la liste des documents requis selon les caractéristiques de la société
        required_docs = company.documents_requis()
        context['required_docs'] = required_docs  # Ajout pour le modal
        
        # Liste des IDs des documents déjà soumis pour le modal
        context['submitted_doc_ids'] = submitted_docs.values_list('document_id', flat=True)
        
        # Utiliser la méthode du modèle pour obtenir les documents manquants
        context['missing_docs'] = company.get_documents_manquants()
        
        # Compteurs pour l'affichage
        total_required = required_docs.count()
        total_submitted = submitted_docs.count()
        context['total_required'] = total_required
        context['total_submitted'] = total_submitted
        
        # Calculer directement les documents manquants
        context['documents_manquants'] = total_required - total_submitted
        
        # Utiliser la méthode du modèle pour calculer le pourcentage de complétion
        context['completion_percentage'] = company.get_document_completion()
        
        # Ajouter les documents administratifs
        context['administrative_documents'] = AdministrativeDocument.objects.all().order_by('-date_enregistrement')
        
        return context


class CompanyCreateView(LoginRequiredMixin, CreateView):
    """Création d'une nouvelle société"""
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'
    success_url = reverse_lazy('company_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une nouvelle société'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Société créée avec succès!')
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    """Modification d'une société existante"""
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la société'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Société modifiée avec succès!')
        return super().form_valid(form)


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    """Suppression d'une société"""
    model = Company
    template_name = 'companies/company_confirm_delete.html'
    success_url = reverse_lazy('company_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Société supprimée avec succès!')
        return super().delete(request, *args, **kwargs)


@login_required
def submit_document(request, company_id):
    """Vue pour permettre à une société de soumettre un document"""
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == 'POST':
        form = DocumentSubmissionForm(company, request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.company = company
            submission.save()
            messages.success(request, 'Document soumis avec succès!')
            return redirect('company_detail', pk=company.id)
    else:
        form = DocumentSubmissionForm(company)
    
    return render(request, 'companies/submit_document.html', {
        'form': form,
        'company': company,
    })


@login_required
def submit_multiple_documents(request, company_id):
    """Vue pour permettre à une société de soumettre plusieurs documents à la fois"""
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == 'POST':
        form = MultiDocumentSubmissionForm(company, request.POST, request.FILES)
        
        if form.is_valid():
            files_submitted = 0
            
            # Parcourir tous les champs du formulaire
            for field_name, field_file in request.FILES.items():
                # Extraire l'ID du document à partir du nom du champ (document_X où X est l'ID)
                if field_name.startswith('document_'):
                    document_id = int(field_name.split('_')[1])
                    document = RequiredDocument.objects.get(id=document_id)
                    
                    # Créer une nouvelle soumission de document
                    submission = DocumentSubmission(
                        company=company,
                        document=document,
                        fichier=field_file
                    )
                    submission.save()
                    files_submitted += 1
            
            if files_submitted > 0:
                messages.success(
                    request, 
                    f'{files_submitted} document{"s" if files_submitted > 1 else ""} soumis avec succès!'
                )
            else:
                messages.warning(request, 'Aucun document n\'a été soumis.')
                
            return redirect('company_detail', pk=company.id)
    else:
        form = MultiDocumentSubmissionForm(company)
    
    return render(request, 'companies/submit_multiple_documents.html', {
        'form': form,
        'company': company,
    })


@login_required
def submit_required_documents(request, company_id):
    """Vue pour permettre à une société de soumettre les 25 documents administratifs requis"""
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == 'POST':
        form = RequiredDocumentsForm(company, request.POST, request.FILES)
        
        if form.is_valid():
            files_submitted = 0
            
            # Parcourir tous les champs du formulaire
            for field_name, field_file in request.FILES.items():
                # Extraire l'ID du document à partir du nom du champ (document_X où X est l'ID)
                if field_name.startswith('document_'):
                    doc_id = int(field_name.split('_')[1])
                    doc_name = next((name for id, name in RequiredDocumentsForm.REQUIRED_DOCUMENTS if id == doc_id), None)
                    
                    if doc_name:
                        # Trouver ou créer un document requis correspondant
                        doc, created = RequiredDocument.objects.get_or_create(
                            nom=doc_name,
                            defaults={'description': f"Document administratif requis #{doc_id}"}
                        )
                        
                        # Créer une nouvelle soumission de document
                        submission = DocumentSubmission(
                            company=company,
                            document=doc,
                            fichier=field_file
                        )
                        submission.save()
                        files_submitted += 1
            
            if files_submitted > 0:
                messages.success(
                    request, 
                    f'{files_submitted} document{"s" if files_submitted > 1 else ""} soumis avec succès!'
                )
            else:
                messages.warning(request, 'Aucun document n\'a été soumis.')
                
            return redirect('company_detail', pk=company.id)
    else:
        form = RequiredDocumentsForm(company)
    
    # Préparer des données pour simplifier l'accès dans le template
    documents_data = []
    for doc_id, doc_name in RequiredDocumentsForm.REQUIRED_DOCUMENTS:
        field_name = f"document_{doc_id}"
        submitted_field_name = f"{field_name}_submitted"
        is_submitted = submitted_field_name in form.fields
        
        documents_data.append({
            'id': doc_id,
            'name': doc_name,
            'field_name': field_name,
            'is_submitted': is_submitted,
            'field': form[field_name] if not is_submitted else None
        })
    
    return render(request, 'companies/submit_required_documents.html', {
        'form': form,
        'company': company,
        'documents_data': documents_data
    })


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    """Mise à jour d'un document soumis"""
    model = DocumentSubmission
    form_class = DocumentUpdateForm
    template_name = 'companies/document_update.html'
    
    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.id})
    
    def form_valid(self, form):
        # Récupérer l'instance existante
        self.object = form.save(commit=False)
        
        # Créer une nouvelle version du document
        fichier = self.request.FILES.get('fichier')
        if fichier:
            # Utiliser la méthode create_new_version pour créer une version
            self.object.create_new_version(fichier)
            
            # Ajouter des notes de version si fournies
            notes = form.cleaned_data.get('notes', 'Mise à jour du document')
            latest_version = self.object.get_current_version()
            if latest_version:
                latest_version.notes = notes
                latest_version.save()
        
        messages.success(self.request, 'Document mis à jour avec succès!')
        return super(UpdateView, self).form_valid(form)


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    """Suppression d'un document soumis"""
    model = DocumentSubmission
    template_name = 'companies/document_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.id})
        
    def get_object(self, queryset=None):
        """
        Récupère l'objet avec gestion des erreurs.
        """
        try:
            return super().get_object(queryset)
        except Http404:
            # Journaliser l'erreur
            print(f"Document non trouvé: {self.kwargs.get('pk')}")
            return None
    
    def post(self, request, *args, **kwargs):
        """
        Intercepte la requête POST pour vérifier si l'objet existe.
        """
        self.object = self.get_object()
        if self.object is None:
            messages.error(request, "Le document demandé n'existe pas ou a déjà été supprimé.")
            # Rediriger vers la page précédente ou la liste des sociétés
            if request.META.get('HTTP_REFERER'):
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                return redirect('company_list')
        
        # Si l'objet existe, procéder à la suppression
        return self.delete(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """
        Effectue la suppression avec gestion des erreurs.
        """
        try:
            company_id = self.object.company.id
            document_name = self.object.document.nom
            result = super().delete(request, *args, **kwargs)
            messages.success(request, f"Le document '{document_name}' a été supprimé avec succès.")
            return result
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
            return redirect('company_list')


@login_required
def view_document(request, document_id):
    """Vue pour visualiser un document en ligne avec prévisualisation intégrée"""
    document = get_object_or_404(DocumentSubmission, pk=document_id)
    
    # Vérifier les autorisations
    if not request.user.is_superuser and not document.company.user_has_access(request.user):
        raise PermissionDenied
    
    # Vérifier si une version spécifique est demandée
    version_id = request.GET.get('version')
    if version_id:
        try:
            version = DocumentVersion.objects.get(pk=version_id, document=document)
            fichier = version.fichier
            version_info = version
        except DocumentVersion.DoesNotExist:
            messages.error(request, "La version demandée n'existe pas.")
            fichier = document.fichier
            version_info = None
    else:
        fichier = document.fichier
        version_info = None
    
    # Obtenir le chemin du fichier
    fichier_path = fichier.path
    
    # Obtenir le type MIME
    content_type, encoding = guess_type(fichier_path)
    if not content_type:
        content_type = 'application/octet-stream'
    
    # Déterminer le type de visualisation en fonction du MIME type
    file_extension = fichier.name.split('.')[-1].lower()
    file_name = os.path.basename(fichier_path)
    file_size = fichier.size if hasattr(fichier, 'size') else os.path.getsize(fichier_path)
    
    # Format de taille lisible
    def human_readable_size(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    # Si mode=raw est spécifié, renvoyer le fichier brut à la place
    if request.GET.get('mode') == 'raw':
        # Ouvrir le fichier et créer une réponse pour l'afficher en ligne
        with open(fichier_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            
            # Utiliser Content-Disposition: inline pour afficher dans le navigateur
            response['Content-Disposition'] = f'inline; filename="{file_name}"'
            
            return response
    
    context = {
        'document': document,
        'fichier': fichier,
        'fichier_path': fichier_path,
        'file_name': file_name,
        'file_extension': file_extension,
        'file_size': human_readable_size(file_size),
        'content_type': content_type,
        'raw_url': f"{request.path}?mode=raw{f'&version={version_id}' if version_id else ''}",
        'version_info': version_info,
        'company': document.company
    }
    
    return render(request, 'companies/document_viewer.html', context)


@login_required
def email_document(request, document_id):
    """Vue pour envoyer un document par email"""
    document = get_object_or_404(DocumentSubmission, pk=document_id)
    
    # Vérifier les autorisations
    if not request.user.is_superuser and not document.company.user_has_access(request.user):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = EmailDocumentForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            message = form.cleaned_data['message']
            
            try:
                # Envoyer l'email avec le document en pièce jointe
                email = EmailMessage(
                    subject=f"Document DPMG: {document.document.nom} - {document.company.nom}",
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient_email],
                )
                
                # Ajouter le document en pièce jointe
                email.attach_file(document.fichier.path)
                
                # Envoyer l'email
                email.send()
                
                messages.success(request, f"Le document a été envoyé à {recipient_email}")
                return redirect('company_detail', pk=document.company.id)
                
            except Exception as e:
                messages.error(request, f"Erreur lors de l'envoi de l'email: {str(e)}")
        
    else:
        form = EmailDocumentForm()
    
    return render(request, 'companies/email_document.html', {
        'form': form,
        'document': document,
        'company': document.company
    })


@login_required
def email_multiple_documents(request, company_id):
    """Vue pour envoyer plusieurs documents par email"""
    company = get_object_or_404(Company, pk=company_id)
    
    # Vérifier les autorisations
    if not request.user.is_superuser and not company.user_has_access(request.user):
        raise PermissionDenied
    
    # Récupérer tous les documents de la société
    documents = DocumentSubmission.objects.filter(company=company)
    
    if request.method == 'POST':
        form = EmailDocumentsForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            message = form.cleaned_data['message']
            selected_documents = request.POST.getlist('documents')
            
            # Vérifier qu'au moins un document est sélectionné
            if not selected_documents:
                messages.warning(request, "Veuillez sélectionner au moins un document à envoyer.")
                return render(request, 'companies/email_multiple_documents.html', {
                    'form': form,
                    'documents': documents,
                    'company': company
                })
            
            try:
                # Créer l'email
                email = EmailMessage(
                    subject=f"Documents DPMG pour {company.nom}",
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient_email],
                )
                
                # Ajouter les documents sélectionnés en pièces jointes
                for doc_id in selected_documents:
                    document = documents.filter(id=doc_id).first()
                    if document:
                        email.attach_file(document.fichier.path)
                
                # Envoyer l'email
                email.send()
                
                messages.success(request, f"Les documents ont été envoyés à {recipient_email}")
                return redirect('company_detail', pk=company.id)
                
            except Exception as e:
                messages.error(request, f"Erreur lors de l'envoi de l'email: {str(e)}")
        
    else:
        form = EmailDocumentsForm()
    
    return render(request, 'companies/email_multiple_documents.html', {
        'form': form,
        'documents': documents,
        'company': company
    })


@login_required
def required_docs_list(request):
    """
    Affiche la liste de toutes les sociétés avec leur statut de complétion des 25 documents requis.
    """
    companies = Company.objects.all().order_by('nom')
    companies_data = []
    
    for company in companies:
        # Calculer le nombre de documents soumis et le pourcentage de complétion
        submitted_docs = DocumentSubmission.objects.filter(company=company)
        required_docs = company.documents_requis()
        
        companies_data.append({
            'company': company,
            'total_required': required_docs.count(),
            'total_submitted': submitted_docs.count(),
            'completion_percentage': company.get_document_completion(),
            'missing_count': required_docs.count() - submitted_docs.count()
        })
    
    context = {
        'companies_data': companies_data,
        'title': 'Liste des sociétés - Documents requis'
    }
    
    return render(request, 'companies/required_docs_list.html', context)


@login_required
def document_versions(request, document_id):
    """
    Affiche l'historique des versions d'un document et permet d'ajouter une nouvelle version.
    """
    # Récupérer le document
    document = get_object_or_404(DocumentSubmission, pk=document_id)
    
    # Vérifier les autorisations
    if not request.user.is_superuser and not document.company.user_has_access(request.user):
        raise PermissionDenied
    
    # Récupérer toutes les versions du document
    versions = DocumentVersion.objects.filter(document=document).order_by('-date_creation')
    
    if request.method == 'POST':
        form = DocumentVersionFormStandard(request.POST, request.FILES)
        if form.is_valid():
            fichier = form.cleaned_data['fichier']
            notes = form.cleaned_data['notes']
            
            # Créer une nouvelle version
            document.create_new_version(fichier, notes)
            
            messages.success(request, "Nouvelle version ajoutée avec succès!")
            return redirect('document_versions', document_id=document.id)
    else:
        form = DocumentVersionFormStandard()
    
    return render(request, 'companies/document_versions.html', {
        'document': document,
        'versions': versions,
        'form': form
    })


@login_required
def activate_document_version(request, version_id):
    """
    Active une version spécifique d'un document (la définit comme version courante).
    """
    # Récupérer la version
    version = get_object_or_404(DocumentVersion, pk=version_id)
    document = version.document
    
    # Vérifier les autorisations
    if not request.user.is_superuser and not document.company.user_has_access(request.user):
        raise PermissionDenied
    
    try:
        # Désactiver toutes les versions
        DocumentVersion.objects.filter(document=document).update(is_current=False)
        
        # Activer la version demandée
        version.is_current = True
        version.save()
        
        messages.success(request, "Version activée avec succès!")
    except Exception as e:
        messages.error(request, f"Erreur lors de l'activation de la version: {str(e)}")
    
    return redirect('document_versions', document_id=document.id)


# ======== Vues pour la gestion des comptes DPMG ========

def dpmg_register(request):
    """
    Vue pour l'inscription d'un nouveau DPMG.
    """
    if request.method == 'POST':
        form = DPMGRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            dpmg = form.save()
            messages.success(request, f"Le compte DPMG pour {dpmg.prefecture} a été créé avec succès! Vous pouvez maintenant vous connecter.")
            return redirect('login')
    else:
        form = DPMGRegistrationForm()
    
    return render(request, 'dpmg/register.html', {
        'form': form,
        'title': "Inscription d'un nouveau DPMG"
    })


@login_required
def dpmg_dashboard(request):
    """
    Tableau de bord spécifique pour les utilisateurs DPMG.
    """
    # Vérifier si l'utilisateur est un DPMG
    try:
        dpmg_profile = request.user.dpmg_profile
    except:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    
    # Récupérer les sociétés qui relèvent de ce DPMG
    # Par défaut, on suppose que toutes les sociétés sont accessibles à tous les DPMG
    # Vous pourriez ajuster cela pour filtrer par région ou préfecture
    companies = Company.objects.all().order_by('nom')
    
    # Statistiques pour le tableau de bord
    stats = {
        'total_companies': companies.count(),
        'total_documents': DocumentSubmission.objects.filter(company__in=companies).count(),
        'recent_submissions': DocumentSubmission.objects.filter(company__in=companies).order_by('-date_submission')[:5],
        'incomplete_companies': [
            {
                'company': company,
                'missing_count': company.get_documents_manquants().count(),
                'completion_percentage': company.get_document_completion()
            }
            for company in companies if company.get_document_completion() < 100
        ]
    }
    
    return render(request, 'dpmg/dashboard.html', {
        'dpmg': dpmg_profile,
        'stats': stats,
        'companies': companies,
        'title': f"Tableau de bord DPMG {dpmg_profile.prefecture}"
    })


@login_required
def dpmg_profile(request):
    """
    Vue pour afficher et modifier le profil d'un DPMG.
    """
    # Vérifier si l'utilisateur est un DPMG
    try:
        dpmg_profile = request.user.dpmgprofile
    except:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    
    if request.method == 'POST':
        # Utiliser notre formulaire dédié
        form = DPMGProfileForm(request.POST, request.FILES, instance=dpmg_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès!")
            return redirect('dpmg_profile')
    else:
        # Préremplir le formulaire avec les informations existantes
        form = DPMGProfileForm(instance=dpmg_profile)
    
    return render(request, 'dpmg/profile.html', {
        'form': form,
        'dpmg': dpmg_profile,
        'title': "Mon profil DPMG"
    })
