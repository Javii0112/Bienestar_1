
from .models import Logro, LogroUsuario, RegistroEmocion, RegistroHabito, Diario
from django.utils import timezone
from datetime import timedelta

def verificar_logros(usuario):
    """Revisa condiciones y desbloquea logros si corresponde."""
    nuevos = []

    total_emociones = RegistroEmocion.objects.filter(usuario=usuario).count()
    total_habitos   = RegistroHabito.objects.filter(usuario=usuario).count()
    total_diario    = Diario.objects.filter(usuario=usuario).count()

    # Racha de emociones (días consecutivos)
    racha_emociones = calcular_racha_emociones(usuario)
    racha_habitos   = calcular_racha_habitos(usuario)

    logros_condiciones = [
        # (slug-identificador, condicion_bool)
        ('primera_emocion',    total_emociones >= 1),
        ('cinco_emociones',    total_emociones >= 5),
        ('veinte_emociones',   total_emociones >= 20),
        ('primer_habito',      total_habitos >= 1),
        ('diez_habitos',       total_habitos >= 10),
        ('cincuenta_habitos',  total_habitos >= 50),
        ('primer_diario',      total_diario >= 1),
        ('cinco_diarios',      total_diario >= 5),
        ('racha_3_emociones',  racha_emociones >= 3),
        ('racha_7_emociones',  racha_emociones >= 7),
        ('racha_3_habitos',    racha_habitos >= 3),
        ('racha_7_habitos',    racha_habitos >= 7),
    ]

    for nombre_logro, condicion in logros_condiciones:
        if condicion:
            try:
                logro = Logro.objects.get(nombre=nombre_logro)
                _, creado = LogroUsuario.objects.get_or_create(
                    usuario=usuario, logro=logro
                )
                if creado:
                    nuevos.append(logro)
            except Logro.DoesNotExist:
                pass

    return nuevos  # lista de logros recién desbloqueados


def calcular_racha_emociones(usuario):
    """Cuenta cuántos días consecutivos el usuario ha registrado emociones."""
    from .models import RegistroEmocion
    from datetime import date, timedelta

    hoy = date.today()
    racha = 0
    dia = hoy

    while True:
        tiene = RegistroEmocion.objects.filter(
            usuario=usuario, fecha__date=dia
        ).exists()
        if tiene:
            racha += 1
            dia -= timedelta(days=1)
        else:
            break

    return racha


def calcular_racha_habitos(usuario):
    """Cuenta cuántos días consecutivos el usuario ha registrado hábitos."""
    from .models import RegistroHabito
    from datetime import date, timedelta

    hoy = date.today()
    racha = 0
    dia = hoy

    while True:
        tiene = RegistroHabito.objects.filter(
            usuario=usuario, fecha=dia
        ).exists()
        if tiene:
            racha += 1
            dia -= timedelta(days=1)
        else:
            break

    return racha