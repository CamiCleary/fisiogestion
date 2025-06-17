from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import PacienteForm, FisioterapeutaForm, LoginForm

Usuario = get_user_model()

def inicio(request):
    return render(request, 'index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.nombre}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Email o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'user': request.user})


# --- Vistas de Gestión ---

@login_required
def lista_fisioterapeutas(request):
    # Filtra por el rol de Fisioterapeuta si es lo que quieres mostrar en esta lista
    fisioterapeutas = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA)
    return render(request, 'Lista_fisioterapeutas.html', {'fisioterapeutas': fisioterapeutas})


@login_required
def crear_fisioterapeuta(request):
    if request.method == 'POST':
        form = FisioterapeutaForm(request.POST)
        if form.is_valid():
            # El método save() del formulario (si lo has sobrescrito)
            # se encargará de hashear la contraseña.
            form.save()
            messages.success(request, 'Fisioterapeuta registrado exitosamente.')
            return redirect('lista_fisioterapeutas')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = FisioterapeutaForm(initial={'rol': Usuario.FISIOTERAPEUTA}) # Para que el rol por defecto sea fisioterapeuta
    return render(request, 'registro_fisioterapeuta.html', {'form': form})


@login_required
def editar_fisioterapeuta(request, pk):
    fisioterapeuta = get_object_or_404(Usuario, pk=pk, rol=Usuario.FISIOTERAPEUTA) # Asegura que sea un fisioterapeuta
    if request.method == 'POST':
        form = FisioterapeutaForm(request.POST, instance=fisioterapeuta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fisioterapeuta actualizado exitosamente.')
            return redirect('lista_fisioterapeutas')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = FisioterapeutaForm(instance=fisioterapeuta)
    return render(request, 'registro_fisioterapeuta.html', {'form': form, 'edit': True, 'fisioterapeuta': fisioterapeuta})


@login_required
def eliminar_fisioterapeuta(request, pk):
    fisioterapeuta = get_object_or_404(Usuario, pk=pk, rol=Usuario.FISIOTERAPEUTA) # Asegura que sea un fisioterapeuta
    if request.method == 'POST':
        fisioterapeuta.delete()
        messages.success(request, 'Fisioterapeuta eliminado exitosamente.')
        return redirect('lista_fisioterapeutas')
    return render(request, 'confirmar_eliminar_fisioterapeuta.html', {'fisioterapeuta': fisioterapeuta})


@login_required
def lista_pacientes(request):
    # Filtra por el rol de Paciente
    pacientes = Usuario.objects.filter(rol=Usuario.PACIENTE)
    return render(request, 'Lista_clientes.html', {'pacientes': pacientes})


@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente registrado exitosamente.')
            return redirect('lista_pacientes')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = PacienteForm(initial={'rol': Usuario.PACIENTE}) # Para que el rol por defecto sea paciente
    return render(request, 'registro_paciente.html', {'form': form})


@login_required
def editar_paciente(request, pk):
    paciente = get_object_or_404(Usuario, pk=pk, rol=Usuario.PACIENTE) # Asegura que sea un paciente
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado exitosamente.')
            return redirect('lista_pacientes')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'registro_paciente.html', {'form': form, 'edit': True, 'paciente': paciente})


@login_required
def eliminar_paciente(request, pk):
    paciente = get_object_or_404(Usuario, pk=pk, rol=Usuario.PACIENTE) # Asegura que sea un paciente
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado exitosamente.')
        return redirect('lista_pacientes')
    return render(request, 'confirmar_eliminar_paciente.html', {'paciente': paciente})

def reportes(request):
    return render(request, 'reportes.html')

def reporte_pacientes_view(request):
    context = {
        'titulo': 'Reporte de Pacientes',
    }
    return render(request, 'fisiogestion/pacientes_reporte.html', context)



@login_required 
def telemedicina_view(request):
   
    context = {
        'titulo_pagina': 'Telemedicina y Archivos de Paciente',
        'nombre_fisioterapeuta': 'Dr. Juan Pérez', 
        'nombre_paciente': 'María García', 
    
    }
    return render(request, 'telemedicina.html', context)