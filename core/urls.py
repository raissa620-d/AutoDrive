from django.urls import path
from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
path("agences/", views.agences, name="agences"),


# Ajoutez cette ligne :
    path('contact/', views.contact, name='contact'),

    # Véhicules
    path("vehicules/", views.liste_vehicules, name="liste_vehicules"),
    path("vehicules/<int:vehicule_id>/reserver/", views.reserver_vehicule, name="reserver_vehicule"),

    # Paiement
    path("paiement/<int:reservation_id>/", views.paiement, name="paiement"),
    path("confirmation/<int:reservation_id>/", views.confirmation_paiement, name="confirmation_paiement"),

    # Authentification
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
# Dans la liste urlpatterns, ajoutez :
path("dashboard/", views.dashboard, name="dashboard"),
path("reservation/<int:reservation_id>/annuler/", views.annuler_reservation, name="annuler_reservation"),
]
