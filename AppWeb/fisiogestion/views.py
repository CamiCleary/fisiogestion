from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.contrib.auth import get_user_model
from .forms import PacienteForm, FisioterapeutaForm, LoginForm, ConsultaForm , PagoForm
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from django.http import JsonResponse
import json
from django.utils import timezone # Importar timezone para manejar fechas con zonas horarias


# Importar los modelos y formularios de tu app
from .models import Usuario, Consulta, Pago, Horario # Asegúrate de importar Horario si lo usas
from .forms import PacienteForm, FisioterapeutaForm, LoginForm, ConsultaForm, AgendarCitaForm

Usuario = get_user_model() # Obtener el modelo de usuario personalizado

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

    context = {
        "user": request.user,
    }

    if rol == Usuario.ADMIN:
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
        # Citas programadas para hoy para el fisioterapeuta logueado
        today = timezone.localdate()
        citas_hoy = Consulta.objects.filter(
            fisioterapeuta=request.user, 
            fecha_consulta__date=today
        ).order_by('fecha_consulta')
        
        context.update(
            {
                "mis_consultas": request.user.consultas_fisioterapeuta.all(),
                "mi_horario": request.user.horarios_fisioterapeuta.all(), # Asegúrate que tu modelo Horario existe y está relacionado
                "citas_hoy": citas_hoy, # Para mostrar en el dashboard del fisio
            }
        )
    elif rol == Usuario.PACIENTE:
        # Citas programadas para hoy para el paciente logueado
        today = timezone.localdate()
        citas_hoy = Consulta.objects.filter(
            paciente=request.user, 
            fecha_consulta__date=today
        ).order_by('fecha_consulta')

        context.update(
            {
                "mis_consultas": request.user.consultas_paciente.all(),
                "mi_historial": request.user.historiales_paciente.all(), # Asegúrate que tu modelo HistorialMedico existe y está relacionado
                "citas_hoy": citas_hoy, # Para mostrar en el dashboard del paciente
            }
        )

    return render(request, tpl, context)

# --- Vistas de Gestión ---

@login_required
def lista_fisioterapeutas(request):
    queryset = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA)
    search_query = request.GET.get("q", "")

    if search_query:
        queryset = queryset.filter(
            Q(nombre__icontains=search_query)
            | Q(apellido__icontains=search_query)
            | Q(email__icontains=search_query)
        )
    context = {
        "fisioterapeutas": queryset,
        "search_query": search_query,
    }
    return render(request, "lista_fisioterapeutas.html", context)

@login_required
def crear_fisioterapeuta(request):
    if request.method == "POST":
        form = FisioterapeutaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fisioterapeuta registrado exitosamente.")
            return redirect("lista_fisioterapeutas")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = FisioterapeutaForm(
            initial={"rol": Usuario.FISIOTERAPEUTA}
        )
    return render(request, "registro_fisioterapeuta.html", {"form": form})

@login_required
def editar_fisioterapeuta(request, pk):
    fisioterapeuta = get_object_or_404(
        Usuario, pk=pk, rol=Usuario.FISIOTERAPEUTA
    )
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
    return render(
        request,
        "confirmar_eliminar_fisioterapeuta.html",
        {"fisioterapeuta": fisioterapeuta},
    )

@login_required
def lista_pacientes(request):
    queryset = Usuario.objects.filter(rol=Usuario.PACIENTE)
    search_query = request.GET.get("q", "").strip()

    if search_query:
        queryset = queryset.filter(
            Q(nombre__icontains=search_query)
            | Q(apellido__icontains=search_query)
            | Q(cedula__icontains=search_query)
        )
    context = {
        "pacientes": queryset,
        "search_query": search_query,
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
    )
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
    return render(request, "confirmar_eliminar_paciente.html", {"paciente": paciente})

@login_required
def reportes(request):
    return render(request, "reportes.html")

@login_required
def reporte_paciente_view(request):
    context = {
        "titulo": "Reporte de Pacientes",
    }
    return render(request, "reporte_paciente.html", context)


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
    # Calcular max_c de forma segura para evitar divisiones por cero si no hay datos
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

@login_required
def citas_view(request):
    # Esta vista podría ser para una tabla de todas las citas, no el calendario interactivo.
    # El calendario se maneja en calendario_view.
    citas = Consulta.objects.all().order_by("fecha_consulta") # Puedes filtrar por usuario logueado si es necesario
    context = {"citas": citas, "page_title": "Lista de Citas"}
    return render(request, "citas.html", context)

@login_required
def calendario_view(request):
    """
    Vista principal para mostrar el calendario interactivo.
    Solo maneja la solicitud GET para renderizar la página y pasar el formulario.
    Las acciones POST de agendar cita se manejan en agendar_cita_api.
    """
    form = AgendarCitaForm() # Siempre inicializa un formulario vacío para el GET

    # La lógica para obtener y formatear los eventos para FullCalendar
    # se ha movido principalmente a get_monthly_events_api para peticiones AJAX.
    # Sin embargo, pasamos un set inicial por si el calendario lo necesita al cargar.
    
    # Obtener todas las citas existentes para mostrar en el calendario (solo al cargar la página)
    if hasattr(request.user, 'rol') and request.user.rol == Usuario.PACIENTE:
        citas_existentes = Consulta.objects.filter(paciente=request.user).order_by('fecha_consulta')
    elif hasattr(request.user, 'rol') and request.user.rol == Usuario.FISIOTERAPEUTA:
        citas_existentes = Consulta.objects.filter(fisioterapeuta=request.user).order_by('fecha_consulta')
    else: # Para otros roles o admins, mostrar todas las citas
        citas_existentes = Consulta.objects.all().order_by('fecha_consulta')

    eventos = []
    for cita in citas_existentes:
        paciente_nombre_completo = f"{cita.paciente.nombre} {cita.paciente.apellido}" if hasattr(cita.paciente, 'nombre') and hasattr(cita.paciente, 'apellido') else cita.paciente.email # Usar email si nombre/apellido no existen
        fisioterapeuta_nombre_completo = f"{cita.fisioterapeuta.nombre} {cita.fisioterapeuta.apellido}" if hasattr(cita.fisioterapeuta, 'nombre') and hasattr(cita.fisioterapeuta, 'apellido') else cita.fisioterapeuta.email # Usar email si nombre/apellido no existen
        
        eventos.append({
            'title': f"Cita {paciente_nombre_completo} ({fisioterapeuta_nombre_completo})", # Título del evento
            'start': cita.fecha_consulta.isoformat(),
            'id': cita.id,
            'fisioterapeuta_nombre': fisioterapeuta_nombre_completo,
            'paciente_nombre': paciente_nombre_completo,
            'hora_inicio': cita.fecha_consulta.strftime('%H:%M'),
        })
    
    context = {
        'form': form, # Pasa la instancia del formulario al contexto
        'eventos_json': json.dumps(eventos), # Los eventos iniciales para el calendario JavaScript
        'page_title': 'Mi Calendario',
    }
    return render(request, 'fisiogestion/calendario.html', context)


@login_required
def get_monthly_events_api(request):
    """
    API para obtener eventos del calendario para un rango de fechas (usado por FullCalendar).
    FullCalendar enviará 'start' y 'end' como parámetros GET.
    """
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    if not start_str or not end_str:
        return JsonResponse({'error': 'Fechas de inicio y fin son requeridas'}, status=400)

    try:
        # Convertir strings a objetos datetime. FullCalendar envía en formato ISO 8601.
        start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')) # Manejar 'Z' de UTC
        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido. Use ISO 8601'}, status=400)

    # Filtrar citas dentro del rango de fechas y por el rol del usuario
    if hasattr(request.user, 'rol') and request.user.rol == Usuario.PACIENTE:
        citas = Consulta.objects.filter(
            paciente=request.user,
            fecha_consulta__range=[start_date, end_date]
        ).order_by('fecha_consulta')
    elif hasattr(request.user, 'rol') and request.user.rol == Usuario.FISIOTERAPEUTA:
        citas = Consulta.objects.filter(
            fisioterapeuta=request.user,
            fecha_consulta__range=[start_date, end_date]
        ).order_by('fecha_consulta')
    else: # Admin o otros roles pueden ver todas las citas en el rango
        citas = Consulta.objects.filter(
            fecha_consulta__range=[start_date, end_date]
        ).order_by('fecha_consulta')

    eventos = []
    for cita in citas:
        paciente_nombre_completo = f"{cita.paciente.nombre} {cita.paciente.apellido}" if hasattr(cita.paciente, 'nombre') and hasattr(cita.paciente, 'apellido') else cita.paciente.email
        fisioterapeuta_nombre_completo = f"{cita.fisioterapeuta.nombre} {cita.fisioterapeuta.apellido}" if hasattr(cita.fisioterapeuta, 'nombre') and hasattr(cita.fisioterapeuta, 'apellido') else cita.fisioterapeuta.email
        
        eventos.append({
            'title': f"Cita {paciente_nombre_completo} ({fisioterapeuta_nombre_completo})",
            'start': cita.fecha_consulta.isoformat(),
            'id': cita.id,
            'fisioterapeuta_nombre': fisioterapeuta_nombre_completo,
            'paciente_nombre': paciente_nombre_completo,
            'hora_inicio': cita.fecha_consulta.strftime('%H:%M'),
        })
    return JsonResponse(eventos, safe=False)


@login_required
def agendar_cita_api(request):
    """
    API para agendar una nueva cita via POST (usado por el formulario del calendario).
    Devuelve una respuesta JSON.
    """
    if request.method == 'POST':
        form = AgendarCitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            
            # Asigna el paciente logueado a la cita
            # Es crucial que el usuario logueado sea un paciente para agendar
            if hasattr(request.user, 'rol') and request.user.rol == Usuario.PACIENTE:
                cita.paciente = request.user
                try:
                    cita.save()
                    return JsonResponse({'success': True, 'message': 'Cita agendada exitosamente.'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al guardar la cita: {e}'}, status=500)
            else:
                return JsonResponse({'success': False, 'message': 'Acceso denegado. Solo los pacientes pueden agendar citas.'}, status=403)
        else:
            # Si el formulario no es válido, devuelve los errores
            errors = form.errors.as_json() # Opcional: form.errors.as_ul() para HTML
            return JsonResponse({'success': False, 'message': 'Errores de validación.', 'errors': json.loads(errors)}, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


@login_required
def get_daily_appointments_api(request):
    selected_date_str = request.GET.get('date')
    if not selected_date_str:
        return JsonResponse({'error': 'No se proporcionó la fecha'}, status=400)

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=400)

    if hasattr(request.user, 'rol') and request.user.rol == Usuario.PACIENTE:
        citas_del_dia = Consulta.objects.filter(
            paciente=request.user,
            fecha_consulta__date=selected_date
        ).order_by('fecha_consulta__time')
    elif hasattr(request.user, 'rol') and request.user.rol == Usuario.FISIOTERAPEUTA:
        citas_del_dia = Consulta.objects.filter(
            fisioterapeuta=request.user,
            fecha_consulta__date=selected_date
        ).order_by('fecha_consulta__time')
    else:
        citas_del_dia = Consulta.objects.filter(
            fecha_consulta__date=selected_date
        ).order_by('fecha_consulta__time')

    data = []
    for cita in citas_del_dia:
        paciente_nombre_completo = f"{cita.paciente.nombre} {cita.paciente.apellido}" if hasattr(cita.paciente, 'nombre') and hasattr(cita.paciente, 'apellido') else cita.paciente.email
        fisioterapeuta_nombre_completo = f"{cita.fisioterapeuta.nombre} {cita.fisioterapeuta.apellido}" if hasattr(cita.fisioterapeuta, 'nombre') and hasattr(cita.fisioterapeuta, 'apellido') else cita.fisioterapeuta.email

        data.append({
            'id': cita.id,
            'paciente_nombre': paciente_nombre_completo,
            'fisioterapeuta_nombre': fisioterapeuta_nombre_completo,
            'fecha_hora': cita.fecha_consulta.strftime('%H:%M'),
            'fecha_completa': cita.fecha_consulta.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse(data, safe=False)

# --- Vistas de Consultas ---

@login_required
def consultas(request):
    todas_las_consultas = Consulta.objects.select_related('paciente', 'fisioterapeuta') \
                                         .order_by('-fecha_consulta')
    total_pacientes = Usuario.objects.filter(rol=Usuario.PACIENTE).count()
    total_consultas = todas_las_consultas.count()

    return render(request, 'consultas.html', {
        'consultas': todas_las_consultas,
        'total_pacientes': total_pacientes,
        'total_consultas': total_consultas,
    })

@login_required
def crear_consulta(request):
    if request.method == "POST":
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
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
    total_pacientes = Usuario.objects.filter(rol=Usuario.PACIENTE).count()
    consultas = Consulta.objects.select_related('paciente', 'fisioterapeuta') \
                                .order_by('-fecha_consulta')
    total_consultas = consultas.count()

    return render(request, 'consultas.html', {
        'consultas': consultas,
        'total_pacientes': total_pacientes,
        'total_consultas': total_consultas,
    })
    
@login_required
def editar_consulta(request, pk):
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

@login_required
def eliminar_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)

    if request.method == "POST":
        consulta_id = consulta.id 
        consulta.delete()
        messages.success(request, f"Consulta #{consulta_id} eliminada.")
        return redirect('consultas')

    return render(request, 'confirmar_eliminar_consulta.html', {
        'consulta': consulta
    })

@login_required
def pagos_fisioterapeuta(request):
    # Trae todos los pagos de las consultas donde el fisioterapeuta logueado es el responsable
    pagos = (Pago.objects
             .filter(consulta__fisioterapeuta=request.user)
             .select_related('consulta__paciente', 'consulta__fisioterapeuta'))

    return render(request, 'pagos_fisioterapeuta.html', {
        'pagos': pagos
    })

@login_required
def pagos_paciente(request):
    # Traemos todos los pagos asociados a las consultas de este paciente
    pagos = Pago.objects.filter(
        consulta__paciente=request.user
    ).select_related('consulta__fisioterapeuta')

    return render(request, 'pagos_paciente.html', {
        'pagos': pagos
    })

@login_required
def pagos_administrador(request):
    # Solo administradores
    if request.user.rol != Usuario.ADMIN:
        messages.error(request, "No tienes permiso para ver esta página.")
        return redirect('dashboard')

    # Traigo todos los pagos con sus consultas, pacientes, fisioterapeutas y facturas
    pagos = (Pago.objects
             .select_related('consulta__paciente', 'consulta__fisioterapeuta')
             .prefetch_related('facturas')
             .order_by('-fecha_pago'))

    return render(request, 'pagos_administrador.html', {
        'pagos': pagos
    })

@login_required
def telemedicina_view(request):
    return render(request, "telemedicina_fisioterapeuta.html")

@login_required
def telemedicina_paciente_view(request):
    return render(request, "telemedicina_paciente.html")

@login_required
def agregar_pagos(request):
    """
    Gestiona la creación de un nuevo pago.
    - Si la petición es GET, muestra el formulario vacío.
    - Si la petición es POST, procesa los datos y guarda el pago.
    """
    if request.method == 'POST':
        # Creamos una instancia del formulario con los datos enviados (POST) y los archivos
        form = PagoForm(request.POST, request.FILES)
        
        # Verificamos si el formulario es válido según las reglas definidas en forms.py
        if form.is_valid():
            # Si es válido, guardamos el objeto en la base de datos
            form.save()
            
            # Mostramos un mensaje de éxito
            messages.success(request, '¡El pago ha sido registrado exitosamente!')
            
            # Redirigimos al usuario a otra página (ej. el dashboard o una lista de pagos)
            return redirect('pagos_paciente') # Asegúrate que 'dashboard_admin' es una URL válida
        else:
            # Si el formulario no es válido, mostramos un mensaje de error
            messages.error(request, 'Hubo un error en el formulario. Por favor, revisa los datos.')
            
    else:
        # Si la petición es GET, creamos una instancia del formulario vacío
        form = PagoForm()

    # Preparamos el contexto para enviar el formulario al template
    context = {
        'form': form
    }
    
    # Renderizamos la plantilla, pasándole el contexto
    return render(request, 'agregar_pagos_paciente.html', context)

@login_required
def ver_factura_pdf(request, pk):
    # 1) Recuperar el pago
    pago = get_object_or_404(Pago, pk=pk)

    # 2) Control de permisos (solo admin, paciente dueño o el fisioterapeuta asociado)
    user = request.user
    es_paciente = pago.consulta.paciente == user
    es_fisio = pago.consulta.fisioterapeuta == user
    if not (user.rol == Usuario.ADMIN or es_paciente or es_fisio):
        raise Http404("No tienes permiso para ver este comprobante.")

    # 3) Si existe el archivo, redirigir a su URL
    if pago.imagen_referencia:
        return redirect(pago.imagen_referencia.url)
    else:
        raise Http404("Este pago no tiene comprobante asociado.")