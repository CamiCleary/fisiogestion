from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Usuario , Consulta

Usuario = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

class FisioterapeutaForm(forms.ModelForm):
    # Hacemos que el campo de contraseña sea requerido y use el widget de contraseña
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    class Meta:
        model = Usuario
        # Define los campos que quieres en el formulario
        fields = [
            'nombre', 'apellido', 'email', 'telefono', 
            'cedula', 'direccion', 'rol', 'especialidad', 
            'info_adicional', 'password'
        ]

    def __init__(self, *args, **kwargs):
        """
        Sobrescribimos el __init__ para añadir clases de Bootstrap a todos los campos
        y hacer que el campo 'rol' sea de solo lectura si ya tiene un valor inicial.
        """
        super().__init__(*args, **kwargs)
        # Ponemos el rol como Fisioterapeuta por defecto y lo hacemos de solo lectura
        self.fields['rol'].initial = Usuario.FISIOTERAPEUTA
        self.fields['rol'].widget.attrs['readonly'] = True
        
        # Asignamos la clase 'form-control' de Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # Añadimos placeholders genéricos
            if field_name == "password":
                field.widget.attrs['placeholder'] = 'Contraseña segura'
            else:
                 field.widget.attrs['placeholder'] = field.label or field_name.capitalize()


    def save(self, commit=True):
        """
        Sobrescribimos el método save para hashear la contraseña. ¡ESTO ES CRUCIAL!
        """
        # Obtenemos la instancia del usuario, pero aún no la guardamos en la BD
        user = super().save(commit=False)
        
        # Obtenemos la contraseña del formulario y la establecemos de forma segura
        password = self.cleaned_data["password"]
        user.set_password(password) # set_password se encarga del hasheo
        
        if commit:
            user.save()
        return user
    
class PacienteForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña segura',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellido', 'email', 'telefono',
            'cedula', 'direccion', 'info_adicional', 'password'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'María'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'González'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+58 414-1234567'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'V-12345678'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Av. Bolívar, casa 12'}),
            'info_adicional': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Alergias, condiciones previas',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asignar rol en el form pero oculto al usuario
        self.fields['rol'] = forms.CharField(
            initial=Usuario.PACIENTE,
            widget=forms.HiddenInput()
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    # Hacemos que el campo de contraseña sea requerido y use el widget de contraseña
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    class Meta:
        model = Usuario
        # Define los campos que quieres en el formulario
        fields = [
            'nombre', 'apellido', 'email', 'telefono', 
            'cedula', 'direccion', 'rol',
            'info_adicional', 'password'
        ]

    def __init__(self, *args, **kwargs):
        """
        Sobrescribimos el __init__ para añadir clases de Bootstrap a todos los campos
        y hacer que el campo 'rol' sea de solo lectura si ya tiene un valor inicial.
        """
        super().__init__(*args, **kwargs)
        # Ponemos el rol como Fisioterapeuta por defecto y lo hacemos de solo lectura
        self.fields['rol'].initial = Usuario.PACIENTE
        self.fields['rol'].widget.attrs['readonly'] = True
        
        # Asignamos la clase 'form-control' de Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # Añadimos placeholders genéricos
            if field_name == "password":
                field.widget.attrs['placeholder'] = 'Contraseña segura'
            else:
                 field.widget.attrs['placeholder'] = field.label or field_name.capitalize()


    def save(self, commit=True):
        """
        Sobrescribimos el método save para hashear la contraseña. ¡ESTO ES CRUCIAL!
        """
        # Obtenemos la instancia del usuario, pero aún no la guardamos en la BD
        user = super().save(commit=False)
        
        # Obtenemos la contraseña del formulario y la establecemos de forma segura
        password = self.cleaned_data["password"]
        user.set_password(password) # set_password se encarga del hasheo
        
        if commit:
            user.save()
        return user
    
class ConsultaForm(forms.ModelForm):
    fecha_consulta = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Consulta
        fields = ['paciente', 'fisioterapeuta', 'fecha_consulta']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'fisioterapeuta': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'paciente': 'Paciente',
            'fisioterapeuta': 'Fisioterapeuta',
            'fecha_consulta': 'Fecha y hora de la consulta',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: si quieres limitar fisioterapeutas a los activos
        self.fields['fisioterapeuta'].queryset = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA)
        self.fields['paciente'].queryset = Usuario.objects.filter(rol=Usuario.PACIENTE)