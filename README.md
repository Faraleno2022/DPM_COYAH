# DPMG Coyah - Système de Gestion Documentaire

Application de gestion documentaire pour la Direction Préfectorale des Mines et Géologie de Coyah, permettant la gestion des sociétés de carrières et leurs documents réglementaires.

## Fonctionnalités principales

### Partie publique
- Consultation de la liste des sociétés et de leurs informations
- Visualisation des documents soumis par chaque société
- Formulaire de dépôt de documents pour les sociétés

### Partie administrative
- Interface d'administration sécurisée
- Gestion complète des sociétés (CRUD)
- Gestion des documents administratifs (décrets, arrêtés, notes de service)
- Statistiques et tableaux de bord
- Suivi des soumissions de documents

## Prérequis

- Python 3.8+
- Django 4.x
- Base de données SQLite en développement (PostgreSQL recommandé en production)

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-utilisateur/dpmg-coyah.git
   cd dpmg-coyah
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   ```

3. **Activer l'environnement virtuel**
   - Windows : 
     ```bash
     venv\Scripts\activate
     ```
   - Unix/MacOS : 
     ```bash
     source venv/bin/activate
     ```

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialiser le projet**
   
   Cette commande va :
   - Appliquer les migrations
   - Charger les 25 documents requis dans la base de données
   - Créer un compte administrateur par défaut
   
   ```bash
   python manage.py initialize_project
   ```
   
   Vous pouvez également personnaliser le compte admin :
   ```bash
   python manage.py initialize_project --username=votre_admin --email=email@exemple.com --password=votre_mot_de_passe
   ```

6. **Démarrer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

7. **Accéder à l'application**
   - Interface principale : http://127.0.0.1:8000/
   - Interface d'administration : http://127.0.0.1:8000/admin/

## Structure du projet

- `companies` : Application pour la gestion des sociétés et de leurs documents
- `administration_docs` : Application pour la gestion des documents administratifs
- `templates` : Modèles HTML pour l'interface utilisateur
- `static` : Fichiers statiques (CSS, JS, images)
- `fixtures` : Données initiales pour les documents requis

## Documentation détaillée

### Liste des documents requis

Le système gère 25 types de documents requis pour chaque société :

1. Autorisation d'exploitation / Renouvellement
2. PV de bornage
3. Plan de gestion environnemental et social (PGES)
4. Autorisation / Certificat environnemental
5. Liste des travailleurs guinéens
6. Liste des travailleurs étrangers
7. Déclaration AGUPE/IGT
8. Carnet d'assurance sociale
9. Liste des engins et équipements
10. Assurance des engins
11. RCCM / Statut
12. Registre de production
13. États financiers N-1
14. Balance générale
15. DMU (année N-1)
16. Frais CPDM
17. Droit fixe / timbre
18. Taxe superficiaire
19. Permis de travail & passeports expats
20. PV délégation syndicale
21. Règlement intérieur
22. PV Comité SST + rapports
23. Liste des clients (volume vendu)
24. Fiche de liquidation + quittances
25. Immatriculation ONFPP + 3 quittances

### Conditions dynamiques sur les documents

Le système applique des règles conditionnelles pour les documents requis :
- Le PV de délégation syndicale est requis pour les entreprises de moins de 25 employés
- Le Règlement intérieur est obligatoire pour les entreprises de plus de 25 employés

## Déploiement en production

Pour le déploiement en production, il est recommandé de :

1. Utiliser PostgreSQL comme base de données
2. Configurer un stockage distant pour les fichiers (comme AWS S3)
3. Utiliser un serveur WSGI comme Gunicorn
4. Configurer un serveur web comme Nginx comme proxy inverse
5. Activer HTTPS avec Let's Encrypt

## Développement futur

- Notifications par email lors des soumissions de documents
- Export de rapports en PDF/Excel
- Tableaux de bord avancés avec graphiques
- Interface mobile optimisée

## Licence

Développé pour la Direction Préfectorale des Mines et Géologie de Coyah - Tous droits réservés
