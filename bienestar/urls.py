from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from bienestar.views import EmailTokenObtainPairView

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('habitos/', views.registro_habitos, name='habitos'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path("estadistica/", views.estadistica_view, name="estadistica"),
    path("recursos/", views.recursos_view, name="recursos"),
    path("diario/", views.diario,
          name="diario"),
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logros/', views.logros_view, name='logros'),
    path('limpiar-logros/', views.limpiar_logros_sesion, name='limpiar_logros_sesion'),
]
