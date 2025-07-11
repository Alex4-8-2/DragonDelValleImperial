from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Almuerzo, Empleado, Reserva, Perfil
from .models import Comentario
from allauth.account.forms import SignupForm

# --- Formularios Platillos / Almuerzos ---
class AlmuerzoForm(forms.ModelForm):
    class Meta:
        model = Almuerzo
        fields = ['nombre', 'tipo', 'precio', 'descripcion', 'imagen', ]
        widgets = {
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ej: 19.99'
            }),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'informacion': forms.Textarea(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }

# Subformularios por tipo (reutilizan AlmuerzoForm)
class ParrillaForm(AlmuerzoForm): pass
class EntradaForm(AlmuerzoForm): pass
class EnsaladaForm(AlmuerzoForm): pass
class PastaForm(AlmuerzoForm): pass
class PostreForm(AlmuerzoForm): pass
class BebidaForm(AlmuerzoForm): pass

# --- Formulario para Empleados ---
class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'carnet', 'telefono', 'direccion', 'puesto', 'identificacion', 'pais']

# --- Formularios para Usuarios ---
class RegistroUsuarioForm(UserCreationForm, SignupForm):  # ← Hereda ambos
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(max_length=30, label="Nombre", required=False)
    last_name = forms.CharField(max_length=30, label="Apellido", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo electrónico ya está registrado.")
        return email

    def signup(self, request, user):
        """Método requerido por allauth"""
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.save()
        return user

class EmailUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nuevo correo electrónico'
            }),
        }

class PerfilForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Nombre completo',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_nombre',
            'placeholder': 'Nombre completo'
        })
    )

    class Meta:
        model = Perfil
        fields = ['telefono', 'direccion', 'foto', 'banner']
        labels = {
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'foto': 'Foto de perfil',
            'banner': 'Banner de perfil',
        }
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_telefono',
                'placeholder': 'Teléfono'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'id': 'id_direccion',
                'placeholder': 'Dirección o ubicación...'
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'id': 'id_foto',
            }),
            'banner': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'id': 'id_banner',
            }),
        }
        
# --- Formulario para Reservas ---
class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['personas', 'grupo', 'fecha', 'hora', 'dia_especial', 'metodo_pago']


class ReservaEdicionForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha', 'hora', 'personas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'personas': forms.NumberInput(attrs={'min': 1}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['nombre', 'texto', 'puntuacion']
        widgets = {
            'puntuacion': forms.NumberInput(attrs={'min': 1, 'max': 10})
        }