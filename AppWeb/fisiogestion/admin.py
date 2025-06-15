from django.contrib import admin
from .models import Paciente
from .models import Fisioterapeuta

admin.site.register(Paciente)

admin.site.register(Fisioterapeuta)
