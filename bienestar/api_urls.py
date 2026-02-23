from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    EmocionViewSet,
    RegistroEmocionViewSet,
    AlumnoListView,
    AlumnoPerfilView,
    AlumnoEmocionesView,
    AlumnoHabitosView,
    AlumnoDiarioView,
    AlumnoNotasView,
)

router = DefaultRouter()
router.register(r'emociones',         EmocionViewSet,         basename='emocion')
router.register(r'registros-emocion', RegistroEmocionViewSet, basename='registro-emocion')

urlpatterns = router.urls + [
    path('alumnos/',                    AlumnoListView.as_view(),      name='alumnos-list'),
    path('alumnos/<int:pk>/perfil/',    AlumnoPerfilView.as_view(),    name='alumno-perfil'),
    path('alumnos/<int:pk>/emociones/', AlumnoEmocionesView.as_view(), name='alumno-emociones'),
    path('alumnos/<int:pk>/habitos/',   AlumnoHabitosView.as_view(),   name='alumno-habitos'),
    path('alumnos/<int:pk>/diario/',    AlumnoDiarioView.as_view(),    name='alumno-diario'),
    path('alumnos/<int:pk>/notas/',     AlumnoNotasView.as_view(),     name='alumno-notas'),
]