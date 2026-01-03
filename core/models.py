from django.db import models

# Create your models here.
from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=255)
    mot_de_passe = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Vehicule(models.Model):
    CATEGORIES = [
        ("citadine", "Citadine"),
        ("compacte", "Compacte"),
        ("berline", "Berline"),
        ("suv", "SUV"),
        ("utilitaire", "Utilitaire"),
    ]
    TRANSMISSIONS = [
        ("manuelle", "Manuelle"),
        ("automatique", "Automatique"),
    ]
    CARBURANTS = [
        ("essence", "Essence"),
        ("diesel", "Diesel"),
        ("electrique", "Electrique"),
        ("hybride", "Hybride"),
    ]
    STATUTS = [
        ("disponible", "Disponible"),
        ("indisponible", "Indisponible"),
        ("maintenance", "Maintenance"),
    ]

    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    immatriculation = models.CharField(max_length=50, unique=True)
    categorie = models.CharField(max_length=50, choices=CATEGORIES)
    prix_jour = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUTS, default="disponible")
    transmission = models.CharField(max_length=20, choices=TRANSMISSIONS, default="manuelle")
    carburant = models.CharField(max_length=20, choices=CARBURANTS, default="essence")
    places = models.PositiveSmallIntegerField(default=5)
    adresse = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="vehicules/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["marque", "modele"]

    def __str__(self):
        return f"{self.marque} {self.modele}"

    @property
    def is_geolocated(self):
        return self.latitude is not None and self.longitude is not None


class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, default="en attente")

    def __str__(self):
        return f"Réservation {self.id} - {self.client}"


class Paiement(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    date_paiement = models.DateTimeField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=50)

    def __str__(self):
        return f"Paiement {self.id} - {self.reservation}"


class Admin(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=255)

    def __str__(self):
        return self.nom
