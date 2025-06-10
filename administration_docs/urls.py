from django.urls import path
from . import views

urlpatterns = [
    # Routes générales pour tous les documents administratifs
    path('', views.AdministrativeDocumentListView.as_view(), name='admin_doc_list'),
    path('<int:pk>/', views.AdministrativeDocumentDetailView.as_view(), name='admin_doc_detail'),
    path('create/', views.AdministrativeDocumentCreateView.as_view(), name='admin_doc_create'),
    path('<int:pk>/update/', views.AdministrativeDocumentUpdateView.as_view(), name='admin_doc_update'),
    path('<int:pk>/delete/', views.AdministrativeDocumentDeleteView.as_view(), name='admin_doc_delete'),
    
    # Route pour les 25 derniers documents avec sociétés
    path('recent-with-companies/', views.RecentDocsWithCompaniesView.as_view(), name='recent_docs_with_companies'),
    
    # Routes pour les types spécifiques de documents
    path('decrets/', views.DecretListView.as_view(), name='decret_list'),
    path('arretes/', views.ArreteListView.as_view(), name='arrete_list'),
    path('notes/', views.NoteServiceListView.as_view(), name='note_list'),
]
