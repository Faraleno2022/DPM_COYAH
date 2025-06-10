from django import forms
from django.contrib.auth.models import User, Group
from .models import Company, DocumentSubmission, RequiredDocument, DocumentVersion, DPMGProfile


class CompanyForm(forms.ModelForm):
    """Formulaire pour créer ou modifier une société"""
    class Meta:
        model = Company
        fields = ['nom', 'nombre_employes', 'adresse', 'telephone', 'email', 'date_autorisation']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_employes': forms.NumberInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date_autorisation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }


class DocumentSubmissionForm(forms.ModelForm):
    """Formulaire pour soumettre un document"""
    class Meta:
        model = DocumentSubmission
        fields = ['document', 'fichier']
        widgets = {
            'document': forms.Select(attrs={'class': 'form-select'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, company=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.company = company
        
        # Filtrer les documents qui n'ont pas encore été soumis par cette société
        if company:
            submitted_docs = DocumentSubmission.objects.filter(company=company).values_list('document_id', flat=True)
            self.fields['document'].queryset = RequiredDocument.objects.exclude(id__in=submitted_docs)


class DocumentUpdateForm(forms.ModelForm):
    """Formulaire pour mettre à jour un document existant"""
    notes = forms.CharField(
        label="Notes de version",
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Décrivez les modifications apportées dans cette nouvelle version...'
        }),
        required=False,
        help_text="Informations sur les changements apportés à cette version du document."
    )
    
    class Meta:
        model = DocumentSubmission
        fields = ['fichier']
        widgets = {
            'fichier': forms.FileInput(attrs={'class': 'form-control'})
        }


class DocumentVersionForm(forms.Form):
    """
    Formulaire pour ajouter une nouvelle version à un document existant
    """
    fichier = forms.FileField(
        label="Fichier",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label="Notes de version",
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Décrivez les modifications apportées dans cette version...'
        }),
        required=False,
        help_text="Informations sur les changements apportés à cette version du document."
    )


class MultiDocumentSubmissionForm(forms.Form):
    """
    Formulaire pour soumettre plusieurs documents à la fois.
    Ce formulaire génère dynamiquement un champ de fichier pour chaque document requis
    qui n'a pas encore été soumis par la société.
    """
    
    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        
        # Récupérer les documents déjà soumis par cette société
        submitted_docs = DocumentSubmission.objects.filter(
            company=company
        ).values_list('document_id', flat=True)
        
        # Récupérer les documents requis qui n'ont pas encore été soumis
        missing_docs = RequiredDocument.objects.exclude(id__in=submitted_docs)
        
        # Pour chaque document manquant, créer un champ de fichier
        for doc in missing_docs:
            field_name = f"document_{doc.id}"
            self.fields[field_name] = forms.FileField(
                required=False,  # optionnel pour permettre de soumettre seulement certains documents
                label=doc.nom,
                help_text=doc.description if doc.description else "",
                widget=forms.FileInput(attrs={
                    'class': 'form-control',
                    'data-document-id': doc.id,
                    'data-document-name': doc.nom
                })
            )


class RequiredDocumentsForm(forms.Form):
    """
    Formulaire spécifique pour la soumission des 25 documents administratifs requis.
    Ce formulaire contient un champ pour chacun des 25 documents obligatoires.
    """
    
    # Définition des 25 documents requis
    REQUIRED_DOCUMENTS = [
        (1, "Autorisation d'exploitation / Renouvellement"),
        (2, "PV de bornage"),
        (3, "Plan de gestion environnemental et social (PGES)"),
        (4, "Autorisation / Certificat environnemental"),
        (5, "Liste des travailleurs guinéens"),
        (6, "Liste des travailleurs étrangers"),
        (7, "Déclaration AGUPE/IGT"),
        (8, "Carnet d'assurance sociale"),
        (9, "Liste des engins et équipements"),
        (10, "Assurance des engins"),
        (11, "RCCM / Statut"),
        (12, "Registre de production"),
        (13, "Etats financiers N-1"),
        (14, "Balance générale"),
        (15, "DMU (année N-1)"),
        (16, "Frais CPDM"),
        (17, "Droit fixe / timbre"),
        (18, "Taxe superficiaire"),
        (19, "Permis de travail & passeports expats"),
        (20, "PV délégation syndicale (si < 25 employés)"),
        (21, "Règlement intérieur (< 25 employés)"),
        (22, "PV Comité SST + rapports"),
        (23, "Liste des clients (volume vendu)"),
        (24, "Fiche de liquidation + quittances"),
        (25, "Immatriculation ONFPP + 3 quittances"),
    ]
    
    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        
        # Récupérer les documents déjà soumis par cette société
        submitted_docs = DocumentSubmission.objects.filter(company=company)
        submitted_doc_names = [doc.document.nom.lower() for doc in submitted_docs]
        
        # Pour chaque document requis, créer un champ de fichier
        for doc_id, doc_name in self.REQUIRED_DOCUMENTS:
            # Vérifier si un document similaire a déjà été soumis (en comparant les noms)
            is_submitted = any(
                all(keyword.lower() in doc_submitted for keyword in doc_name.lower().split())
                for doc_submitted in submitted_doc_names
            )
            
            # Si le document n'est pas déjà soumis, ajouter un champ pour le soumettre
            field_name = f"document_{doc_id}"
            self.fields[field_name] = forms.FileField(
                required=False,  # Permet de soumettre seulement certains documents
                label=doc_name,
                widget=forms.FileInput(attrs={
                    'class': 'form-control',
                    'data-document-id': doc_id,
                    'data-document-name': doc_name,
                    'disabled': is_submitted,  # Désactiver le champ si document déjà soumis
                })
            )
            
            # Si le document est déjà soumis, ajouter un champ caché pour l'indiquer
            if is_submitted:
                self.fields[f"{field_name}_submitted"] = forms.BooleanField(
                    initial=True,
                    widget=forms.HiddenInput(),
                    required=False
                )


class EmailDocumentForm(forms.Form):
    """
    Formulaire pour envoyer un document par email.
    """
    recipient_email = forms.EmailField(
        label="Adresse email du destinataire",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=False
    )


class EmailDocumentsForm(forms.Form):
    """
    Formulaire pour envoyer plusieurs documents par email.
    """
    recipient_email = forms.EmailField(
        label="Adresse email du destinataire",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=False
    )


# Formulaires pour l'inscription et la gestion des comptes DPMG
class DPMGRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription pour un nouveau DPMG"""
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"})
    )
    email = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Adresse e-mail"})
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Mot de passe"})
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Confirmer le mot de passe"})
    )
    
    class Meta:
        model = DPMGProfile
        fields = ['prefecture', 'region', 'telephone', 'adresse', 'code_dpmg', 'logo']
        widgets = {
            'prefecture': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Préfecture'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Région'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse complète'}),
            'code_dpmg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code unique DPMG'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean_password2(self):
        """Vérifie que les deux mots de passe sont identiques"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2
    
    def clean_username(self):
        """Vérifie que le nom d'utilisateur est unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username
    
    def clean_email(self):
        """Vérifie que l'adresse e-mail est unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email
    
    def clean_code_dpmg(self):
        """Vérifie que le code DPMG est unique"""
        code_dpmg = self.cleaned_data.get('code_dpmg')
        if DPMGProfile.objects.filter(code_dpmg=code_dpmg).exists():
            raise forms.ValidationError("Ce code DPMG est déjà utilisé.")
        return code_dpmg
    
    def save(self, commit=True):
        """Crée un nouvel utilisateur et un profil DPMG associé"""
        # Ne pas enregistrer le formulaire directement, nous le ferons manuellement
        dpmg_profile = super().save(commit=False)
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        
        # Attribuer des permissions spécifiques au DPMG
        # On peut définir un groupe de permissions spécifiques pour les DPMG
        dpmg_group, created = Group.objects.get_or_create(name='DPMG')
        user.groups.add(dpmg_group)
        
        # Associer l'utilisateur au profil DPMG
        dpmg_profile.user = user
        
        if commit:
            dpmg_profile.save()
        
        return dpmg_profile


class DPMGProfileForm(forms.ModelForm):
    """Formulaire pour la mise à jour du profil DPMG"""
    class Meta:
        model = DPMGProfile
        fields = ['prefecture', 'region', 'telephone', 'adresse', 'logo']
        widgets = {
            'prefecture': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le logo optionnel pour permettre de le conserver inchangé
        self.fields['logo'].required = False
