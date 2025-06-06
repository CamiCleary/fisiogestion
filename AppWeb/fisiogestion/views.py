from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente
from .forms import PacienteForm

def inicio(request):
    return render(request, 'index.html')

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
    return render(request, 'Registro paciente.html', {'form': form})

def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'Registro paciente.html', {'form': form, 'edit': True, 'paciente': paciente})

def eliminar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('lista_pacientes')
    return render(request, 'confirmar_eliminar_paciente.html', {'paciente': paciente})
