from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente
from .forms import PacienteForm
from .models import Fisioterapeuta
from .forms import FisioterapeutaForm

def inicio(request):
    return render(request, 'index.html')

def crear_fisioterapeuta(request):
    if request.method == 'POST':
        form = FisioterapeutaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')  # Puedes cambiar a una lista de fisioterapeutas luego
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
from django.shortcuts import render

def inicio(request):
    return render(request, 'index.html')

from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html')
