# Guide de déploiement sur PythonAnywhere
Ce guide vous explique comment déployer l'application DPMG Coyah sur PythonAnywhere.

## 1. Créer un compte PythonAnywhere

Si ce n'est pas déjà fait, créez un compte sur [PythonAnywhere](https://www.pythonanywhere.com/).

## 2. Télécharger le projet sur PythonAnywhere

### Option 1: Via Git (recommandé)
1. Dans la console PythonAnywhere, clonez votre dépôt :
   ```bash
   git clone https://github.com/votre-compte/dpmg-coyah.git
   ```

### Option 2: Via téléchargement direct
1. Compressez le dossier du projet en ZIP
2. Allez dans la section "Files" de PythonAnywhere
3. Téléversez le fichier ZIP
4. Décompressez-le avec :
   ```bash
   unzip votre-projet.zip
   ```

## 3. Configuration de l'environnement virtuel

1. Dans la console PythonAnywhere, créez un environnement virtuel :
   ```bash
   mkvirtualenv --python=python3.11 dpmg_venv
   ```

2. Activez l'environnement et installez les dépendances :
   ```bash
   workon dpmg_venv
   cd ~/dpmg-coyah
   pip install -r requirements.txt
   ```

## 4. Créer et configurer le fichier .env

Créez un fichier `.env` dans le répertoire du projet avec les variables suivantes :
```
DJANGO_SECRET_KEY=votre_clé_secrète_très_longue_et_aléatoire
DJANGO_DEBUG=False
ENCRYPTION_KEY=votre_clé_de_chiffrement_32_caractères
EMAIL_HOST=smtp.votre-fournisseur.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@example.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-email
DEFAULT_FROM_EMAIL=noreply@dpmg-coyah.gov.gn
```

## 5. Configurer la base de données

1. Créez la base de données :
   ```bash
   cd ~/dpmg-coyah
   python manage.py migrate
   ```

2. Créez un superutilisateur :
   ```bash
   python manage.py createsuperuser
   ```

## 6. Collecter les fichiers statiques

```bash
python manage.py collectstatic --no-input
```

## 7. Configurer l'application web PythonAnywhere

1. Allez dans l'onglet "Web" de PythonAnywhere
2. Cliquez sur "Add a new web app"
3. Choisissez "Manual configuration"
4. Sélectionnez Python 3.11

5. Configurez le chemin vers le virtualenv :
   `/home/votre-username/.virtualenvs/dpmg_venv`

6. Configurez le fichier WSGI en cliquant sur le lien correspondant et remplacez son contenu par :
   ```python
   import os
   import sys

   # Remplacez 'votre-username' par votre nom d'utilisateur PythonAnywhere
   path = '/home/votre-username/dpmg-coyah'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'dpmg_project.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

7. Dans la section "Static files", ajoutez :
   - URL : `/static/`
   - Path : `/home/votre-username/dpmg-coyah/staticfiles`

8. Et pour les médias :
   - URL : `/media/`
   - Path : `/home/votre-username/dpmg-coyah/media`

## 8. Redémarrer l'application

Cliquez sur le bouton "Reload" pour appliquer les changements.

## 9. Accéder à l'application

Votre application est maintenant disponible à l'adresse `https://votre-username.pythonanywhere.com`

## Résolution de problèmes

### Erreur 500
- Vérifiez les logs d'erreurs dans l'onglet "Web"
- Assurez-vous que toutes les dépendances sont installées
- Vérifiez que le fichier .env est correctement configuré

### Problèmes avec les fichiers statiques
- Assurez-vous que `collectstatic` a bien été exécuté
- Vérifiez la configuration des URL et chemins statiques

### Problèmes de base de données
- Vérifiez les permissions de fichiers SQLite
- Assurez-vous que les migrations ont été appliquées
