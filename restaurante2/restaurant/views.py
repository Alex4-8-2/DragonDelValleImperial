from allauth.account.views import SignupView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from collections import OrderedDict
from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Reserva
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from .forms import RegistroUsuarioForm
from .models import Perfil
from .forms import PerfilForm 
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from .models import Notificacion
from django.views.decorators.csrf import csrf_exempt
from .forms import (
    PerfilForm,
    ReservaEdicionForm,
    EmailUpdateForm,
    EmpleadoForm,
    AlmuerzoForm,
    ReservaForm,
    ComentarioForm
)
from .models import Comentario, Empleado, Almuerzo, Reserva, Platillo, Reseña

def solo_admin(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return func(request, *args, **kwargs)
    return wrapper

@login_required
def menuPrincipal(request):
    reseñas = Reseña.objects.all().order_by('-fecha')
    comentarios = Comentario.objects.all().order_by('-id')

    categorias = [
        ('parrilla', 'bi-fire', 'Parrilla'),
        ('entrada', 'bi-egg-fried', 'Entradas'),
        ('ensalada', 'bi-basket', 'Ensaladas'),
        ('pasta', 'bi-emoji-smile', 'Pastas'),
        ('postre', 'bi-cake2', 'Postres'),
        ('bebida', 'bi-cup-straw', 'Bebidas'),
    ]

    return render(request, "inicio/principal.html", {
        'reseñas': reseñas,
        'comentarios': comentarios,
        'categorias': categorias,
    })


@login_required
def accesibilidad(request):
    return render(request, "accesibilidad/inf.html")

@login_required
def Informacion(request):
    return render(request, "Informacion/info.html")

@login_required
def menu(request):
    return render(request, "menu/men.html")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_comentario(request, comentario_id):
    if request.method == 'POST':
        comentario = get_object_or_404(Comentario, id=comentario_id)
        comentario.delete()
        messages.success(request, "Comentario eliminado exitosamente.")
    else:
        messages.error(request, "Método no permitido.")
    return redirect('menuprin')

# --- MENU ---
@login_required
def mostrar_categoria(request, categoria_slug):
    slug_to_nombre = {
        'parrilla': 'Especialidades a la Parrilla',
        'entrada': 'Entradas y Aperitivos',
        'ensalada': 'Ensaladas',
        'pasta': 'Pastas Artesanales',
        'postre': 'Postres',
        'bebida': 'Bebidas'
    }

    nombre_categoria = slug_to_nombre.get(categoria_slug.lower())
    if not nombre_categoria:
        return render(request, '404.html', status=404)

    platillos = Almuerzo.objects.filter(tipo=categoria_slug.lower())
    return render(request, 'menu/categorias/categoria.html', {
        'platillos': platillos,
        'tipo': categoria_slug.lower(),
    })

@login_required
def agregar_y_ver_platillos(request):
    if request.method == 'POST':
        form = AlmuerzoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('agregar_y_ver_platillos')
    else:
        form = AlmuerzoForm()

    tipos = OrderedDict([
        ('parrilla', 'Parrilla'),
        ('entrada', 'Entrada'),
        ('ensalada', 'Ensalada'),
        ('pasta', 'Pasta'),
        ('postre', 'Postre'),
        ('bebida', 'Bebida'),
    ])

    platillos_por_tipo = {tipo: Almuerzo.objects.filter(tipo=tipo) for tipo in tipos}
    return render(request, 'menu/agregar/agregar_y_ver_platillos.html', {
        'form': form,
        'tipos': tipos,
        'platillos_por_tipo': platillos_por_tipo,
    })

@login_required
def editar_platillo(request, pk):
    platillo = get_object_or_404(Almuerzo, pk=pk)
    if request.method == 'POST':
        form = AlmuerzoForm(request.POST, request.FILES, instance=platillo)
        if form.is_valid():
            form.save()
            return redirect('agregar_y_ver_platillos')
    else:
        form = AlmuerzoForm(instance=platillo)

    return render(request, 'menu/agregar/editar_platillo.html', {
        'form': form,
        'platillo': platillo
    })

@login_required
def eliminar_platillo(request, pk):
    platillo = get_object_or_404(Almuerzo, pk=pk)
    platillo.delete()
    return redirect('agregar_y_ver_platillos')

# --- EMPLEADOS---
@solo_admin
@login_required
def ver_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'empleados/ver_empleados.html', {'empleados': empleados})

@solo_admin
@login_required
def agregar_empleados(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            empleado = form.save(commit=False)  
            pais = request.POST.get('pais')
            if pais:
                empleado.pais = pais
            empleado.save()  
            messages.success(request, 'Empleado agregado exitosamente.')
            form = EmpleadoForm()  
    else:
        form = EmpleadoForm()
    return render(request, 'empleados/agregar_empleado.html', {'form': form})

@login_required
def editar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id=id)

    if request.method == 'POST':
        empleado.nombre = request.POST.get('nombre')
        empleado.carnet = request.POST.get('carnet')
        empleado.telefono = request.POST.get('telefono')
        empleado.direccion = request.POST.get('direccion')
        empleado.puesto = request.POST.get('puesto')
        empleado.pais = request.POST.get('pais')
        empleado.save()
        messages.success(request, 'Empleado editado correctamente.')
        return redirect('ver_empleados')
    return redirect('ver_empleados')

@login_required
def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado correctamente.')
        return redirect('ver_empleados')
    return render(request, 'empleados/confirmar_eliminacion.html', {'empleado': empleado})

# --- ALMUERZOS --- 
@solo_admin
@login_required
def agregar_almuerzo(request):
    if request.method == 'POST':
        form = AlmuerzoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_almuerzos')
    else:
        form = AlmuerzoForm()
    return render(request, 'menu/almuerzo/agregar.html', {'form': form})

@solo_admin
@login_required
def listar_almuerzos(request):
    form = AlmuerzoForm()
    almuerzos = Almuerzo.objects.all()
    return render(request, 'menu/agregar/agregar_y_ver_platillos.html', {
        'almuerzos': almuerzos,
        'form': form,
        'tipo': 'almuerzo',
    })

@solo_admin
@login_required
def editar_almuerzo(request, almuerzo_id):
    almuerzo = get_object_or_404(Almuerzo, id=almuerzo_id)
    
    if request.method == 'POST':
        form = AlmuerzoForm(request.POST, request.FILES, instance=almuerzo)
        if form.is_valid():
            form.save()
            return redirect('listar_almuerzos')
    else:
        form = AlmuerzoForm(instance=almuerzo)
    
    return render(request, 'menu/agregar/agregar_y_ver_platillos.html', {
        'form': form,
        'es_edicion': True, 
        'tipo': 'platillo',
    })

# --- REGISTRO / LOGIN---

@login_required
def login_view(request):
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def post_login_redirect(request):
    if not request.user.has_usable_password():
        return redirect('account_set_password')
    return redirect('menuprin')

class CustomSignupView(SignupView):
    form_class = RegistroUsuarioForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "¡Cuenta creada con éxito!")
        return response

# --- RESERVAS ---
def puede_ver_reservas(user):
    return user.is_superuser or user.has_perm('restaurant.view_reserva')
@login_required
@user_passes_test(puede_ver_reservas)
def ver_reservas(request):
    list(messages.get_messages(request))
    today = timezone.now().date()
    reservas = Reserva.objects.all().order_by('-fecha', '-hora')
    fecha = request.GET.get('fecha', '')
    usuario = request.GET.get('usuario', '')
    if fecha:
        reservas = reservas.filter(fecha=fecha)
    if usuario:
        reservas = reservas.filter(usuario__username__icontains=usuario)
    for reserva in reservas:
        reserva.actualizar_estado()
    paginator = Paginator(reservas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'reservas/ver_reservas.html', {
        'reservas': page_obj,
        'fecha': fecha,
        'usuario': usuario,
        'today': today
    })

@login_required
def cambiar_estado_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        if reserva.estado == 'activa':
            reserva.estado = 'pasiva'  
        else:
            reserva.estado = 'activa'
        reserva.save()
        messages.success(request, f"Estado de la reserva {reserva.id} actualizado a {reserva.estado}.")
    return redirect('ver_reservas')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_reservas_pasadas(request):
    if request.method == 'POST':
        hoy = timezone.localdate()
        reservas_pasadas = Reserva.objects.filter(fecha__lt=hoy, estado='activa')
        for reserva in reservas_pasadas:
            reserva.actualizar_estado()
        eliminadas_dict = Reserva.objects.filter(estado='pasada').delete()
        cantidad_eliminadas = eliminadas_dict[0]
        if cantidad_eliminadas:
            messages.success(request, f"Se eliminaron {cantidad_eliminadas} reservas pasadas.", extra_tags='eliminar_pasadas')
        else:
            messages.info(request, "No hay reservas pasadas para eliminar.", extra_tags='eliminar_pasadas')
    return redirect('ver_reservas')

@login_required
def cambiar_estado_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.actualizar_estado()
    if reserva.estado == 'activa':
        reserva.estado = 'pasada'
    else:
        reserva.estado = 'activa'
    reserva.save()
    return redirect('ver_reservas') 

@login_required
@require_POST
def eliminar_reservas_multiples(request):
    ids = request.POST.get("ids", "")
    id_list = [int(id_str) for id_str in ids.split(",") if id_str.isdigit()]
    reservas_eliminadas = Reserva.objects.filter(id__in=id_list)
    cantidad = reservas_eliminadas.count()
    reservas_eliminadas.delete()
    messages.success(request, f'Se eliminaron {cantidad} reservas seleccionadas.', extra_tags='eliminar_multiples')
    return redirect('ver_reservas')

@login_required
def realizar_reserva(request):
    if request.method == 'POST':
        try:
            personas = int(request.POST.get('personas'))
            grupo = request.POST.get('grupo', 'Ninguna')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            dia_especial = request.POST.get('dia_especial', 'Ninguna')
            metodo_pago = request.POST.get('metodo_pago')
            comentarios = request.POST.get("comentarios", "")

            reserva = Reserva.objects.create(
                usuario=request.user,
                personas=personas,
                grupo=grupo,
                fecha=fecha,
                hora=hora,
                dia_especial=dia_especial,
                metodo_pago=metodo_pago,
                comentarios=comentarios,
            )

            messages.success(request, 'Reserva registrada con éxito.')
            return redirect('realizar_reserva')

        except Exception as e:
            messages.error(request, f'Error al registrar la reserva: {str(e)}')
            return redirect('realizar_reserva')

    horarios = ["13:30", "14:00", "14:30", "15:00", "19:30", "20:00", "20:30", "21:00"]
    return render(request, 'reservas/realizar_reserva.html', {
        'horarios': horarios,
    })

def reservacion_email(user, reservation_data):
    subject = 'Confirmación de Reserva'
    html_message = render_to_string('reservas/confirmacion_reserva.html', {'reservation_data': reservation_data})
    plain_message = strip_tags(html_message)

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Reserva Confirmada: {reservation_data['fecha']} a las {reservation_data['hora']}")
    p.drawString(100, 780, f"Número de personas: {reservation_data['personas']}")
    p.drawString(100, 760, f"Nombre: {reservation_data['nombre']}")
    p.drawString(100, 740, f"Solicitud especial: {reservation_data['solicitud']}")
    p.drawString(100, 720, f"Pago realizado: {reservation_data['metodo_pago']}")
    p.showPage()
    p.save()

    buffer.seek(0)
    attachment = buffer.read()

    email = EmailMessage(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    email.attach_alternative(html_message, "text/html")
    email.attach('comprobante_reserva.pdf', attachment, 'application/pdf')
    email.send()

# --- USUARIO ---

def obtener_usuarios_logeados():
    sesiones = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []
    for sesion in sesiones:
        data = sesion.get_decoded()
        uid = data.get('_auth_user_id')
        if uid:
            uid_list.append(uid)
    return User.objects.filter(id__in=uid_list)

@login_required
def usuarios_logeados_view(request):
    usuarios_logeados = obtener_usuarios_logeados()
    return render(request, 'usuarios/usuarios_logeados.html', {'usuarios_logeados': usuarios_logeados})

@login_required
def vista_usuario(request):
    perfil, creado = Perfil.objects.get_or_create(usuario=request.user)
    user = request.user
    reseñas = Reseña.objects.filter(usuario=user)
    comentarios = Comentario.objects.filter(usuario=user).order_by('-fecha_hora')  

    reserva_activa = Reserva.objects.filter(usuario=user, estado='Activa').first()
    es_editable = False
    form_edicion = None

    if reserva_activa:
        tiempo_restante = reserva_activa.fecha - timezone.now().date()
        es_editable = tiempo_restante.days >= 2
        form_edicion = ReservaEdicionForm(instance=reserva_activa)

        if request.method == 'POST' and 'editar_reserva' in request.POST:
            form_edicion = ReservaEdicionForm(request.POST, instance=reserva_activa)
            if form_edicion.is_valid() and es_editable:
                form_edicion.save()
                return redirect('vista_usuario')

    perfil_form = PerfilForm(instance=perfil, initial={'nombre': user.first_name})
    usuarios_logeados = obtener_usuarios_logeados()
    context = {
        'reseñas': reseñas,
        'comentarios': comentarios,  
        'reserva_activa': reserva_activa,
        'es_editable': es_editable,
        'form_edicion': form_edicion,
        'perfil_form': perfil_form,
        'perfil': perfil,
        'user': user,
        'usuarios_logeados': usuarios_logeados,
    }
    return render(request, 'usuarios/us.html', context)

@login_required
def editar_perfil(request):
    user = request.user
    perfil, creado = Perfil.objects.get_or_create(usuario=user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            user.first_name = form.cleaned_data.get('nombre')
            user.save()
            messages.success(request, 'Perfil actualizado con éxito.')
            return redirect('vista_usuario')
    else:
        initial = {'nombre': user.first_name}
        form = PerfilForm(instance=perfil, initial=initial)

    return render(request, 'usuarios/editar_perfil.html', {'perfil_form': form})

@login_required
def actualizar_email(request):
    if request.method == 'POST':
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Correo actualizado correctamente.')
            return redirect('vista_usuario')
    else:
        form = EmailUpdateForm(instance=request.user)
    return render(request, 'usuarios/actualizar_email.html', {'form': form})

@login_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Cuenta eliminada correctamente.')
        return redirect('inicio')
    return redirect('vista_usuario')

@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    ahora = datetime.now()
    fecha_hora = datetime.combine(reserva.fecha, reserva.hora)
    if fecha_hora - ahora <= timedelta(hours=48):
        messages.error(request, 'No puedes editar reservas con menos de 48 horas de anticipación.')
        return redirect('vista_usuario')

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva actualizada.')
            return redirect('vista_usuario')
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'reservas/editar_reserva.html', {'form': form})

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    ahora = datetime.now()
    fecha_hora = datetime.combine(reserva.fecha, reserva.hora)
    if fecha_hora - ahora <= timedelta(hours=48):
        messages.error(request, 'No puedes cancelar reservas con menos de 48 horas de anticipación.')
    else:
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, 'Reserva cancelada.')
    return redirect('vista_usuario')

@csrf_exempt
def notificaciones_leidas(request):
    if request.method == "POST" and request.user.is_authenticated:
        Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'forbidden'}, status=403)

def mostrar_usuario(request):
    return render(request, 'usuarios/us.html')

def lista_reservas(request):
    reservas = Reserva.objects.all()
    return render(request, 'reservas/ver_reservas.html', {'reservas': reservas})

def principal(request):
    comentarios = Comentario.objects.all()
    form = ComentarioForm()

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menuprin')  

    return render(request, 'inicio/principal.html', {
        'comentarios': comentarios,
        'form': form,
    })

def agregar_comentario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        texto = request.POST.get('texto')
        puntuacion = request.POST.get('puntuacion')
        try:
            puntuacion = int(puntuacion)
            if 1 <= puntuacion <= 5:
                Comentario.objects.create(
                    usuario=request.user if request.user.is_authenticated else None,
                    nombre=nombre,
                    texto=texto,
                    puntuacion=puntuacion
                )
                messages.success(request, "Gracias por tu comentario.")
            else:
                messages.error(request, "La puntuación debe estar entre 1 y 5.")
        except (ValueError, TypeError):
            messages.error(request, "Puntuación no válida.")

    return redirect('menuprin')