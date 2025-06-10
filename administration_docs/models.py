from django.db import models
from django.urls import reverse


def admin_doc_upload_path(instance, filename):
    """Chemin de téléchargement pour les documents administratifs"""
    # Format: admin_docs/type/numero/filename
    doc_type = instance.get_type_display().lower().replace(' ', '_')
    return f'admin_docs/{doc_type}/{instance.numero}/{filename}'


class AdministrativeDocument(models.Model):
    """Modèle pour les documents administratifs (décrets, arrêtés, notes de service)"""
    
    # Types de documents administratifs
    DECRET = 'DECRET'
    ARRETE = 'ARRETE'
    NOTE = 'NOTE'
    
    DOCUMENT_TYPES = [
        (DECRET, 'Décret'),
        (ARRETE, 'Arrêté'),
        (NOTE, 'Note de service'),
    ]
    
    type = models.CharField(
        "Type de document", 
        max_length=10, 
        choices=DOCUMENT_TYPES
    )
    numero = models.CharField("Numéro", max_length=50)
    titre = models.CharField("Titre", max_length=255)
    date_enregistrement = models.DateField("Date d'enregistrement")
    date_creation = models.DateTimeField("Date de création", auto_now_add=True)
    description = models.TextField("Description", blank=True, null=True)
    fichier = models.FileField("Fichier", upload_to=admin_doc_upload_path)
    
    class Meta:
        verbose_name = "Document administratif"
        verbose_name_plural = "Documents administratifs"
        ordering = ['-date_enregistrement', 'type']
        # Les numéros doivent être uniques par type de document
        unique_together = ['type', 'numero']
    
    def __str__(self):
        return f"{self.get_type_display()} N°{self.numero} - {self.titre}"
    
    def get_absolute_url(self):
        return reverse('admin_doc_detail', kwargs={'pk': self.pk})
    
    @property
    def document_type_display(self):
        """Retourne l'affichage du type de document"""
        return self.get_type_display()
        
    @property
    def get_type_badge(self):
        """
        Retourne la classe CSS Bootstrap pour le badge correspondant au type de document
        - Décret: info (bleu)
        - Arrêté: warning (jaune)
        - Note: secondary (gris)
        """
        badge_classes = {
            self.DECRET: 'info',
            self.ARRETE: 'warning',
            self.NOTE: 'secondary',
        }
        return badge_classes.get(self.type, 'primary')
