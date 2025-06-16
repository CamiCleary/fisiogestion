from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Paciente, Fisioterapeuta
from .forms import PacienteForm, FisioterapeutaForm


def inicio(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Por defecto Django usa 'username'; si tu User.USERNAME_FIELD es 'email', funciona directamente
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email o contraseña incorrectos')
    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # Página principal tras iniciar sesión
    return render(request, 'dashboard.html')


# Vistas protegidas para área administrativa
@login_required
def lista_fisioterapeutas(request):
    fisioterapeutas = Fisioterapeuta.objects.all()
    return render(request, 'Lista_fisioterapeutas.html', {'fisioterapeutas': fisioterapeutas})


@login_required
def crear_fisioterapeuta(request):
    if request.method == 'POST':
        form = FisioterapeutaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_fisioterapeutas')
    else:
        form = FisioterapeutaForm()
    return render(request, 'registro_fisioterapeuta.html', {'form': form})


@login_required
def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'Lista_clientes.html', {'pacientes': pacientes})


@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'registro_paciente.html', {'form': form})


@login_required
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


@login_required
def eliminar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('lista_pacientes')
    return render(request, 'confirmar_eliminar_paciente.html', {'paciente': paciente})
