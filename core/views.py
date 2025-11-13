

# Create your views here.
from django.shortcuts import render
from .models import Vehicule

def accueil(request):
    vehicules = Vehicule.objects.filter(statut='disponible')
    return render(request, 'core/accueil.html', {'vehicules': vehicules})
