from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.http import Http404
from django.contrib.auth import get_user_model
from .forms import PacienteForm, FisioterapeutaForm, LoginForm, ConsultaForm , PagoForm , PlanTratamientoForm, HorarioForm
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import json
from django.utils import timezone # Importar timezone para manejar fechas con zonas horarias


# Importar los modelos y formularios de tu app
from .models import Usuario, Consulta, Pago, Horario , PlanTratamiento, Teleconsulta # Asegúrate de importar Horario si lo usas
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
    # Totales
    total_usuarios  = Usuario.objects.count()
    total_consultas = Consulta.objects.count()
    total_pagos     = Pago.objects.count()
    suma_pagos      = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0

    # Consultas por mes
    consultas_qs = (
        Consulta.objects
        .values('fecha_consulta__year', 'fecha_consulta__month')
        .annotate(c=Count('id'))
        .order_by('fecha_consulta__year','fecha_consulta__month')
    )
    meses = [f"{item['fecha_consulta__year']}-{item['fecha_consulta__month']:02d}" for item in consultas_qs]
    consultas_por_mes = [item['c'] for item in consultas_qs]

    # Ingresos mensuales
    pagos_qs = (
        Pago.objects
        .values('fecha_pago__year', 'fecha_pago__month')
        .annotate(total=Sum('monto'))
        .order_by('fecha_pago__year','fecha_pago__month')
    )
    ingresos_mensuales_labels = [f"{item['fecha_pago__year']}-{item['fecha_pago__month']:02d}" for item in pagos_qs]
    ingresos_mensuales_data   = [float(item['total']) for item in pagos_qs]

    # Pagos por usuario (top 5)
    pagos_user_qs = (
        Pago.objects
        .values('consulta__paciente__nombre')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    usuarios_con_pagos = [item['consulta__paciente__nombre'] for item in pagos_user_qs]
    pagos_por_usuario  = [item['count'] for item in pagos_user_qs]

    context = {
        'total_usuarios': total_usuarios,
        'total_consultas': total_consultas,
        'total_pagos': total_pagos,
        'suma_pagos': suma_pagos,
        'meses': meses,
        'consultas_por_mes': consultas_por_mes,
        'ingresos_mensuales_labels': ingresos_mensuales_labels,
        'ingresos_mensuales_data': ingresos_mensuales_data,
        'usuarios_con_pagos': usuarios_con_pagos,
        'pagos_por_usuario': pagos_por_usuario,
    }
    return render(request, 'reportes.html', context)

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
def horarios_list(request):
    horarios = (
        Horario.objects
        .select_related('fisioterapeuta')
        .all()
        .order_by('dia_semana', 'hora_inicio')
    )
    # Si quieres contar cuántos horarios hay a partir de hoy:
    proximos = horarios.count()  # o lógica distinta, pues no hay fecha_consulta
    return render(request, 'citas.html', {
        'consultas': horarios,   # tu plantilla lee 'consultas'
        'proximas': proximos,
        'page_title': 'Lista de Horarios'
    })

@login_required
def editar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    form = HorarioForm(request.POST or None, instance=horario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Horario actualizado correctamente.")
        return redirect('citas')
    return render(request, 'cita_form.html', {
        'form': form,
        'page_title': 'Editar Horario'
    })

@login_required
def eliminar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        horario.delete()
        messages.success(request, "Horario eliminado.")
        return redirect('citas')
    return render(request, 'cita_confirm_delete.html', {
        'horario': horario,
        'page_title': 'Eliminar Horario'
    })



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
    
@login_required
def telemedicina(request):
    return render(request, "telemedicina_fisioterapeuta.html")


@login_required
def reporte_pdf(request):
    # 1) Totales generales
    total_pacientes        = Usuario.objects.filter(rol=Usuario.PACIENTE).count()
    total_fisioterapeutas  = Usuario.objects.filter(rol=Usuario.FISIOTERAPEUTA).count()
    mes_actual             = datetime.now().month
    total_citas_mes        = Consulta.objects.filter(fecha_consulta__month=mes_actual).count()
    ingresos_totales       = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0

    # 2) Datos para gráfico de citas por mes
    datos_citas = (
        Consulta.objects
        .annotate(mes=TruncMonth('fecha_consulta'))
        .values('mes')
        .annotate(c=Count('id'))
        .order_by('mes')
    )
    # Etiquetas cortas de meses y porcentaje respecto al máximo
    meses_etq    = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    max_c        = max((d['c'] for d in datos_citas), default=1)
    citas_mensuales = { meses_etq[d['mes'].month-1]: int((d['c']/max_c)*100) for d in datos_citas }

    # 3) Contexto que pasamos al PDF
    context = {
        'total_pacientes'       : total_pacientes,
        'total_fisioterapeutas' : total_fisioterapeutas,
        'total_citas_mes'       : total_citas_mes,
        'ingresos_totales'      : ingresos_totales,
        'citas_mensuales'       : citas_mensuales,
    }

    # 4) Render a HTML y luego a PDF
    template = get_template('reportes_pdf.html')
    html     = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f"Error al generar PDF:<br/><pre>{html}</pre>")
    return response
   
   
@login_required
def calendario(request):
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Horario creado exitosamente.")
            return redirect('citas')  # Ajusta este nombre de URL según tu configuración
    else:
        form = HorarioForm()
    return render(request, 'calendario.html', {'form': form})