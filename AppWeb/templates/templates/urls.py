from django.urls import path
from . import views

urlpatterns = [
    # Vistas generales (se mantienen)
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),

    # CRUD de Pacientes (ya existente, base para todos)
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/editar/<int:pk>/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/eliminar/<int:pk>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('registro_paciente/', views.crear_paciente, name='registro_paciente'), # Considera si esta es redundante con 'pacientes/nuevo/'

    # CRUD de Fisioterapeutas (ya existente, base para todos)
    path('fisioterapeutas/', views.lista_fisioterapeutas, name='lista_fisioterapeutas'),
    path('registro_fisioterapeuta/', views.crear_fisioterapeuta, name='registro_fisioterapeuta'), # Considera si esta es redundante

    # --- VISTAS ASIGNADAS A SAMUEL (ADMIN) ---

    # Dashboard Admin
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),

    # Gestión de Usuarios y Roles
    path('admin/usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('admin/usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('admin/roles/', views.gestionar_roles, name='gestionar_roles'),

    # Detalle de Pacientes y Fisioterapeutas (Admin)
    path('admin/pacientes/<int:pk>/', views.detalle_paciente_admin, name='detalle_paciente_admin'),
    path('admin/fisioterapeutas/<int:pk>/', views.detalle_fisioterapeuta, name='detalle_fisioterapeuta'),

    # Gestión de Consultas (Admin)
    path('admin/consultas/', views.lista_consultas, name='lista_consultas_admin'),
    path('admin/consultas/crear/', views.crear_consulta, name='crear_consulta'),
    path('admin/consultas/<int:pk>/editar/', views.editar_consulta, name='editar_consulta'),
    path('admin/consultas/<int:pk>/', views.detalle_consulta, name='detalle_consulta'),
    path('admin/consultas/<int:pk>/eliminar/', views.eliminar_consulta, name='eliminar_consulta'),

    # Gestión de Pagos y Facturación (Admin)
    path('admin/pagos/', views.lista_pagos, name='lista_pagos_admin'),
    path('admin/pagos/registrar/', views.registrar_pago, name='registrar_pago'),
    path('admin/pagos/<int:pk>/', views.detalle_pago, name='detalle_pago'),
    path('admin/pagos/<int:pk>/eliminar/', views.eliminar_pago, name='eliminar_pago'),

    # Telemedicina Admin
    path('admin/telemedicina/', views.telemedicina, name='telemedicina_admin'), # Renombrado para claridad

    # Reportes Admin
    path('admin/reportes/', views.reportes, name='reportes_admin'), # Renombrado para claridad
]