from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import PacienteForm, FisioterapeutaForm, LoginForm
from django.db.models import Q

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
    # Selección de plantilla según rol
    rol = request.user.rol
    templates = {
        Usuario.ADMIN: 'dashboard_administrador.html',
        Usuario.FISIOTERAPEUTA: 'dashboard_fisioterapeuta.html',
        Usuario.PACIENTE: 'dashboard_paciente.html',
    }
    tpl = templates.get(rol)
    if not tpl:
        messages.error(request, 'Rol de usuario no reconocido.')
        return redirect('login')

    # Contexto base
    context = {
        'user': request.user,
    }
    # Añadir datos específicos por rol
    if rol == Usuario.ADMIN:
        from django.db.models import Count
        context.update({
            'total_usuarios': Usuario.objects.count(),
            'total_pacientes': Usuario.objects.filter(rol=Usuario.PACIENTE).count(),
            'total_fisioterapeutas': Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA).count(),
        })
    elif rol == Usuario.FISIOTERAPEUTA:
        context.update({
            'mis_consultas': request.user.consultas_fisioterapeuta.all(),
            'mi_horario': request.user.horarios_fisioterapeuta.all(),
        })
    elif rol == Usuario.PACIENTE:
        context.update({
            'mis_consultas': request.user.consultas_paciente.all(),
            'mi_historial': request.user.historiales_paciente.all(),
        })

    return render(request, tpl, context)


# --- Vistas de Gestión ---

@login_required
def lista_fisioterapeutas(request):
    # --- LA CORRECCIÓN ESTÁ AQUÍ ---

    # Paso 1: Define el queryset BASE. 
    # En lugar de todos los usuarios, partimos solo de los que ya son Fisioterapeutas.
    queryset = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA)

    # Paso 2: Obtén el término de búsqueda de la URL (si existe).
    search_query = request.GET.get('q', '')

    # Paso 3: Si hay un término de búsqueda, aplica el filtro ADICIONAL sobre el queryset base.
    if search_query:
        queryset = queryset.filter(
            Q(nombre__icontains=search_query) |
            Q(apellido__icontains=search_query) |
            Q(email__icontains=search_query)
        )
        # Nota: Asumo que tu modelo Usuario tiene los campos 'nombre', 'apellido' y 'email'.
        #       Ajusta los campos si se llaman diferente.

    # Paso 4: Prepara el contexto para enviar al template.
    context = {
        'fisioterapeutas': queryset,  # Pasamos el queryset final (ya filtrado)
        'search_query': search_query, # Devolvemos la búsqueda para que el campo no se borre
    }
    
    return render(request, 'lista_fisioterapeutas.html', context)


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
    fisioterapeuta = get_object_or_404(Usuario, pk=pk, rol=Usuario.FISIOTERAPEUTA)
    if request.method == 'POST':
        fisioterapeuta.delete()
        messages.success(request, 'Fisioterapeuta eliminado exitosamente.')
        return redirect('lista_fisioterapeutas')
    # GET: muestra plantilla de confirmación
    return render(request, 'confirmar_eliminar_fisioterapeuta.html', {
        'fisioterapeuta': fisioterapeuta
    })


@login_required
def lista_pacientes(request):
    # --- LA CORRECCIÓN ESTÁ AQUÍ ---

    # Paso 1: Define el queryset BASE. 
    # En lugar de todos los usuarios, partimos solo de los que ya son Fisioterapeutas.
    queryset = Usuario.objects.filter(rol=Usuario.PACIENTE)

    # Paso 2: Obtén el término de búsqueda de la URL (si existe).
    search_query = request.GET.get('q', '')

    # Paso 3: Si hay un término de búsqueda, aplica el filtro ADICIONAL sobre el queryset base.
    if search_query:
        queryset = queryset.filter(
            Q(nombre__icontains=search_query) |
            Q(apellido__icontains=search_query) |
            Q(email__icontains=search_query)
        )
        # Nota: Asumo que tu modelo Usuario tiene los campos 'nombre', 'apellido' y 'email'.
        #       Ajusta los campos si se llaman diferente.

    # Paso 4: Prepara el contexto para enviar al template.
    context = {
        'fisioterapeutas': queryset,  # Pasamos el queryset final (ya filtrado)
        'search_query': search_query, # Devolvemos la búsqueda para que el campo no se borre
    }
    
    return render(request, 'lista_pacientes.html', context)


@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            # El método save() del formulario (si lo has sobrescrito)
            # se encargará de hashear la contraseña.
            form.save()
            messages.success(request, 'Paciente registrado exitosamente.')
            return redirect('lista_pacientes')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = FisioterapeutaForm(initial={'rol': Usuario.PACIENTE}) # Para que el rol por defecto sea fisioterapeuta
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
    paciente = get_object_or_404(Usuario, pk=pk, rol=Usuario.PACIENTE)
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado exitosamente.')
        return redirect('lista_pacientes')
    # GET: muestra plantilla de confirmación
    return render(request, 'confirmar_eliminar_paciente.html', {
        'paciente': paciente
    })

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