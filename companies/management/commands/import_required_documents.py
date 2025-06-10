from django.core.management.base import BaseCommand
from companies.models import RequiredDocument


class Command(BaseCommand):
    help = "Import la liste des 25 documents requis pour les sociétés"

    def handle(self, *args, **kwargs):
        # Liste des documents à créer
        documents = [
            {
                "nom": "Autorisation d'exploitation / Renouvellement",
                "description": "Document officiel d'autorisation d'exploitation ou son renouvellement"
            },
            {
                "nom": "PV de bornage",
                "description": "Procès-verbal de bornage du site d'exploitation"
            },
            {
                "nom": "Plan de gestion environnemental et social (PGES)",
                "description": "Document détaillant la gestion environnementale et sociale du site"
            },
            {
                "nom": "Autorisation / Certificat environnemental",
                "description": "Document officiel d'autorisation environnementale"
            },
            {
                "nom": "Liste des travailleurs guinéens",
                "description": "Liste à jour des employés de nationalité guinéenne"
            },
            {
                "nom": "Liste des travailleurs étrangers",
                "description": "Liste à jour des employés de nationalité étrangère"
            },
            {
                "nom": "Déclaration AGUPE/IGT",
                "description": "Déclaration officielle auprès de l'AGUPE ou l'IGT"
            },
            {
                "nom": "Carnet d'assurance sociale",
                "description": "Documentation relative à l'assurance sociale des employés"
            },
            {
                "nom": "Liste des engins et équipements",
                "description": "Inventaire des engins et équipements d'exploitation"
            },
            {
                "nom": "Assurance des engins",
                "description": "Polices d'assurance pour les engins d'exploitation"
            },
            {
                "nom": "RCCM / Statut",
                "description": "Registre du Commerce et du Crédit Mobilier et statuts de la société"
            },
            {
                "nom": "Registre de production",
                "description": "Document officiel détaillant la production de la société"
            },
            {
                "nom": "Etats financiers N-1",
                "description": "États financiers de l'année précédente"
            },
            {
                "nom": "Balance générale",
                "description": "Balance comptable générale"
            },
            {
                "nom": "DMU (année N-1)",
                "description": "Déclaration mensuelle unique de l'année précédente"
            },
            {
                "nom": "Frais CPDM",
                "description": "Justificatif de paiement des frais du Centre de Promotion et de Développement Minier"
            },
            {
                "nom": "Droit fixe / timbre",
                "description": "Justificatif de paiement des droits fixes et timbres"
            },
            {
                "nom": "Taxe superficiaire",
                "description": "Justificatif de paiement de la taxe superficiaire"
            },
            {
                "nom": "Permis de travail & passeports expats",
                "description": "Copies des permis de travail et passeports des employés expatriés"
            },
            {
                "nom": "PV délégation syndicale",
                "description": "Procès-verbal de la délégation syndicale",
                "condition": "nombre_employes <= 25"
            },
            {
                "nom": "Règlement intérieur",
                "description": "Règlement intérieur de l'entreprise",
                "condition": "nombre_employes > 25"
            },
            {
                "nom": "PV Comité SST + rapports",
                "description": "Procès-verbaux et rapports du Comité de Santé et Sécurité au Travail"
            },
            {
                "nom": "Liste des clients (volume vendu)",
                "description": "Liste des clients avec volumes de produits vendus"
            },
            {
                "nom": "Fiche de liquidation + quittances",
                "description": "Fiche de liquidation et quittances associées"
            },
            {
                "nom": "Immatriculation ONFPP + 3 quittances",
                "description": "Immatriculation à l'Office National de Formation et de Perfectionnement Professionnel avec quittances"
            },
        ]

        # Compteurs pour le rapport
        created_count = 0
        updated_count = 0

        for doc_data in documents:
            doc, created = RequiredDocument.objects.update_or_create(
                nom=doc_data["nom"],
                defaults={
                    "description": doc_data.get("description", ""),
                    "condition": doc_data.get("condition", None)
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Créé: {doc.nom}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Mis à jour: {doc.nom}"))
                
        # Afficher un résumé
        self.stdout.write(self.style.SUCCESS(
            f"Importation terminée! {created_count} documents créés, {updated_count} documents mis à jour."
        ))
