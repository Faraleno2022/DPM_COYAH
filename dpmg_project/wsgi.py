"""
WSGI config for dpmg_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Ajout du chemin du projet au path système
# Remplacer 'username' par votre nom d'utilisateur PythonAnywhere et ajuster le chemin
# path = '/home/username/dpmg_project'
# if path not in sys.path:
#    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpmg_project.settings')

application = get_wsgi_application()
