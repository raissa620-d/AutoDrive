from django.contrib import admin
from .models import Admin, Client, Paiement, Reservation, Vehicule

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_prenom', 'get_nom', 'get_email', 'telephone', 'adresse')

    def get_prenom(self, obj):
        return obj.user.first_name
    get_prenom.short_description = 'Prénom'

    def get_nom(self, obj):
        return obj.user.last_name
    get_nom.short_description = 'Nom'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('marque', 'modele', 'immatriculation', 'categorie', 'prix_jour', 'statut', 'transmission', 'carburant', 'places', 'ville')
    list_filter = ('categorie', 'statut', 'transmission', 'carburant', 'ville')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("client", "vehicule", "date_debut", "date_fin", "statut", "montant_total")
    list_filter = ("statut",)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("reservation", "montant", "mode_paiement", "date_paiement")


@admin.register(Admin)
class CustomAdmin(admin.ModelAdmin):
    list_display = ("nom", "email")
