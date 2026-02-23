from rest_framework import serializers
from .models import (
    Emocion, RegistroEmocion,
    Perfil, Usuario,
    RegistroHabito, Habito,
    Diario, NotaPsicologo
)
from datetime import date


# ── Emociones ─────────────────────────────────────
class EmocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emocion
        fields = "__all__"


class RegistroEmocionSerializer(serializers.ModelSerializer):
    emocion_nombre = serializers.CharField(source='emocion.nombre', read_only=True)

    class Meta:
        model  = RegistroEmocion
        fields = ['id', 'emocion', 'emocion_nombre', 'intensidad', 'comentario', 'fecha']


# ── Perfil alumno ─────────────────────────────────
class PerfilSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='usuario.email', read_only=True)
    edad  = serializers.SerializerMethodField()

    class Meta:
        model  = Perfil
        fields = ['id', 'nombre', 'apellido', 'email', 'genero', 'fecha_nacimiento', 'edad']

    def get_edad(self, obj):
        if not obj.fecha_nacimiento:
            return None
        hoy = date.today()
        fn  = obj.fecha_nacimiento
        return hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))


# ── Lista de alumnos (vista resumida) ─────────────
class AlumnoResumenSerializer(serializers.ModelSerializer):
    nombre   = serializers.CharField(source='perfil.nombre',   read_only=True)
    apellido = serializers.CharField(source='perfil.apellido', read_only=True)

    class Meta:
        model  = Usuario
        fields = ['id', 'email', 'nombre', 'apellido', 'fecha_creacion']


# ── Hábitos ───────────────────────────────────────
class HabitoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Habito
        fields = ['id', 'nombre', 'descripcion']


class RegistroHabitoSerializer(serializers.ModelSerializer):
    habito_nombre = serializers.CharField(source='habito.nombre', read_only=True)

    class Meta:
        model  = RegistroHabito
        fields = ['id', 'habito', 'habito_nombre', 'fecha', 'valor']


# ── Diario ────────────────────────────────────────
class DiarioSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Diario
        fields = ['id', 'contenido', 'fecha']


# ── Notas del psicólogo ───────────────────────────
class NotaPsicologoSerializer(serializers.ModelSerializer):
    psicologo_email = serializers.EmailField(source='psicologo.email', read_only=True)

    class Meta:
        model  = NotaPsicologo
        fields = ['id', 'contenido', 'fecha', 'psicologo_email']
        read_only_fields = ['fecha', 'psicologo_email']