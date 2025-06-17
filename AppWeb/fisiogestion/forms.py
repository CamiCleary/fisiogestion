from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Usuario

Usuario = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

class PacienteForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'cedula', 'info_adicional']
        widgets = {
            'password': forms.PasswordInput(),
        }

class FisioterapeutaForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'cedula', 'especialidad']
        widgets = {
            'password': forms.PasswordInput(),
        }