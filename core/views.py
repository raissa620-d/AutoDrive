from datetime import date
from decimal import Decimal, InvalidOperation
import re
import time
from django.shortcuts import render

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

from .forms import ReservationForm
from .models import Client, Reservation, Vehicule, Paiement


def _build_map_data(vehicules):
    points = []
    for vehicule in vehicules:
        if vehicule.is_geolocated:
            points.append({
                "label": f"{vehicule.marque} {vehicule.modele}",
                "lat": float(vehicule.latitude),
                "lng": float(vehicule.longitude),
                "adresse": vehicule.adresse or "",
                "ville": vehicule.ville or "",
                "prix_jour": float(vehicule.prix_jour),
                "categorie": vehicule.get_categorie_display(),
                "statut": vehicule.get_statut_display(),
            })
    return points


def accueil(request):
    vehicules = Vehicule.objects.filter(statut="disponible").order_by("prix_jour")[:6]
    context = {
        "vehicules": vehicules,
        "map_data": _build_map_data(vehicules),
    }
    return render(request, "core/accueil.html", context)


def liste_vehicules(request):
    vehicules = Vehicule.objects.filter(statut="disponible")
    categorie = request.GET.get("categorie", "").strip()
    transmission = request.GET.get("transmission", "").strip()
    carburant = request.GET.get("carburant", "").strip()
    ville = request.GET.get("ville", "").strip()
    prix_max = request.GET.get("prix_max", "").strip()

    if categorie:
        vehicules = vehicules.filter(categorie=categorie)
    if transmission:
        vehicules = vehicules.filter(transmission=transmission)
    if carburant:
        vehicules = vehicules.filter(carburant=carburant)
    if ville:
        vehicules = vehicules.filter(ville__icontains=ville)

    if prix_max:
        try:
            prix_max_decimal = Decimal(prix_max)
            vehicules = vehicules.filter(prix_jour__lte=prix_max_decimal)
        except InvalidOperation:
            prix_max = ""

    context = {
        "vehicules": vehicules,
        "map_data": _build_map_data(vehicules),
        "filters": {
            "categorie": categorie,
            "transmission": transmission,
            "carburant": carburant,
            "ville": ville,
            "prix_max": prix_max,
        },
    }
    return render(request, "core/liste_vehicules.html", context)


def reserver_vehicule(request, vehicule_id: int):
    vehicule = get_object_or_404(Vehicule, pk=vehicule_id, statut="disponible")
    form = ReservationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        date_debut = data["date_debut"]
        date_fin = data["date_fin"]

        if date_fin < date_debut:
            form.add_error("date_fin", "La date de fin doit être après la date de début.")
        elif date_debut < date.today():
            form.add_error("date_debut", "La date de début doit être aujourd'hui ou plus tard.")
        else:
            overlap = Reservation.objects.filter(
                vehicule=vehicule,
                date_debut__lte=date_fin,
                date_fin__gte=date_debut,
            ).exclude(statut__iexact="annulee")

            if overlap.exists():
                form.add_error(None, "Ce véhicule est déjà réservé sur ces dates.")
            else:
                client, _ = Client.objects.get_or_create(
                    email=data["email"],
                    defaults={
                        "nom": data["nom"],
                        "prenom": data["prenom"],
                        "telephone": data["telephone"],
                        "adresse": data.get("adresse", ""),
                        "mot_de_passe": "",
                    },
                )
                # Mise à jour éventuelle des infos client
                client.nom = data["nom"]
                client.prenom = data["prenom"]
                client.telephone = data["telephone"]
                client.adresse = data.get("adresse", "")
                client.save()

                nb_jours = (date_fin - date_debut).days + 1
                montant_total = nb_jours * vehicule.prix_jour

                reservation = Reservation.objects.create(
                    client=client,
                    vehicule=vehicule,
                    date_debut=date_debut,
                    date_fin=date_fin,
                    montant_total=montant_total,
                    statut="en attente",
                )

                messages.success(request, "✅ Réservation créée ! Procédez maintenant au paiement.")
                return redirect("paiement", reservation_id=reservation.id)

    context = {
        "vehicule": vehicule,
        "form": form,
    }
    return render(request, "core/reservation_form.html", context)


def paiement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if hasattr(reservation, 'paiement'):
        messages.warning(request, '⚠️ Cette réservation a déjà été payée.')
        return redirect('confirmation_paiement', reservation_id=reservation.id)

    if request.method == 'POST':
        mode_paiement = request.POST.get('mode_paiement')
        time.sleep(2)
        Paiement.objects.create(
            reservation=reservation,
            montant=reservation.montant_total,
            mode_paiement=mode_paiement
        )
        reservation.statut = 'confirmée'
        reservation.save()
        messages.success(request, '✅ Paiement effectué avec succès !')
        return redirect('confirmation_paiement', reservation_id=reservation.id)

    return render(request, 'core/paiement.html', {'reservation': reservation})


def confirmation_paiement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    try:
        paiement = reservation.paiement
    except Paiement.DoesNotExist:
        messages.error(request, '❌ Aucun paiement trouvé.')
        return redirect('paiement', reservation_id=reservation.id)

    return render(request, 'core/confirmation_paiement.html', {
        'reservation': reservation,
        'paiement': paiement
    })


def inscription(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Vérification mots de passe
        if password != password_confirm:
            messages.error(request, '❌ Les mots de passe ne correspondent pas.')
            return render(request, 'core/accueil.html', {
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'telephone': telephone,
                'adresse': adresse,
                'open_modal': True,
                'active_tab': 'register'
            })

        # Vérification complexité
        pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]).{8,}$'
        if not re.match(pattern, password):
            messages.error(request,
                '❌ Le mot de passe doit contenir au moins 8 caractères, '
                'une majuscule, un chiffre et un caractère spécial.')
            return render(request, 'core/accueil.html', {
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'telephone': telephone,
                'adresse': adresse,
                'open_modal': True,
                'active_tab': 'register'
            })

        # Vérification email existant
        if User.objects.filter(username=email).exists():
            messages.error(request, '❌ Cet email est déjà utilisé.')
            return render(request, 'core/accueil.html', {
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'telephone': telephone,
                'adresse': adresse,
                'open_modal': True,
                'active_tab': 'register'
            })

        # Création User et Client
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=prenom,
            last_name=nom
        )
        Client.objects.create(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            adresse=adresse,
        )

        login(request, user)
        messages.success(request, '✅ Inscription réussie ! Bienvenue !')
        return redirect('accueil')

    return redirect('accueil')


def connexion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, f'✅ Bienvenue {user.first_name} !')
            return redirect('accueil')
        else:
            messages.error(request, '❌ Email ou mot de passe incorrect.')
            return redirect('accueil')

    return redirect('accueil')


def deconnexion(request):
    logout(request)
    messages.success(request, '👋 Vous êtes déconnecté.')
    return redirect('accueil')


def agences(request):
    agences = [
        {
            "nom": "AutoDrive Lomé",
            "adresse": "Quartier A, Rue 123, Lomé",
            "telephone": "+228 90 00 00 01",
            "email": "lome@autodrive.com",
            "lat": 6.1319,    # latitude Lomé
            "lng": 1.2228,    # longitude Lomé
            "photo": None
        },
        {
            "nom": "AutoDrive Kara",
            "adresse": "Quartier B, Rue 456, Kara",
            "telephone": "+228 90 00 00 02",
            "email": "kara@autodrive.com",
            "lat": 9.5509,    # latitude Kara
            "lng": 1.1840,    # longitude Kara
            "photo": None
        },
        {
            "nom": "AutoDrive Sokodé",
            "adresse": "Quartier C, Rue 789, Sokodé",
            "telephone": "+228 90 00 00 03",
            "email": "sokode@autodrive.com",
            "lat": 8.9833,
            "lng": 1.1333,
            "photo": None
        },
        # Ajoute d'autres agences ici
    ]
    return render(request, "core/agences.html", {"agences": agences})
