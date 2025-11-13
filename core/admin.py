from django.contrib import admin

# Register your models here.

from .models import Client, Vehicule, Reservation, Paiement, Admin

admin.site.register(Client)
admin.site.register(Vehicule)
admin.site.register(Reservation)
admin.site.register(Paiement)
admin.site.register(Admin)
