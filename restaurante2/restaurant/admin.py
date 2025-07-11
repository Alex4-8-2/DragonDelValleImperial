from django.contrib import admin
from .models import Empleado, Almuerzo, Platillo, Reserva, Comentario

admin.site.register(Empleado)
admin.site.register(Almuerzo)
admin.site.register(Platillo)
admin.site.register(Reserva)

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puntuacion', 'texto', 'fecha_formateada')
    readonly_fields = ('fecha_hora',)