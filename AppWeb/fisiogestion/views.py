from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario
from .forms import PacienteForm, FisioterapeutaForm


def inicio(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresada = request.POST.get('password')

        try:
            # Busca el usuario por email
            user_db = Usuario.objects.get(email=email_ingresado)

            # --- RIESGO DE SEGURIDAD: COMPARACIÓN DE CONTRASEÑAS EN TEXTO PLANO ---
            # Compara la contraseña ingresada con la almacenada directamente
            if user_db.password == password_ingresada:
                # Si las credenciales coinciden, "inicia sesión"
                # Aquí simulamos el login de Django, pero no usando el sistema de auth completo
                # Esto guardará el ID del usuario en la sesión para @login_required

                # Puedes guardar el id del usuario en la sesión
                request.session['user_id'] = user_db.id
                request.session['user_email'] = user_db.email
                request.session['user_rol'] = user_db.rol

                messages.success(request, f'¡Bienvenido, {user_db.nombre}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Email o contraseña incorrectos.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Email o contraseña incorrectos.') # Mensaje genérico por seguridad
        except Exception as e:
            messages.error(request, f'Ocurrió un error: {e}')

    return render(request, 'login.html')


# Modifica el logout para limpiar la sesión que creaste manualmente
# @login_required es del sistema de auth de Django, no funcionará con tu modelo Usuario directamente
def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
        del request.session['user_email']
        del request.session['user_rol']
        messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


# Dashboard y otras vistas protegidas: Necesitarás un decorador personalizado
# para verificar si el usuario está "logueado" con tu sistema de sesión manual.
def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' in request.session:
            # Si hay un user_id en la sesión, el usuario está "logueado"
            # Opcional: Cargar el objeto usuario para pasarlo a la plantilla
            # request.user_obj = Usuario.objects.get(id=request.session['user_id'])
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('login')
    return wrapper

@custom_login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@custom_login_required
def lista_fisioterapeutas(request):
    fisioterapeutas = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA) # Filtra por rol si es necesario
    return render(request, 'Lista_fisioterapeutas.html', {'fisioterapeutas': fisioterapeutas})


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
    paciente = get_object_or_404(Usuario, pk=pk)
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
    paciente = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('lista_pacientes')
    return render(request, 'confirmar_eliminar_paciente.html', {'paciente': paciente})
