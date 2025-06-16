from django.urls import path
from . import views

urlpatterns = [
    # Routes pour les sociétés
    path('', views.CompanyListView.as_view(), name='company_list'),
    path('<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('create/', views.CompanyCreateView.as_view(), name='company_create'),
    path('<int:pk>/update/', views.CompanyUpdateView.as_view(), name='company_update'),
    path('<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
    
    # Routes pour les soumissions de documents
    path('<int:company_id>/submit/', views.submit_document, name='submit_document'),
    path('<int:company_id>/submit-multiple/', views.submit_multiple_documents, name='submit_multiple_documents'),
    path('<int:company_id>/submit-required/', views.submit_required_documents, name='submit_required_documents'),
    path('document/<int:pk>/update/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('document/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    
    # Routes pour visualiser et envoyer des documents par email
    path('document/<int:document_id>/view/', views.view_document, name='view_document'),
    path('document/<int:document_id>/email/', views.email_document, name='email_document'),
    path('<int:company_id>/email-documents/', views.email_multiple_documents, name='email_multiple_documents'),
    
    # Routes pour la gestion des versions de documents
    path('document/<int:document_id>/versions/', views.document_versions, name='document_versions'),
    path('document/version/<int:version_id>/activate/', views.activate_document_version, name='activate_document_version'),
    
    # Route pour la liste des documents requis
    path('required-docs/', views.required_docs_list, name='required_docs_list'),
    
    # URLs pour les comptes DPMG
    path('dpmg/register/', views.dpmg_register, name='dpmg_register'),
    path('dpmg/dashboard/', views.dpmg_dashboard, name='dpmg_dashboard'),
    path('dpmg/profile/', views.dpmg_profile, name='dpmg_profile'),
    path('dpmg/complete-profile/', views.complete_dpmg_profile, name='complete_dpmg_profile'),
    path('dpmg/list/', views.dpmg_list, name='dpmg_list'),
    path('dpmg/<int:dpmg_id>/', views.dpmg_detail, name='dpmg_detail'),
]
