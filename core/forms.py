from django import forms


class ReservationForm(forms.Form):
    nom = forms.CharField(label="Nom", max_length=100)
    prenom = forms.CharField(label="Prénom", max_length=100)
    email = forms.EmailField(label="Email")
    telephone = forms.CharField(label="Téléphone", max_length=20)
    adresse = forms.CharField(label="Adresse", max_length=255, required=False)
    date_debut = forms.DateField(label="Date de début", widget=forms.DateInput(attrs={"type": "date"}))
    date_fin = forms.DateField(label="Date de fin", widget=forms.DateInput(attrs={"type": "date"}))
