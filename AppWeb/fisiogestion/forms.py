from django import forms
from django.contrib.auth.forms import UserCreationForm # Solo si aún lo usas, si no, puedes quitarlo
from django.contrib.auth import get_user_model
from .models import Usuario, Consulta , Pago, PlanTratamiento, Horario # Asegúrate de que HistorialMedico esté importado si lo usas en PacienteForm
from django.utils import timezone # Importar timezone para comparaciones de fecha y hora

Usuario = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

class FisioterapeutaForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellido', 'email', 'telefono', 
            'cedula', 'direccion', 'rol', 'especialidad', 
            'info_adicional', 'password'
        ]
        widgets = { # Añadir widgets aquí para placeholders y clases
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'juan.perez@fisiogestion.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+58 414-1234567'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'V-12345678'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Av. Principal, Edificio X'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fisioterapia Deportiva'}),
            'info_adicional': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Información adicional del fisioterapeuta'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ponemos el rol como Fisioterapeuta por defecto y lo hacemos de solo lectura
        self.fields['rol'].initial = Usuario.FISIOTERAPEUTA
        self.fields['rol'].widget.attrs['readonly'] = True
        
        # Aseguramos que todos los campos tengan la clase 'form-control' si no tienen un widget específico
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


    def save(self, commit=True):
        user = super().save(commit=False)
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
    
class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['paciente', 'fisioterapeuta', 'fecha_consulta', 'observaciones']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'fisioterapeuta': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Ingrese las observaciones de la consulta...'
            }),
            'fecha_consulta': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'dd/mm/aaaa --:--',
                'type': 'datetime-local'
            }),
        }
        labels = {
            'paciente': 'Paciente',
            'fisioterapeuta': 'Fisioterapeuta',
            'fecha_consulta': 'Fecha y hora de la consulta',
            'observaciones': 'Observaciones' # Asegurarse de tener un label para observaciones
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra los fisioterapeutas y pacientes por su rol
        self.fields['fisioterapeuta'].queryset = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA)
        self.fields['paciente'].queryset = Usuario.objects.filter(rol=Usuario.PACIENTE)
        
    # Calendario de citas
    
class AgendarCitaForm(forms.ModelForm): # Cambiado a forms.ModelForm
    """
    Formulario para agendar una nueva cita.
    Este formulario ahora es un ModelForm para interactuar directamente con el modelo Consulta.
    """
    # Campo para seleccionar el fisioterapeuta
    fisioterapeuta = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA),
        empty_label="--- Selecciona un Fisioterapeuta ---",
        label="Fisioterapeuta",
        widget=forms.Select(attrs={'class': 'form-control rounded-lg px-4 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )

    # Campo para la fecha y hora de la consulta (representa el inicio de la cita)
    fecha_consulta = forms.DateTimeField(
        label="Fecha y Hora de la Cita",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control rounded-lg px-4 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )

    class Meta:
        model = Consulta
        fields = ['fisioterapeuta', 'fecha_consulta']
        # El campo 'paciente' se asignará en la vista ('agendar_cita_api')
        # Otros campos como 'observaciones' podrían ser añadidos si es necesario
        # widgets = {
        #     'fisioterapeuta': forms.Select(attrs={'class': 'form-control'}),
        #     'fecha_consulta': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        # }


    # Método de validación personalizado para el formulario completo
    def clean(self):
        cleaned_data = super().clean()
        fecha_consulta = cleaned_data.get('fecha_consulta') 

        # Validación: Asegurarse de que la fecha y hora de la cita no estén en el pasado
        if fecha_consulta:
            # Comparamos la fecha y hora de la cita con la fecha y hora actual del servidor.
            # Usamos timezone.now() para manejar datetimes con información de zona horaria (aware datetimes).
            if fecha_consulta < timezone.now():
                self.add_error('fecha_consulta', 'No se puede agendar una cita en el pasado.')
        
        # Aquí podrías añadir validaciones adicionales, como:
        # - Verificar la disponibilidad real del fisioterapeuta (requeriría lógica más compleja que interactúe con el modelo Horario).
        # - Verificar solapamientos con otras citas del mismo fisioterapeuta.
        
        return cleaned_data
        
class PagoForm(forms.ModelForm):
    
    # Opciones para el campo 'metodo_pago'
    METODO_PAGO_CHOICES = [
        ('', 'Seleccione un método'),
        ('Transferencia', 'Transferencia'),
        ('Pago Móvil', 'Pago Móvil'),
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta de Débito/Crédito'),
    ]

    # Redefinimos el campo para usar nuestras opciones personalizadas
    metodo_pago = forms.ChoiceField(
        choices=METODO_PAGO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Pago
        # Campos del modelo que se incluirán en el formulario
        fields = ['consulta', 'fecha_pago', 'monto', 'metodo_pago', 'imagen_referencia']
        
        # Widgets para personalizar la apariencia de los campos y que coincida con tu HTML
        widgets = {
            'consulta': forms.Select(attrs={'class': 'form-select'}),
            'fecha_pago': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'monto': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ej: 25.00'}
            ),
            'imagen_referencia': forms.ClearableFileInput(
                attrs={'class': 'form-control', 'accept': 'image/*'}
            ),
        }
        
        # Etiquetas personalizadas para los campos del formulario
        labels = {
            'consulta': 'Consulta Asociada:',
            'fecha_pago': 'Fecha y Hora del Pago:',
            'monto': 'Monto ($):',
            'metodo_pago': 'Método de Pago:',
            'imagen_referencia': 'Comprobante (opcional):'
        }

    def __init__(self, *args, **kwargs):
        """
        Personalizamos el formulario al iniciarse.
        Hacemos que el campo de consulta muestre información útil.
        """
        super().__init__(*args, **kwargs)
        
        # Filtramos para mostrar solo consultas relevantes (puedes ajustar esta lógica)
        self.fields['consulta'].queryset = Consulta.objects.order_by('-fecha_consulta')
        
        # Cambiamos cómo se muestra cada opción en el <select> de consultas
        self.fields['consulta'].label_from_instance = lambda obj: f"{obj.fecha_consulta.strftime('%d/%m/%Y')} - {obj.paciente}"

class PlanTratamientoForm(forms.ModelForm):
    class Meta:
        model = PlanTratamiento
        fields = ['video_ejercicios', 'documentos_adjuntos', 'instrucciones']
        labels = {
            'video_ejercicios': 'Seleccionar Foto o Video',
            'documentos_adjuntos': 'Adjuntar Documentos (PDF, DOCX...)',
            'instrucciones': 'Descripción del contenido',
        }
        widgets = {
            'video_ejercicios': forms.ClearableFileInput(attrs={
                'accept': 'image/*,video/*',
                'class': 'form-control'
            }),
            'documentos_adjuntos': forms.ClearableFileInput(attrs={
                'accept': '.pdf,.docx',
                'class': 'form-control'
            }),
            'instrucciones': forms.Textarea(attrs={
                'placeholder': 'Describe el progreso o la condición...',
                'rows': 3,
                'class': 'form-control'
            }),
        }
        

class HorarioForm(forms.ModelForm):
    DIAS_SEMANA = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]

    # Sobrescribimos el campo para usar un ChoiceField
    dia_semana = forms.ChoiceField(choices=DIAS_SEMANA, widget=forms.Select(attrs={'class': 'form-control'}))
    
    # Aseguramos que el queryset para fisioterapeuta esté filtrado
    fisioterapeuta = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Horario
        fields = ['fisioterapeuta', 'dia_semana', 'hora_inicio', 'hora_fin']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        return cleaned_data