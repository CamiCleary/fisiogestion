from django.urls import path, include # Asegúrate de importar 'include' si lo usas en otras partes
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Un solo dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Pacientes
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='registro_paciente'),
    path('pacientes/editar/<int:pk>/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/eliminar/<int:pk>/', views.eliminar_paciente, name='eliminar_paciente'),
    
    # Citas (si es una vista separada de calendario_view)
    path('citas/', views.horarios_list, name='citas'),
    path('citas/<int:pk>/editar/', views.editar_horario, name='cita_editar'),
    path('citas/<int:pk>/eliminar/', views.eliminar_horario, name='cita_eliminar'),
    
    # Calendario y sus APIs (agrupadas y sin duplicados)
    path('calendario/', views.calendario, name='calendario'), # Única definición para la vista del calendario
    
    # Consultas (si es diferente de las citas del calendario)
    path('consultas/', views.consultas, name='consultas'),
    path('consultas/nuevo/', views.crear_consulta, name='crear_consulta'),
    path('consultas/editar/<int:pk>/', views.editar_consulta, name='editar_consulta'),
    path('consultas/eliminar/<int:pk>/', views.eliminar_consulta, name='eliminar_consulta'),
    
    # Fisioterapeutas
    path('fisioterapeutas/', views.lista_fisioterapeutas, name='lista_fisioterapeutas'),
    path('fisioterapeutas/nuevo/', views.crear_fisioterapeuta, name='registro_fisioterapeuta'),
    path('fisioterapeutas/editar/<int:pk>/', views.editar_fisioterapeuta, name='editar_fisioterapeuta'),
    path('fisioterapeutas/eliminar/<int:pk>/', views.eliminar_fisioterapeuta, name='eliminar_fisioterapeuta'),

    # Reportes y telemedicina
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/pdf/', views.reporte_pdf, name='reporte_pdf'),
    path('reporte_paciente/', views.reporte_paciente_view, name='reporte_paciente'),
    path(
      'telemedicina/',
      views.telemedicina_view,
      name='telemedicina'
    ),
    path('telemedicina_paciente/', views.telemedicina_paciente_view, name='telemedicina_paciente'),
    
    # Pagos
    path('pagos_fisioterapeuta/', views.pagos_fisioterapeuta, name='pagos_fisioterapeuta'),
    path('pagos_paciente/', views.pagos_paciente, name='pagos_paciente'),
    path('pagos_administrador/', views.pagos_administrador, name='pagos_administrador'),
    path('agregar_pagos/', views.agregar_pagos, name='agregar_pagos'),
    path(
        'ver_factura_pdf/<int:pk>/',
        views.ver_factura_pdf,
        name='ver_factura_pdf'
    ),
]

# Configuración para servir archivos de medios en desarrollo (MEDIA_URL)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)