from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Almuerzo(models.Model):
    TIPO_CHOICES = [
        ('parrilla', 'Parrilla'),
        ('entrada', 'Entrada'),
        ('ensalada', 'Ensalada'),
        ('pasta', 'Pasta'),
        ('postre', 'Postre'),
        ('bebida', 'Bebida'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagen = models.ImageField(upload_to='platillos/', blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='parrilla')
    

    def __str__(self):
        return self.nombre


class Platillo(models.Model):
    CATEGORIAS = [
        ('parrilla', 'Especialidades a la Parrilla'),
        ('entradas', 'Entradas y Aperitivos'),
        ('ensaladas', 'Ensaladas'),
        ('pastas', 'Pastas Artesanales'),
        ('postres', 'Postres'),
        ('bebidas', 'Bebidas'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    imagen = models.ImageField(upload_to='platillos/', null=True, blank=True)


    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('pasada', 'Pasada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)  
    personas = models.PositiveIntegerField()
    grupo = models.CharField(max_length=100, blank=True, default='Ninguna')
    fecha = models.DateField()
    hora = models.TimeField()
    dia_especial = models.CharField(max_length=100, blank=True, default='Ninguna')
    creado_en = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activa')
    metodo_pago = models.CharField(max_length=100)
    comentarios = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reserva para {self.personas} personas por {self.usuario.username if self.usuario else self.nombre} en {self.fecha} a las {self.hora}"

    def actualizar_estado(self):
        if self.fecha < timezone.localdate() and self.estado != 'pasada':
            self.estado = 'pasada'
            self.save()

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    carnet = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    puesto = models.CharField(max_length=50)
    pais = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} - {self.puesto}"


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    banner = models.ImageField(upload_to='banners/', null=True, blank=True) 
    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    
class Reseña(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.IntegerField()
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.usuario.username} - {self.calificacion}"
    
class Comentario(models.Model):
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    nombre = models.CharField(max_length=100)
    texto = models.TextField()
    puntuacion = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.puntuacion}/10"

    def fecha_formateada(self):
        return self.fecha_hora.strftime('%d/%m/%Y %I:%M %p')
    fecha_formateada.short_description = 'Fecha y hora'

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario.username} - {'Leída' if self.leido else 'No leída'}"
