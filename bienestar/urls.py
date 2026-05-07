from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from bienestar.views import EmailTokenObtainPairView
from .views import mensajes_view

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('habitos/', views.registro_habitos, name='habitos'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path("estadistica/", views.estadistica_view, name="estadistica"),
    path("recursos/", views.recursos_view, name="recursos"),
    path("diario/", views.diario, name="diario"),
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logros/', views.logros_view, name='logros'),
    path('limpiar-logros/', views.limpiar_logros_sesion, name='limpiar_logros_sesion'),
    path('mensajes/', mensajes_view, name='mensajes'),
    path('habitos/recomendaciones/', views.recomendaciones_habitos, name='recomendaciones_habitos'),
    path("diario/<int:pk>/editar/", views.diario_editar, name="diario_editar"),
    path("diario/<int:pk>/eliminar/", views.diario_eliminar, name="diario_eliminar"),
    path('emociones/', views.lista_emociones, name='lista_emociones'),
    path('emociones/nueva/', views.crear_emocion, name='crear_emocion'),
    path('emociones/editar/<int:id>/', views.editar_emocion, name='editar_emocion'),
    path('emociones/eliminar/<int:id>/', views.eliminar_emocion, name='eliminar_emocion'),
    path("cambiar-password/", views.cambiar_password_view, name="cambiar_password"),

    # ✅ API para app de escritorio
    path('api/students/', views.AlumnoListView.as_view(), name='api_alumnos'),
    path('api/students/<int:pk>/', views.AlumnoPerfilView.as_view(), name='api_alumno_perfil'),
    path('api/students/<int:pk>/emociones/', views.AlumnoEmocionesView.as_view(), name='api_alumno_emociones'),
    path('api/students/<int:pk>/habitos/', views.AlumnoHabitosView.as_view(), name='api_alumno_habitos'),
    path('api/students/<int:pk>/diario/', views.AlumnoDiarioView.as_view(), name='api_alumno_diario'),
    path('api/students/<int:pk>/notas/', views.AlumnoNotasView.as_view(), name='api_alumno_notas'),
]