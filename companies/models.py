from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.conf import settings
from django.core.exceptions import ValidationError

# Ajout des validateurs d'upload sécurisé
def validate_file_size(value):
    """Valide que le fichier ne dépasse pas 10MB"""
    filesize = value.size
    
    if filesize > 10 * 1024 * 1024:  # 10MB limite
        raise ValidationError("La taille maximale de fichier autorisée est 10 MB.")

# Définir les extensions de fichiers autorisées
ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']

# Pour le moment, nous utilisons TextField standard en développement
# La version chiffrée sera implémentée plus tard en production


class Company(models.Model):
    """Modèle représentant une société de carrière"""
    nom = models.CharField("Nom de la société", max_length=255, unique=True)
    date_creation = models.DateField("Date de création", auto_now_add=True)
    nombre_employes = models.PositiveIntegerField("Nombre d'employés", default=0, validators=[MinValueValidator(0)])
    adresse = models.CharField("Adresse", max_length=255, blank=True, null=True)
    telephone = models.CharField("Téléphone", max_length=20, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)
    date_autorisation = models.DateField("Date d'autorisation d'exploitation", blank=True, null=True)
    
    class Meta:
        verbose_name = "Société"
        verbose_name_plural = "Sociétés"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom
    
    def get_absolute_url(self):
        return reverse('company_detail', args=[str(self.id)])
    
    def documents_requis(self):
        """Retourne la liste des documents requis pour cette société en fonction de ses caractéristiques"""
        from .models import RequiredDocument
        
        # Documents de base requis pour toutes les sociétés
        docs = RequiredDocument.objects.filter(condition__isnull=True)
        
        # Documents conditionnels basés sur le nombre d'employés
        if self.nombre_employes <= 25:
            # PV délégation syndicale pour les entreprises < 25 employés
            docs = docs | RequiredDocument.objects.filter(nom__icontains="délégation syndicale")
        else:
            # Règlement intérieur pour les entreprises > 25 employés
            docs = docs | RequiredDocument.objects.filter(nom__icontains="Règlement intérieur")
            
        return docs
    
    def get_document_completion(self):
        """
        Calcule le pourcentage de complétion des documents requis pour la société.
        Retourne un entier entre 0 et 100.
        """
        # Récupérer les documents requis et soumis
        documents_requis = self.documents_requis().count()
        documents_soumis = self.submissions.count()
        
        # Éviter la division par zéro
        if documents_requis == 0:
            return 0
            
        # Calculer le pourcentage, avec un maximum de 100%
        pourcentage = min(int((documents_soumis / documents_requis) * 100), 100)
        return pourcentage
    
    def get_documents_manquants(self):
        """
        Retourne la liste des documents requis mais non soumis par la société.
        Cette méthode est utile pour éviter de recalculer cette liste dans différentes vues.
        """
        # Récupérer la liste des documents requis
        required_docs = self.documents_requis()
        
        # Liste des IDs des documents déjà soumis
        submitted_doc_ids = self.submissions.values_list('document_id', flat=True)
        
        # Retourner les documents requis qui ne sont pas dans la liste des soumis
        return required_docs.exclude(id__in=submitted_doc_ids)


class RequiredDocument(models.Model):
    """Modèle représentant un type de document requis pour les sociétés"""
    nom = models.CharField("Nom du document", max_length=255)
    description = models.TextField("Description", blank=True, null=True)
    condition = models.TextField("Condition d'application", blank=True, null=True)
    
    class Meta:
        verbose_name = "Document requis"
        verbose_name_plural = "Documents requis"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


def document_upload_path(instance, filename):
    """Définir le chemin d'upload pour les documents soumis"""
    # Format: documents/societe_id/type_document/filename
    return f'documents/{instance.company.id}/{instance.document.id}/{filename}'


class DocumentSubmission(models.Model):
    """Modèle représentant un document soumis par une société"""
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='submissions',
        verbose_name="Société"
    )
    document = models.ForeignKey(
        RequiredDocument, 
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name="Type de document"
    )
    fichier = models.FileField(
        "Fichier", 
        upload_to=document_upload_path, 
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS),
            validate_file_size
        ]
    )
    date_submission = models.DateTimeField("Date de soumission", auto_now_add=True)
    
    class Meta:
        verbose_name = "Document soumis"
        verbose_name_plural = "Documents soumis"
        ordering = ['-date_submission']
        # Un seul document actif par type et par société
        unique_together = ['company', 'document']
    
    def __str__(self):
        return f"{self.document.nom} - {self.company.nom}"
    
    def get_absolute_url(self):
        return reverse('document_detail', args=[str(self.id)])
    
    def get_versions(self):
        """Retourne toutes les versions de ce document classées par date"""
        return self.versions.all().order_by('-date_creation')
    
    def get_current_version(self):
        """Retourne la version actuelle du document"""
        return self.versions.filter(is_current=True).first()
    
    def create_new_version(self, fichier, notes=None):
        """Crée une nouvelle version pour ce document"""
        # Désactiver l'ancienne version active
        self.versions.filter(is_current=True).update(is_current=False)
        
        # Créer la nouvelle version
        version = DocumentVersion.objects.create(
            document=self,
            fichier=fichier,
            is_current=True,
            notes=notes or ""
        )
        
        # Mettre à jour le fichier principal
        self.fichier = fichier
        self.save()
        
        return version


class DocumentVersion(models.Model):
    """Modèle pour gérer les différentes versions d'un document"""
    document = models.ForeignKey(
        DocumentSubmission,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name="Document"
    )
    fichier = models.FileField(
        "Fichier", 
        upload_to='documents/versions/',
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS),
            validate_file_size
        ]
    )
    date_creation = models.DateTimeField(
        "Date de création",
        auto_now_add=True
    )
    notes = models.TextField(
        "Notes de version",
        blank=True,
        null=True
    )
    is_current = models.BooleanField(
        "Version actuelle",
        default=True
    )
    
    def __str__(self):
        return f"Version {self.id} - {self.document.document.nom} ({self.date_creation.strftime('%d/%m/%Y')})"


class DPMGProfile(models.Model):
    """Profil pour chaque Direction Préfectorale des Mines et de la Géologie"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dpmg_profile')
    prefecture = models.CharField(max_length=100, verbose_name="Préfecture")
    region = models.CharField(max_length=100, verbose_name="Région")
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    adresse = models.TextField(verbose_name="Adresse physique")  
    code_dpmg = models.CharField(max_length=20, unique=True, verbose_name="Code DPMG")
    logo = models.ImageField(upload_to='dpmg_logos/', blank=True, null=True, verbose_name="Logo")
    date_creation = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    
    class Meta:
        verbose_name = "Profil DPMG"
        verbose_name_plural = "Profils DPMG"
    
    def __str__(self):
        return f"DPMG {self.prefecture}"
