from datetime import date
from decimal import Decimal, InvalidOperation
import re
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .forms import ReservationForm
from .models import Client, Reservation, Vehicule, Paiement
# views.py
from django.shortcuts import render




@login_required
def dashboard(request):
    # On récupère uniquement les réservations de l'utilisateur connecté
    mes_reservations = Reservation.objects.filter(client=request.user)

    return render(request, 'core/dashboard.html', {
        'reservations': mes_reservations
    })
def contact(request):
    if request.method == 'POST':
        # Ici vous gérerez plus tard l'envoi de l'email
        pass
    return render(request, 'core/contact.html') # vérifiez bien le nom du fichier .html

# ---------------------------
# Helpers
# ---------------------------
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


# ---------------------------
# Pages publiques
# ---------------------------
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


def agences(request):
    agences = [
        {"nom": "AutoDrive Lomé", "adresse": "Quartier A, Rue 123, Lomé", "telephone": "+228 90 00 00 01", "email": "lome@autodrive.com", "lat": 6.1319, "lng": 1.2228, "photo": None},
        {"nom": "AutoDrive Kara", "adresse": "Quartier B, Rue 456, Kara", "telephone": "+228 90 00 00 02", "email": "kara@autodrive.com", "lat": 9.5509, "lng": 1.1840, "photo": None},
        {"nom": "AutoDrive Sokodé", "adresse": "Quartier C, Rue 789, Sokodé", "telephone": "+228 90 00 00 03", "email": "sokode@autodrive.com", "lat": 8.9833, "lng": 1.1333, "photo": None},
    ]
    return render(request, "core/agences.html", {"agences": agences})

# ---------------------------
# Inscription / Connexion
# ---------------------------
def inscription(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, '❌ Les mots de passe ne correspondent pas.')
            return redirect('accueil')

        pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]).{8,}$'
        if not re.match(pattern, password):
            messages.error(request,
                '❌ Le mot de passe doit contenir au moins 8 caractères, une majuscule, un chiffre et un caractère spécial.')
            return redirect('accueil')

        if User.objects.filter(username=email).exists():
            messages.error(request, '❌ Cet email est déjà utilisé.')
            return redirect('accueil')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=prenom,
            last_name=nom
        )
        Client.objects.create(
            user=user,
            telephone=telephone,
            adresse=adresse
        )

        login(request, user)
        messages.success(request, '✅ Inscription réussie ! Bienvenue !')
        return redirect('dashboard')

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
            return redirect('dashboard')
        else:
            messages.error(request, '❌ Email ou mot de passe incorrect.')
            return redirect('accueil')

    return redirect('accueil')


def deconnexion(request):
    logout(request)
    messages.success(request, '👋 Vous êtes déconnecté.')
    return redirect('accueil')


# ---------------------------
# Réservation / Paiement
# ---------------------------
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
                # Client connecté
                if request.user.is_authenticated:
                    client = request.user.client
                else:
                    # Client temporaire
                    client, _ = Client.objects.get_or_create(
                        email=data["email"],
                        defaults={
                            "nom": data["nom"],
                            "prenom": data["prenom"],
                            "telephone": data["telephone"],
                            "adresse": data.get("adresse", ""),
                        },
                    )
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
        time.sleep(2)  # Simule le délai de paiement
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


# ---------------------------
# Tableau de bord client
# ---------------------------
@login_required(login_url='accueil')
def dashboard(request):
    client = request.user.client
    reservations = Reservation.objects.filter(client=client).select_related('vehicule').order_by('-date_debut')

    filtre_statut = request.GET.get('statut', '').strip()
    if filtre_statut:
        reservations = reservations.filter(statut__iexact=filtre_statut)

    stats = {
        'total': reservations.count(),
        'en_attente': reservations.filter(statut='en attente').count(),
        'confirmee': reservations.filter(statut='confirmée').count(),
        'annulee': reservations.filter(statut='annulée').count(),
        'montant_total': reservations.exclude(statut='annulée').aggregate(total=Sum('montant_total'))['total'] or 0,
    }

    for reservation in reservations:
        reservation.duree = (reservation.date_fin - reservation.date_debut).days + 1

    context = {
        'reservations': reservations,
        'stats': stats,
        'filtre_statut': filtre_statut,
    }
    return render(request, 'core/dashboard.html', context)


@login_required(login_url='accueil')
def annuler_reservation(request, reservation_id):
    if request.method == 'POST':
        client = request.user.client
        reservation = get_object_or_404(Reservation, id=reservation_id, client=client)

        if reservation.statut == 'annulée':
            messages.warning(request, '⚠️ Cette réservation est déjà annulée.')
        else:
            reservation.statut = 'annulée'
            reservation.save()
            messages.success(request, '✅ Réservation annulée avec succès.')

    return redirect('dashboard')
