from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


# ==================================================
# MANAGER DE USUARIO (OBLIGATORIO)
# ==================================================
class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener email")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


# ==================================================
# ESTADO USUARIO
# ==================================================
class EstadoUsuario(models.Model):
    nombre_estado = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_estado


# ==================================================
# USUARIO (CUSTOM)
# ==================================================
class Usuario(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    estado_usuario = models.ForeignKey(
        EstadoUsuario,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# ==================================================
# PERFIL
# ==================================================
class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# ==================================================
# ESTADO DE ÁNIMO
# ==================================================
class EstadoAnimo(models.Model):
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion


class RegistroEstadoAnimo(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    estado_animo = models.ForeignKey(EstadoAnimo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)


# ==================================================
# EMOCIÓN
# ==================================================
class CategoriaEmocion(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Emocion(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaEmocion, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class RegistroEmocion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emocion = models.ForeignKey(Emocion, on_delete=models.CASCADE)
    intensidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)


# ==================================================
# HÁBITOS
# ==================================================
class TipoHabito(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Habito(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.ForeignKey(TipoHabito, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class RegistroHabito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    habito = models.ForeignKey(Habito, on_delete=models.CASCADE)
    fecha = models.DateField()
    valor = models.IntegerField()


# ==================================================
# METAS
# ==================================================
class MetaBienestar(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()

    def __str__(self):
        return self.descripcion


class ProgresoMeta(models.Model):
    meta = models.ForeignKey(MetaBienestar, on_delete=models.CASCADE)
    porcentaje = models.IntegerField()
    fecha = models.DateField()


# ==================================================
# NOTIFICACIONES
# ==================================================
class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField()
    estado = models.CharField(max_length=50)


class Recordatorio(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensaje = models.TextField()
    hora = models.TimeField()


# ==================================================
# AUDITORÍA
# ==================================================
class Auditoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

# ==================================================
# diario
# ==================================================
class Diario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.fecha}"