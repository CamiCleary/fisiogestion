from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import PacienteForm, FisioterapeutaForm, LoginForm, ConsultaForm
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from datetime import datetime
from .models import Usuario, Consulta, Pago, Consulta

Usuario = get_user_model()


def inicio(request):
    return render(request, "index.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido, {user.nombre}!")
                return redirect("dashboard")
            else:
                messages.error(request, "Email o contraseña incorrectos.")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect("login")


@login_required
def dashboard(request):
    # Selección de plantilla según rol
    rol = request.user.rol
    templates = {
        Usuario.ADMIN: "dashboard_administrador.html",
        Usuario.FISIOTERAPEUTA: "dashboard_fisioterapeuta.html",
        Usuario.PACIENTE: "dashboard_paciente.html",
    }
    tpl = templates.get(rol)
    if not tpl:
        messages.error(request, "Rol de usuario no reconocido.")
        return redirect("login")

    # Contexto base
    context = {
        "user": request.user,
    }
    # Añadir datos específicos por rol
    if rol == Usuario.ADMIN:
        from django.db.models import Count

        context.update(
            {
                "total_usuarios": Usuario.objects.count(),
                "total_pacientes": Usuario.objects.filter(rol=Usuario.PACIENTE).count(),
                "total_fisioterapeutas": Usuario.objects.filter(
                    rol=Usuario.FISIOTERAPEUTA
                ).count(),
            }
        )
    elif rol == Usuario.FISIOTERAPEUTA:
        context.update(
            {
                "mis_consultas": request.user.consultas_fisioterapeuta.all(),
                "mi_horario": request.user.horarios_fisioterapeuta.all(),
            }
        )
    elif rol == Usuario.PACIENTE:
        context.update(
            {
                "mis_consultas": request.user.consultas_paciente.all(),
                "mi_historial": request.user.historiales_paciente.all(),
            }
        )

    return render(request, tpl, context)


# --- Vistas de Gestión ---


@login_required
def lista_fisioterapeutas(request):
    # --- LA CORRECCIÓN ESTÁ AQUÍ ---

    # Paso 1: Define el queryset BASE.
    # En lugar de todos los usuarios, partimos solo de los que ya son Fisioterapeutas.
    queryset = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA)

    # Paso 2: Obtén el término de búsqueda de la URL (si existe).
    search_query = request.GET.get("q", "")

    # Paso 3: Si hay un término de búsqueda, aplica el filtro ADICIONAL sobre el queryset base.
    if search_query:
        queryset = queryset.filter(
            Q(nombre__icontains=search_query)
            | Q(apellido__icontains=search_query)
            | Q(email__icontains=search_query)
        )
        # Nota: Asumo que tu modelo Usuario tiene los campos 'nombre', 'apellido' y 'email'.
        #       Ajusta los campos si se llaman diferente.

    # Paso 4: Prepara el contexto para enviar al template.
    context = {
        "fisioterapeutas": queryset,  # Pasamos el queryset final (ya filtrado)
        "search_query": search_query,  # Devolvemos la búsqueda para que el campo no se borre
    }

    return render(request, "lista_fisioterapeutas.html", context)


@login_required
def crear_fisioterapeuta(request):
    if request.method == "POST":
        form = FisioterapeutaForm(request.POST)
        if form.is_valid():
            # El método save() del formulario (si lo has sobrescrito)
            # se encargará de hashear la contraseña.
            form.save()
            messages.success(request, "Fisioterapeuta registrado exitosamente.")
            return redirect("lista_fisioterapeutas")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = FisioterapeutaForm(
            initial={"rol": Usuario.FISIOTERAPEUTA}
        )  # Para que el rol por defecto sea fisioterapeuta
    return render(request, "registro_fisioterapeuta.html", {"form": form})


@login_required
def editar_fisioterapeuta(request, pk):
    fisioterapeuta = get_object_or_404(
        Usuario, pk=pk, rol=Usuario.FISIOTERAPEUTA
    )  # Asegura que sea un fisioterapeuta
    if request.method == "POST":
        form = FisioterapeutaForm(request.POST, instance=fisioterapeuta)
        if form.is_valid():
            form.save()
            messages.success(request, "Fisioterapeuta actualizado exitosamente.")
            return redirect("lista_fisioterapeutas")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = FisioterapeutaForm(instance=fisioterapeuta)
    return render(
        request,
        "registro_fisioterapeuta.html",
        {"form": form, "edit": True, "fisioterapeuta": fisioterapeuta},
    )


@login_required
def eliminar_fisioterapeuta(request, pk):
    fisioterapeuta = get_object_or_404(Usuario, pk=pk, rol=Usuario.FISIOTERAPEUTA)
    if request.method == "POST":
        fisioterapeuta.delete()
        messages.success(request, "Fisioterapeuta eliminado exitosamente.")
        return redirect("lista_fisioterapeutas")
    # GET: muestra plantilla de confirmación
    return render(
        request,
        "confirmar_eliminar_fisioterapeuta.html",
        {"fisioterapeuta": fisioterapeuta},
    )


@login_required
def lista_pacientes(request):
    # 1) Queryset base: solo usuarios con rol Paciente
    queryset = Usuario.objects.filter(rol=Usuario.PACIENTE)

    # 2) Término de búsqueda desde la URL, Ej: /pacientes/?q=María
    search_query = request.GET.get("q", "").strip()

    # 3) Si hay búsqueda, filtramos por nombre, apellido o cédula
    if search_query:
        queryset = queryset.filter(
            Q(nombre__icontains=search_query)
            | Q(apellido__icontains=search_query)
            | Q(cedula__icontains=search_query)
        )

    # 4) Enviamos al template
    context = {
        "pacientes": queryset,
        "search_query": search_query,  # para rellenar el input si quieres
    }
    return render(request, "lista_pacientes.html", context)


@login_required
def crear_paciente(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente registrado exitosamente.")
            return redirect("lista_pacientes")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = PacienteForm()

    return render(request, "registro_paciente.html", {"form": form})


@login_required
def editar_paciente(request, pk):
    paciente = get_object_or_404(
        Usuario, pk=pk, rol=Usuario.PACIENTE
    )  # Asegura que sea un paciente
    if request.method == "POST":
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente actualizado exitosamente.")
            return redirect("lista_pacientes")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = PacienteForm(instance=paciente)
    return render(
        request,
        "registro_paciente.html",
        {"form": form, "edit": True, "paciente": paciente},
    )


@login_required
def eliminar_paciente(request, pk):
    paciente = get_object_or_404(Usuario, pk=pk, rol=Usuario.PACIENTE)
    if request.method == "POST":
        paciente.delete()
        messages.success(request, "Paciente eliminado exitosamente.")
        return redirect("lista_pacientes")
    # GET: muestra plantilla de confirmación
    return render(request, "confirmar_eliminar_paciente.html", {"paciente": paciente})

@login_required
def reportes(request):
    return render(request, "reportes.html")

@login_required
def reporte_pacientes_view(request):
    context = {
        "titulo": "Reporte de Pacientes",
    }
    return render(request, "fisiogestion/pacientes_reporte.html", context)


@login_required
def telemedicina_view(request):
    return render(request, "telemedicina_fisioterapeuta.html")

@login_required
def telemedicina_paciente_view(request):
    return render(request, "telemedicina_paciente.html")


#CITAS FALTA ARREGLAR ESTO
@login_required
def citas_view(request):

    citas = Consulta.objects.all().order_by("fecha_consulta")

    context = {"citas": citas, "page_title": "Mis Citas"}  # Título para la página
    return render(request, "citas.html", context)

@login_required
def reportes(request):
    # Totales generales
    total_pacientes = Usuario.objects.filter(rol=Usuario.PACIENTE).count()
    total_fisioterapeutas = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA).count()

    # Citas del mes actual
    mes_actual = datetime.now().month
    total_citas_mes = Consulta.objects.filter(
        fecha_consulta__month=mes_actual
    ).count()

    # Ingresos totales
    ingresos_totales = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0

    # Citas agrupadas por mes
    datos = Consulta.objects.annotate(
        mes=TruncMonth('fecha_consulta')
    ).values('mes').annotate(c=Count('id')).order_by('mes')

    # Preparar datos para la plantilla: mes corto + porcentaje relativo
    meses_etq = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    citas_mensuales = {}
    max_c = max((d['c'] for d in datos), default=1)
    for d in datos:
        idx = d['mes'].month - 1
        pct = int((d['c'] / max_c) * 100)
        citas_mensuales[meses_etq[idx]] = pct

    context = {
        'total_pacientes': total_pacientes,
        'total_fisioterapeutas': total_fisioterapeutas,
        'total_citas_mes': total_citas_mes,
        'ingresos_totales': ingresos_totales,
        'citas_mensuales': citas_mensuales,
    }
    return render(request, 'reportes.html', context)

@login_required
def calendario_view(request):
    """
    Vista para mostrar un calendario con las citas del fisioterapeuta.
    """
    # Obtener todas las citas del fisioterapeuta logueado
    citas = Consulta.objects.filter(fisioterapeuta=request.user).order_by("fecha_consulta")

    context = {
        "citas": citas,
        "page_title": "Calendario de Citas",
    }
    return render(request, "calendario.html", context)


@login_required
def consultas(request):
    """
    Muestra TODAS las consultas registradas en el sistema
    y rellena el panel lateral con totales.
    """
    # 1) Recuperar TODAS las consultas, sin filtrar por usuario.
    #    Las ordenamos por fecha más reciente primero.
    todas_las_consultas = Consulta.objects.select_related('paciente', 'fisioterapeuta') \
                                          .order_by('-fecha_consulta')

    # 2) Totales para el panel lateral
    total_pacientes = Usuario.objects.filter(rol=Usuario.PACIENTE).count()
    total_consultas = todas_las_consultas.count()

    return render(request, 'consultas.html', {
        'consultas': todas_las_consultas,
        'total_pacientes': total_pacientes,
        'total_consultas': total_consultas,
    })         

@login_required
def crear_consulta(request):
    """
    Vista para crear una nueva consulta
    """
    if request.method == "POST":
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            # Aseguramos que el fisioterapeuta sea el logueado
            consulta.fisioterapeuta = request.user
            consulta.save()
            messages.success(request, f"Consulta #{consulta.id} creada con éxito.")
            return redirect('consultas')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = ConsultaForm()

    return render(request, 'crear_consulta.html', {
        'form': form,
        'titulo': 'Nueva Consulta',
        'consulta': None,
    })

@login_required
def lista_consultas(request):
    """
    Mostrar todas las consultas registradas junto con un panel lateral
    que muestra el total de pacientes y total de consultas.
    """
    # Contar cuantos pacientes existen
    total_pacientes = Usuario.objects.filter(rol=Usuario.PACIENTE).count()

    # Recuperar todas las consultas, ordenadas de más reciente a más antiguo
    consultas = Consulta.objects.select_related('paciente', 'fisioterapeuta') \
                                .order_by('-fecha_consulta')
    total_consultas = consultas.count()

    return render(request, 'consultas.html', {
        'consultas': consultas,
        'total_pacientes': total_pacientes,
        'total_consultas': total_consultas,
    })
    


# views.py

@login_required
def editar_consulta(request, pk):
    """
    Editar una consulta existente (sin restringir por fisioterapeuta).
    """
    # Buscamos la consulta solo por su ID (pk), sin importar el fisioterapeuta.
    consulta = get_object_or_404(Consulta, pk=pk) 
    
    if request.method == "POST":
        form = ConsultaForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()
            messages.success(request, f"Consulta #{consulta.id} actualizada con éxito.")
            return redirect('consultas')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = ConsultaForm(instance=consulta)

    return render(request, 'crear_consulta.html', {
        'form': form,
        'titulo': f'Editar Consulta #{consulta.id}',
        'consulta': consulta,
    })

# views.py

@login_required
def eliminar_consulta(request, pk):
    """
    Eliminar una consulta existente (sin restringir por fisioterapeuta).
    """
    # Buscamos la consulta solo por su ID (pk), sin importar el fisioterapeuta.
    consulta = get_object_or_404(Consulta, pk=pk)

    if request.method == "POST":
        consulta_id = consulta.id # Guardamos el ID para el mensaje
        consulta.delete()
        messages.success(request, f"Consulta #{consulta_id} eliminada.")
        return redirect('consultas')

    # Para la confirmación (método GET)
    return render(request, 'confirmar_eliminar_consulta.html', {
        'consulta': consulta
    })