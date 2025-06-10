import os
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Génère et applique les migrations pour les modifications de modèles'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Démarrage du processus de migration...'))
            
            # Générer les migrations
            self.stdout.write('Génération des migrations...')
            call_command('makemigrations', 'companies', verbosity=1)
            
            # Appliquer les migrations
            self.stdout.write('Application des migrations...')
            call_command('migrate', verbosity=1)
            
            self.stdout.write(self.style.SUCCESS('Migrations appliquées avec succès!'))
            
        except Exception as e:
            raise CommandError(f'Erreur lors de l\'application des migrations: {e}')
