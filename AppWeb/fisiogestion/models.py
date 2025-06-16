from django.db import models

class Administrador(models.Model):
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128)  # Almacenar contraseña de forma segura

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Fisioterapeuta(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    contraseña = models.CharField(max_length=128)  # Almacenar contraseña de forma segura
    telefono = models.CharField(max_length=20)
    rol = models.CharField(max_length=50)
    especialidad = models.CharField(max_length=100)
    info_adicional = models.TextField(blank=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
class Horario(models.Model):
    fisioterapeuta = models.ForeignKey(Fisioterapeuta, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(max_length=20)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.fisioterapeuta} - {self.dia_semana} {self.hora_inicio}-{self.hora_fin}"


class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    fisioterapeuta = models.ForeignKey(Fisioterapeuta, on_delete=models.CASCADE, related_name='consultas')
    fecha_consulta = models.DateTimeField()

    def __str__(self):
        return f"Consulta {self.id} - {self.paciente} con {self.fisioterapeuta} el {self.fecha_consulta}"


class HistorialMedico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historiales')
    detalle = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Historial {self.id} - {self.paciente} ({self.fecha_creacion:%Y-%m-%d})"


class Diagnostico(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='diagnosticos')
    descripcion = models.TextField()
    fecha_diagnostico = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnóstico {self.id} - Consulta {self.consulta.id}"


class Pago(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)

    def __str__(self):
        return f"Pago {self.id} - {self.consulta} (${self.monto})"


class Facturacion(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='facturas')
    fecha_factura = models.DateTimeField(auto_now_add=True)
    detalle = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Factura {self.id} - Pago {self.pago.id}"


class InformeTratamiento(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='informes_tratamiento')
    detalle_tratamiento = models.TextField()
    fecha_informe = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Informe {self.id} - Consulta {self.consulta.id}"


class Teleconsulta(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='teleconsultas')
    plataforma = models.CharField(max_length=50)
    enlace_sesion = models.URLField(max_length=255)
    duracion = models.DurationField(blank=True, null=True)
    fecha_hora = models.DateTimeField()

    def __str__(self):
        return f"Teleconsulta {self.id} - {self.consulta} en {self.plataforma}"


class PlanTratamiento(models.Model):
    teleconsulta = models.ForeignKey(Teleconsulta, on_delete=models.CASCADE, related_name='planes')
    video_ejercicios = models.FileField(upload_to='videos/', blank=True, null=True)
    documentos_adjuntos = models.FileField(upload_to='docs/', blank=True, null=True)
    instrucciones = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan {self.id} - Teleconsulta {self.teleconsulta.id}"


class Comunicacion(models.Model):
    TIPO_CHOICES = [
        ('Mensaje', 'Mensaje'),
        ('Archivo', 'Archivo'),
        ('Video', 'Video'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='comunicaciones')
    fisioterapeuta = models.ForeignKey(Fisioterapeuta, on_delete=models.CASCADE, related_name='comunicaciones')
    contenido = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=8, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.tipo} {self.id} - {self.paciente} ↔ {self.fisioterapeuta}"


class InformeMensual(models.Model):
    mes = models.DateField(help_text="Primer día del mes, e.g. 2024-05-01")
    total_pacientes = models.IntegerField()
    total_sesiones = models.IntegerField()
    ingresos_totales = models.DecimalField(max_digits=12, decimal_places=2)
    detalle_estadisticas = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('mes',)

    def __str__(self):
        return f"Informe Mensual {self.mes:%Y-%m}"


class DocumentoInforme(models.Model):
    TIPO_DOC_CHOICES = [
        ('PDF', 'PDF'),
        ('Grafico', 'Gráfico'),
    ]

    informe_mensual = models.ForeignKey(InformeMensual, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=7, choices=TIPO_DOC_CHOICES)
    archivo = models.FileField(upload_to='informes/')
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Documento {self.id} - Informe {self.informe_mensual.mes:%Y-%m} ({self.tipo})"
