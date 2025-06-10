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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # En production, utilisez un serveur web comme Nginx pour servir les fichiers statiques et médias
    # Ces lignes sont là pour information, elles n'ont pas d'effet sur le serveur de production
    # Tout doit être configuré au niveau du serveur web (Nginx/Apache)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
