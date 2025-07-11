from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from allauth.socialaccount.providers.google import views as google_views
from allauth.account.views import LoginView, SignupView
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from .views import post_login_redirect, CustomSignupView
from .views import usuarios_logeados_view
from .views import notificaciones_leidas

from . import views

urlpatterns = [
    # Redirección raíz
    path('', lambda request: redirect('login')),

    # --- Autenticación Django y Allauth ---
    path('accounts/google/login/callback/', google_views.oauth2_login, name='google_login'),
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/', include('allauth.urls')),

    # --- Autenticación personalizada ---
    path('admin/login/', LoginView.as_view(template_name='registro/login.html'), name='admin_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='account_login'), name='logout'),
    path('accounts/profile/', post_login_redirect, name='account_profile'),

    # --- Cambio y recuperación de contraseña ---
    path('cambiar-contraseña/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('cambiar-contraseña/hecho/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
    ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    # --- Panel principal y accesibilidad ---
    path('inicio/', views.menuPrincipal, name='menuprin'),
    path('accesibilidad/', views.accesibilidad, name='accesibilidad'),
    path('informacion/', views.Informacion, name='Informacion'),
    path('agregar-comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('comentario/eliminar/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),

    # --- Menú y categorías ---
    path('menu/<str:categoria_slug>/', views.mostrar_categoria, name='mostrar_categoria'),
    path('agregar/', views.agregar_y_ver_platillos, name='agregar_y_ver_platillos'),
    path('almuerzos/editar/<int:almuerzo_id>/', views.editar_almuerzo, name='editar_almuerzo'),
    path('platillos/eliminar/<int:pk>/', views.eliminar_platillo, name='eliminar_platillo'),
    path('almuerzos/', views.listar_almuerzos, name='listar_almuerzos'),
    path('platillos/editar/<int:pk>/', views.editar_platillo, name='editar_platillo'),

    # --- Empleados ---
    path('empleados/', views.ver_empleados, name='ver_empleados'),
    path('empleados/agregar/', views.agregar_empleados, name='agregar_empleado'),
    path('empleados/eliminar/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('empleados/editar/<int:id>/', views.editar_empleado, name='editar_empleado'),

    # --- Reservas ---
    path('realizar-reserva/', views.realizar_reserva, name='realizar_reserva'),
    path('reservas/', views.ver_reservas, name='ver_reservas'),
    path('reservas/lista/', views.lista_reservas, name='lista_reservas'),
    path('reservas/eliminar_pasadas/', views.eliminar_reservas_pasadas, name='eliminar_reservas_pasadas'),
    path('reservas/eliminar-multiples/', views.eliminar_reservas_multiples, name='eliminar_reservas_multiples'),
    path('reserva/<int:reserva_id>/cambiar-estado/', views.cambiar_estado_reserva, name='cambiar_estado_reserva'),

    # --- Perfil de usuario ---
    path('actualizar-email/', views.actualizar_email, name='actualizar_email'),
    path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('usuario/', views.vista_usuario, name='vista_usuario'),
    path('perfil/', views.vista_usuario, name='perfil'),
    path('reservas/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('usuarios-logeados/', usuarios_logeados_view, name='usuarios_logeados'),
    path('notificaciones/leidas/', notificaciones_leidas, name='notificaciones_leidas'),

    # --- Django Admin ---
    path('admin/', admin.site.urls),
]

# --- Archivos estáticos durante desarrollo ---
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
