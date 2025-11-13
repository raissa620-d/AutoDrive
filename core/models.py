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
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    immatriculation = models.CharField(max_length=50, unique=True)
    categorie = models.CharField(max_length=50)
    prix_jour = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, default='disponible')
    photo = models.ImageField(upload_to='vehicules/')

    def __str__(self):
        return f"{self.marque} {self.modele}"

class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, default='en attente')

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
