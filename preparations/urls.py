from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentification
    path('inscription/', views.inscription_view, name='inscription'),
    path('connexion/', auth_views.LoginView.as_view(template_name='registration/connexion.html', redirect_authenticated_user=True), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),

    # Tableau de bord
    path('', views.dashboard_view, name='dashboard'),

    # Module 1 : Fiches de préparation
    path('fiche/nouvelle/', views.creer_fiche_view, name='creer_fiche'),
    path('fiche/<int:pk>/', views.detail_fiche_view, name='detail_fiche'),
    path('fiche/<int:pk>/editer/', views.editer_fiche_view, name='editer_fiche'),
    path('fiche/<int:pk>/supprimer/', views.supprimer_fiche_view, name='supprimer_fiche'),
    path('fiche/<int:pk>/pdf/', views.exporter_pdf_fiche_view, name='exporter_pdf_fiche'),

    # Module 2 : QCM & Évaluations
    path('qcm/nouveau/', views.creer_qcm_view, name='creer_qcm'),
    path('qcm/<int:pk>/', views.detail_qcm_view, name='detail_qcm'),
    path('qcm/<int:pk>/supprimer/', views.supprimer_qcm_view, name='supprimer_qcm'),
    path('qcm/<int:pk>/pdf/<str:mode>/', views.exporter_pdf_qcm_view, name='exporter_pdf_qcm'),
]