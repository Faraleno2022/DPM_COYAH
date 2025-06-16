"""
URL Configuration for dpmg_project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('companies/', include('companies.urls')),
    path('documents/', include('administration_docs.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Ne pas servir les fichiers média directement en production
# En développement, c'est acceptable pour faciliter le développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # En production, tous les fichiers média doivent passer par une vue sécurisée
    urlpatterns += [
        path('media/<path:path>', include('companies.secure_media_urls')),
    ]
