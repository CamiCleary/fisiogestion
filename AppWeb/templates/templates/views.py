from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente, Fisioterapeuta
from .forms import PacienteForm, FisioterapeutaForm

# Asumiendo que tienes un modelo User y quizás Role.
# Si no los tienes, necesitarás crearlos y sus formularios asociados.
from django.contrib.auth.models import User # Ejemplo, si usas el User de Django
# from .models import Consulta, Pago, Role # Descomenta y define estos modelos si los tienes
# from .forms import ConsultaForm, PagoForm, UserForm, RoleForm # Descomenta y define estos formularios

def inicio(request):
    return render(request, 'index.html')

def login_view(request):
    # Aquí deberás implementar tu lógica de inicio de sesión
    return render(request, 'login.html')

# Vistas existentes (ajustadas para reflejar el ámbito de Samuel si es necesario)
def lista_fisioterapeutas(request):
    fisioterapeutas = Fisioterapeuta.objects.all()
    return render(request, 'Lista_fisioterapeutas.html', {'fisioterapeutas': fisioterapeutas})

def crear_fisioterapeuta(request):
    if request.method == 'POST':
        form = FisioterapeutaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_fisioterapeutas')
    else:
        form = FisioterapeutaForm()
    return render(request, 'registro_fisioterapeuta.html', {'form': form})

def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'Lista_clientes.html', {'pacientes': pacientes})

def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'registro_paciente.html', {'form': form})

def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'registro_paciente.html', {'form': form, 'edit': True, 'paciente': paciente})

def eliminar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('lista_pacientes')
    return render(request, 'confirmar_eliminar_paciente.html', {'paciente': paciente})


# Vistas para SAMUEL (Admin)

# Dashboard Admin
def dashboard_admin(request):
    # Aquí podrías cargar datos reales de tus modelos
    # Ejemplo:
    # num_pacientes_activos = Paciente.objects.filter(estado='activo').count()
    # num_fisioterapeutas = Fisioterapeuta.objects.count()
    # consultas_hoy = Consulta.objects.filter(fecha=date.today()).count()
    # ingresos_mes = Pago.objects.filter(fecha__month=date.today().month).aggregate(Sum('monto'))['monto__sum'] or 0

    context = {
        # 'num_pacientes_activos': num_pacientes_activos,
        # 'num_fisioterapeutas': num_fisioterapeutas,
        # 'consultas_hoy': consultas_hoy,
        # 'ingresos_mes': ingresos_mes,
    }
    return render(request, 'dashboard_admin.html', context)

# Gestión de Usuarios y Roles
def gestionar_usuarios(request):
    # users = User.objects.all() # Si usas el modelo User de Django
    # return render(request, 'gestionar_usuarios.html', {'users': users})
    return render(request, 'gestionar_usuarios.html') # Usando el archivo estático por ahora

def editar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk) # Asumiendo un modelo User
    # if request.method == 'POST':
    #     form = UserForm(request.POST, instance=user) # Asumiendo UserForm
    #     if form.is_valid():
    #         form.save()
    #         return redirect('gestionar_usuarios')
    # else:
    #     form = UserForm(instance=user)
    # return render(request, 'editar_usuario.html', {'form': form, 'user': user})
    return render(request, 'editar_usuario.html', {'user': user}) # Placeholder

def gestionar_roles(request):
    # roles = Role.objects.all() # Asumiendo un modelo Role
    # return render(request, 'gestionar_roles.html', {'roles': roles})
    return render(request, 'gestionar_roles.html') # Placeholder

# Detalle de Pacientes (ya existe una similar, renombrada para Admin)
def detalle_paciente_admin(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    # Aquí podrías cargar consultas, pagos, etc., relacionados con el paciente
    return render(request, 'detalle_paciente_fisioterapeuta.html', {'paciente': paciente}) # Reutilizando template

# Detalle de Fisioterapeutas
def detalle_fisioterapeuta(request, pk):
    fisioterapeuta = get_object_or_404(Fisioterapeuta, pk=pk)
    # Aquí podrías cargar consultas, etc., relacionadas con el fisioterapeuta
    return render(request, 'detalle_fisioterapeuta.html', {'fisioterapeuta': fisioterapeuta}) # Necesitas crear detalle_fisioterapeuta.html

# Gestión de Consultas (Admin)
def lista_consultas(request):
    # consultas = Consulta.objects.all() # Asumiendo un modelo Consulta
    # return render(request, 'lista_consultas.html', {'consultas': consultas})
    return render(request, 'lista_consultas.html') # Usando el archivo estático por ahora

def crear_consulta(request):
    # if request.method == 'POST':
    #     form = ConsultaForm(request.POST) # Asumiendo ConsultaForm
    #     if form.is_valid():
    #         form.save()
    #         return redirect('lista_consultas')
    # else:
    #     form = ConsultaForm()
    # return render(request, 'crear_consulta.html', {'form': form})
    return render(request, 'crear_consulta.html') # Placeholder

def editar_consulta(request, pk):
    # consulta = get_object_or_404(Consulta, pk=pk)
    # if request.method == 'POST':
    #     form = ConsultaForm(request.POST, instance=consulta)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('lista_consultas')
    # else:
    #     form = ConsultaForm(instance=consulta)
    # return render(request, 'editar_consulta.html', {'form': form, 'consulta': consulta})
    return render(request, 'editar_consulta.html') # Placeholder

def detalle_consulta(request, pk):
    # consulta = get_object_or_404(Consulta, pk=pk)
    # return render(request, 'detalle_consulta.html', {'consulta': consulta})
    return render(request, 'detalle_consulta.html') # Placeholder

def eliminar_consulta(request, pk):
    # consulta = get_object_or_404(Consulta, pk=pk)
    # if request.method == 'POST':
    #     consulta.delete()
    #     return redirect('lista_consultas')
    # return render(request, 'confirmar_eliminar_consulta.html', {'consulta': consulta})
    return render(request, 'confirmar_eliminar_consulta.html') # Placeholder

# Gestión de Pagos (Admin)
def lista_pagos(request):
    # pagos = Pago.objects.all() # Asumiendo un modelo Pago
    # return render(request, 'lista_pagos.html', {'pagos': pagos})
    return render(request, 'lista_pagos.html') # Usando el archivo estático por ahora

def registrar_pago(request):
    # if request.method == 'POST':
    #     form = PagoForm(request.POST) # Asumiendo PagoForm
    #     if form.is_valid():
    #         form.save()
    #         return redirect('lista_pagos')
    # else:
    #     form = PagoForm()
    # return render(request, 'registrar_pago.html', {'form': form})
    return render(request, 'registrar_pago.html') # Placeholder

def detalle_pago(request, pk):
    # pago = get_object_or_404(Pago, pk=pk)
    # return render(request, 'detalle_pago.html', {'pago': pago})
    return render(request, 'detalle_pago.html') # Placeholder

def eliminar_pago(request, pk):
    # pago = get_object_or_404(Pago, pk=pk)
    # if request.method == 'POST':
    #     pago.delete()
    #     return redirect('lista_pagos')
    # return render(request, 'confirmar_eliminar_pago.html', {'pago': pago})
    return render(request, 'confirmar_eliminar_pago.html') # Placeholder


# Telemedicina Admin
def telemedicina(request):
    # Aquí puedes pasar datos de sesiones de telemedicina
    return render(request, 'telemedicina.html')

# Reportes Admin
def reportes(request):
    # Aquí puedes pasar datos para los reportes y gráficos
    return render(request, 'reportes.html')