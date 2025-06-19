from django.urls import path
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
    path('citas/', views.citas_view, name='citas'),
    path('calendario/', views.calendario_view, name='calendario'),
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
    path('pacientes/reporte/', views.reporte_pacientes_view, name='reporte_pacientes'),
    path('telemedicina/', views.telemedicina_view, name='telemedicina'),
    path('telemedicina-paciente/', views.telemedicina_paciente_view, name='telemedicina-paciente'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)