from django.contrib import admin

from .models import Admin, Client, Paiement, Reservation, Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ("marque", "modele", "categorie", "prix_jour", "statut", "ville")
    list_filter = ("categorie", "statut", "transmission", "carburant")
    search_fields = ("marque", "modele", "immatriculation", "ville")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("prenom", "nom", "email", "telephone")
    search_fields = ("nom", "prenom", "email")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("client", "vehicule", "date_debut", "date_fin", "statut")
    list_filter = ("statut",)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("reservation", "montant", "mode_paiement", "date_paiement")


@admin.register(Admin)
class CustomAdmin(admin.ModelAdmin):
    list_display = ("nom", "email")
