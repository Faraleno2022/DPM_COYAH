import os
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction
from companies.models import RequiredDocument


class Command(BaseCommand):
    help = 'Charge les données initiales des 25 documents requis conformément au cahier des charges'

    def handle(self, *args, **options):
        try:
            # Vérifier si des documents existent déjà
            existing_docs = RequiredDocument.objects.count()
            
            if existing_docs > 0:
                self.stdout.write(self.style.WARNING(
                    f'{existing_docs} documents requis existent déjà. '
                    'Voulez-vous continuer et risquer des doublons? (y/n)'
                ))
                
                answer = input().lower()
                if answer != 'y':
                    self.stdout.write(self.style.SUCCESS('Opération annulée.'))
                    return
            
            # Chemin vers le fichier de fixture
            fixture_path = 'companies/fixtures/initial_data.json'
            
            # Charger les fixtures en utilisant une transaction
            with transaction.atomic():
                call_command('loaddata', fixture_path, verbosity=1)
            
            # Afficher un message de succès
            new_count = RequiredDocument.objects.count() - existing_docs
            self.stdout.write(self.style.SUCCESS(
                f'Configuration réussie! {new_count} nouveaux documents requis ont été ajoutés à la base de données.'
            ))
            
        except Exception as e:
            raise CommandError(f'Erreur lors du chargement des données: {e}')
