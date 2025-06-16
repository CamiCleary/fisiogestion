from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    # Autenticación
    path('login/',  views.login_view,    name='login'),
    path('logout/', views.logout_view,   name='logout'),
    path('dashboard/', views.dashboard,  name='dashboard'),  # Página tras login

    # Gestión de Pacientes
    path('pacientes/',               views.lista_pacientes,  name='lista_pacientes'),
    path('pacientes/nuevo/',         views.crear_paciente,   name='crear_paciente'),
    path('pacientes/editar/<int:pk>/',   views.editar_paciente, name='editar_paciente'),
    path('pacientes/eliminar/<int:pk>/', views.eliminar_paciente, name='eliminar_paciente'),

    # Registro de nuevos
    path('registro_paciente/',        views.crear_paciente,         name='registro_paciente'),
    path('registro_fisioterapeuta/',  views.crear_fisioterapeuta,   name='registro_fisioterapeuta'),

    # Gestión de Fisioterapeutas
    path('fisioterapeutas/',         views.lista_fisioterapeutas, name='lista_fisioterapeutas'),
]
