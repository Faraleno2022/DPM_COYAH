import os
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Initialise le projet DPMG Coyah (migrations, documents requis et compte admin)'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Nom d\'utilisateur pour le compte admin')
        parser.add_argument('--email', type=str, default='admin@dpmgcoyah.gov.gn', help='Email pour le compte admin')
        parser.add_argument('--password', type=str, default='dpmgcoyah2023', help='Mot de passe pour le compte admin')

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Démarrage de l\'initialisation du projet DPMG Coyah...'))
            
            # 1. Générer et appliquer les migrations
            self.stdout.write('1. Application des migrations...')
            try:
                call_command('makemigrations', verbosity=1)
                call_command('migrate', verbosity=1)
                self.stdout.write(self.style.SUCCESS('✓ Migrations appliquées avec succès'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erreur lors de l\'application des migrations: {e}'))
                return
            
            # 2. Charger les documents requis
            self.stdout.write('2. Chargement des documents requis...')
            try:
                call_command('load_required_documents', verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS('✓ Documents requis chargés avec succès'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erreur lors du chargement des documents: {e}'))
            
            # 3. Créer un compte administrateur si nécessaire
            username = options['username']
            email = options['email']
            password = options['password']
            
            self.stdout.write(f'3. Création du compte administrateur ({username})...')
            try:
                if not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(username=username, email=email, password=password)
                    self.stdout.write(self.style.SUCCESS(f'✓ Compte administrateur créé: {username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'✓ Le compte administrateur {username} existe déjà'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erreur lors de la création du compte admin: {e}'))
            
            self.stdout.write(self.style.SUCCESS('Initialisation terminée!'))
            self.stdout.write('\nVous pouvez maintenant démarrer le serveur avec:')
            self.stdout.write(self.style.NOTICE('  python manage.py runserver'))
            self.stdout.write('\nAccédez à l\'interface d\'administration:')
            self.stdout.write(self.style.NOTICE('  http://127.0.0.1:8000/admin/'))
            self.stdout.write(f'  Utilisateur: {username}')
            self.stdout.write(f'  Mot de passe: {password}')
            
        except Exception as e:
            raise CommandError(f'Erreur lors de l\'initialisation du projet: {e}')
