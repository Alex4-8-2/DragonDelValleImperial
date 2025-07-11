# restaurant/context_processors.py
from .models import Notificacion

def notificaciones_context(request):
    if request.user.is_authenticated:
        notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leido=False)
        return {
            'notificaciones_no_leidas': notificaciones_no_leidas,
            'notificaciones_no_leidas_count': min(notificaciones_no_leidas.count(), 99),
        }
    return {
        'notificaciones_no_leidas': [],
        'notificaciones_no_leidas_count': 0,
    }
