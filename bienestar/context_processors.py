from .models import NotaPsicologo

def mensajes_no_leidos(request):
    if request.user.is_authenticated and not request.user.is_staff:
        count = NotaPsicologo.objects.filter(
            alumno=request.user,
            leido=False
        ).count()
        return {'mensajes_no_leidos': count}
    return {'mensajes_no_leidos': 0}