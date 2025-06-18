from django.urls import path
from . import views

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

    # Fisioterapeutas
    path('fisioterapeutas/', views.lista_fisioterapeutas, name='lista_fisioterapeutas'),
    path('fisioterapeutas/nuevo/', views.crear_fisioterapeuta, name='registro_fisioterapeuta'),
    path('fisioterapeutas/editar/<int:pk>/', views.editar_fisioterapeuta, name='editar_fisioterapeuta'),
    path('fisioterapeutas/eliminar/<int:pk>/', views.eliminar_fisioterapeuta, name='eliminar_fisioterapeuta'),

    # Reportes y telemedicina
    path('reportes/', views.reportes, name='reportes'),
    path('pacientes/reporte/', views.reporte_pacientes_view, name='reporte_pacientes'),
    path('telemedicina/', views.telemedicina_view, name='telemedicina'),
]