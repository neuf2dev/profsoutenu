from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_fiches, name='liste_fiches'),
    path('nouvelle/', views.creer_fiche, name='creer_fiche'),
    path('fiche/<int:pk>/', views.detail_fiche, name='detail_fiche'),
    path('fiche/<int:pk>/modifier/', views.modifier_fiche, name='modifier_fiche'),
    path('fiche/<int:pk>/supprimer/', views.supprimer_fiche, name='supprimer_fiche'),
]