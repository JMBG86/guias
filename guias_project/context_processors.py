from guias_app.models import Clinica

def all_clinicas(request):
    return {'clinicas_nav': Clinica.objects.all().order_by('nome')}