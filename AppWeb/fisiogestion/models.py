from django.db import models

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
