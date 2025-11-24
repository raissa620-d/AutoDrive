from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
   path('véhicules/', views.liste_véhicules, name='liste_véhicules'),
]

