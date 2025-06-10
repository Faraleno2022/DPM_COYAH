from django import forms
from .models import AdministrativeDocument


class AdministrativeDocumentForm(forms.ModelForm):
    """Formulaire pour créer ou modifier un document administratif"""
    
    class Meta:
        model = AdministrativeDocument
        fields = ['type', 'numero', 'titre', 'date_enregistrement', 'description', 'fichier']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'date_enregistrement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DocumentFilterForm(forms.Form):
    """Formulaire pour filtrer les documents administratifs récents"""
    
    TYPE_CHOICES = [('', 'Tous types')] + list(AdministrativeDocument.DOCUMENT_TYPES)
    
    type = forms.ChoiceField(
        choices=TYPE_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    keyword = forms.CharField(
        label="Mot-clé",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par numéro, titre ou description'
        })
    )
    
    date_min = forms.DateField(
        label="Date minimum",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_max = forms.DateField(
        label="Date maximum",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
