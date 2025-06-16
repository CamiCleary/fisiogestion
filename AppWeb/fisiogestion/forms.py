from django import forms
from .models import Usuario


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'cedula', 'telefono', 'email', 'direccion']

class FisioterapeutaForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ingrese nombre'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Ingrese apellido'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+58'}),
            'rol': forms.TextInput(attrs={'placeholder': 'Rol del fisioterapeuta'}),
            'especialidad': forms.TextInput(attrs={'placeholder': 'Ej. Rehabilitación'}),
            'info_adicional': forms.Textarea(attrs={'placeholder': 'Información relevante'}),
        }
