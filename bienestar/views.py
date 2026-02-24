from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Perfil
from datetime import date
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import re
from .models import (
    Habito,
    RegistroEmocion,
    RegistroHabito,
    Diario,
    Emocion,
    Logro,
    LogroUsuario,
)
from .utils import verificar_logros

User = get_user_model()


def guardar_logros_sesion(request, nuevos_logros):
    """Guarda los logros nuevos en la sesión para mostrar la animación."""
    if nuevos_logros:
        request.session['nuevos_logros'] = [
            {'nombre': l.descripcion, 'icono': l.icono} for l in nuevos_logros
        ]


# ==================================================
# REGISTRO
# ==================================================
def registro_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        email = request.POST.get("email")
        password1 = request.POST.get("password")
        password2 = request.POST.get("password2")
        genero = request.POST.get("genero")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")

        if not email.endswith("@duocuc.cl"):
            messages.error(request, "Debes usar tu correo institucional @duocuc.cl")
            return render(request, "registro.html", locals())

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya está registrado")
            return render(request, "registro.html", locals())

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, "registro.html", locals())

        if len(password1) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres")
            return render(request, "registro.html", locals())
        if not re.search(r"[A-Z]", password1):
            messages.error(request, "La contraseña debe tener al menos una letra mayúscula")
            return render(request, "registro.html", locals())
        if not re.search(r"[a-z]", password1):
            messages.error(request, "La contraseña debe tener al menos una letra minúscula")
            return render(request, "registro.html", locals())
        if not re.search(r"[0-9]", password1):
            messages.error(request, "La contraseña debe tener al menos un número")
            return render(request, "registro.html", locals())
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
            messages.error(request, "La contraseña debe tener al menos un carácter especial (!@#$...)")
            return render(request, "registro.html", locals())

        if genero not in ["F", "M", "O"]:
            messages.error(request, "Debes seleccionar un género válido")
            return render(request, "registro.html", locals())

        try:
            fecha_nac = date.fromisoformat(fecha_nacimiento)
        except ValueError:
            messages.error(request, "Fecha de nacimiento inválida")
            return render(request, "registro.html", locals())

        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

        if fecha_nac.year < 1920:
            messages.error(request, "Fecha de nacimiento no válida")
            return render(request, "registro.html", locals())

        if edad < 18:
            messages.error(request, "Debes ser mayor de 18 años")
            return render(request, "registro.html", locals())

        user = User.objects.create_user(
            email=email,
            password=password1,
            first_name=nombre,
            last_name=apellido
        )

        Perfil.objects.create(
            usuario=user,
            nombre=nombre,
            apellido=apellido,
            genero=genero,
            fecha_nacimiento=fecha_nac
        )

        messages.success(request, "Usuario registrado correctamente")
        return redirect("login")

    return render(request, "registro.html")


# ==================================================
# LOGIN
# ==================================================
def login_view(request):
    if request.method == "POST":
        email    = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            # ← render en vez de redirect para que el mensaje no se pierda
            return render(request, "login.html", {
                "error": "Correo o contraseña incorrectos.",
                "email": email  # para no borrar el email que escribió
            })

    return render(request, "login.html")


# ==================================================
# DASHBOARD
# ==================================================
@login_required
def dashboard_view(request):
    emociones = Emocion.objects.all()

    if request.method == "POST":
        emocion_id = request.POST.get("emocion")
        intensidad = request.POST.get("intensidad")
        descripcion = request.POST.get("descripcion", "")

        if not emocion_id:
            messages.error(request, "Por favor selecciona una emoción")
        elif not intensidad:
            messages.error(request, "Por favor selecciona una intensidad")
        else:
            try:
                RegistroEmocion.objects.create(
                    usuario=request.user,
                    emocion_id=int(emocion_id),
                    intensidad=int(intensidad),
                    comentario=descripcion
                )
                # Verificar logros
                nuevos_logros = verificar_logros(request.user)
                guardar_logros_sesion(request, nuevos_logros)

                messages.success(request, "¡Emoción registrada exitosamente! 💚")
            except Exception as e:
                messages.error(request, f"Error al guardar: {str(e)}")

        return redirect("dashboard")

    # Última emoción registrada hoy
    hoy = date.today()
    emocion_hoy = RegistroEmocion.objects.filter(
        usuario=request.user,
        fecha__date=hoy
    ).select_related('emocion').last()

    # Todas las emociones registradas (para el historial)
    todas_emociones = RegistroEmocion.objects.filter(
        usuario=request.user
    ).select_related('emocion').order_by('-fecha')[:20]

    # Hábitos registrados hoy
    habitos_hoy = RegistroHabito.objects.filter(
        usuario=request.user,
        fecha=hoy
    ).select_related('habito').order_by('-id')

    return render(request, "dashboard.html", {
        "emociones": emociones,
        "emocion_hoy": emocion_hoy,
        "todas_emociones": todas_emociones,
        "habitos_hoy": habitos_hoy,
    })


# ==================================================
# HÁBITOS
# ==================================================
@login_required
def registro_habitos(request):
    from datetime import timedelta
    habitos = Habito.objects.select_related("tipo").all()
    hoy = date.today()

    if request.method == "POST":
        habito_id = request.POST.get("habito")
        valor = request.POST.get("valor")

        if not habito_id or not valor:
            messages.error(request, "Debes seleccionar un hábito e ingresar un valor.", extra_tags="habito")
            return redirect("habitos")

        habito = Habito.objects.filter(id=habito_id).first()

        if habito:
            ya_registrado = RegistroHabito.objects.filter(
                usuario=request.user,
                habito=habito,
                fecha=hoy
            ).exists()

            if ya_registrado:
                messages.error(request, f"Ya registraste '{habito.nombre}' hoy. ¡Vuelve mañana!", extra_tags="habito")
            else:
                try:
                    valor_int = int(valor)
                    if valor_int < 1:
                        raise ValueError
                    RegistroHabito.objects.create(
                        usuario=request.user,
                        habito=habito,
                        fecha=hoy,
                        valor=valor_int
                    )
                    nuevos_logros = verificar_logros(request.user)
                    guardar_logros_sesion(request, nuevos_logros)
                    messages.success(request, f"¡'{habito.nombre}' registrado correctamente! 💪", extra_tags="habito")
                except ValueError:
                    messages.error(request, "El valor debe ser un número válido mayor a 0.", extra_tags="habito")

        return redirect("habitos")

    habitos_hoy = RegistroHabito.objects.filter(
        usuario=request.user,
        fecha=hoy
    ).select_related("habito__tipo").order_by("-id")

    habitos_hoy_ids = list(habitos_hoy.values_list("habito_id", flat=True))

    from .utils import calcular_racha_habitos
    racha = calcular_racha_habitos(request.user)

    # Encontrar el domingo más reciente
    dias_desde_domingo = (hoy.weekday() + 1) % 7
    domingo = hoy - timedelta(days=dias_desde_domingo)
    dias_semana = [domingo + timedelta(days=i) for i in range(7)]

    dias_con_habito = set(
        RegistroHabito.objects.filter(
            usuario=request.user,
            fecha__in=dias_semana
        ).values_list("fecha", flat=True)
    )

    dias_es = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    progreso_semanal = [{"dia": dias_es[(d.weekday() + 1) % 7], "activo": d in dias_con_habito} for d in dias_semana]

    return render(request, "habitos.html", {
        "habitos": habitos,
        "habitos_hoy": habitos_hoy,
        "habitos_hoy_ids": habitos_hoy_ids,
        "racha": racha,
        "progreso_semanal": progreso_semanal,
        "total_hoy": habitos_hoy.count(),
    })

# ==================================================
# RECOMENDACIONES CON IA (agregar en views.py)
# ==================================================
import os
import anthropic

@login_required
def recomendaciones_habitos(request):
    """Vista que genera recomendaciones personalizadas con Claude."""
    from django.http import JsonResponse
    from datetime import timedelta

    hoy = date.today()
    ultima_semana = hoy - timedelta(days=7)

    # Obtener historial del usuario
    registros = RegistroHabito.objects.filter(
        usuario=request.user,
        fecha__gte=ultima_semana
    ).select_related('habito__tipo')

    # Construir resumen del historial
    resumen = {}
    for r in registros:
        nombre = r.habito.nombre
        if nombre not in resumen:
            resumen[nombre] = {'dias': 0, 'tipo': r.habito.tipo.nombre}
        resumen[nombre]['dias'] += 1

    if resumen:
        historial_texto = ", ".join([
            f"{nombre} ({datos['dias']} días esta semana)"
            for nombre, datos in resumen.items()
        ])
    else:
        historial_texto = "ningún hábito registrado aún"

    # Llamar a Claude
    try:
        cliente = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        respuesta = cliente.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": f"""Eres un coach de bienestar para estudiantes universitarios.
                El estudiante ha registrado esta semana: {historial_texto}.
                Dame exactamente 3 recomendaciones de hábitos saludables personalizadas y cortas.
                Formato de respuesta (solo esto, sin texto extra):
                1. [emoji] Título corto: descripción breve en máximo 15 palabras.
                2. [emoji] Título corto: descripción breve en máximo 15 palabras.
                3. [emoji] Título corto: descripción breve en máximo 15 palabras."""
                            }]
                        )
        texto = respuesta.content[0].text
        # Parsear las 3 recomendaciones
        lineas = [l.strip() for l in texto.strip().split('\n') if l.strip()]
        recomendaciones = []
        for linea in lineas[:3]:
            # Quitar el número del inicio (1. 2. 3.)
            if linea and linea[0].isdigit():
                linea = linea[2:].strip()
            partes = linea.split(':', 1)
            if len(partes) == 2:
                recomendaciones.append({
                    'titulo': partes[0].strip(),
                    'descripcion': partes[1].strip()
                })
            else:
                recomendaciones.append({
                    'titulo': linea,
                    'descripcion': ''
                })

    except Exception as e:
        recomendaciones = [
            {'titulo': '💧 Hidratación', 'descripcion': 'Bebe al menos 8 vasos de agua al día.'},
            {'titulo': '🏃 Ejercicio', 'descripcion': 'Camina 30 minutos para activar tu energía.'},
            {'titulo': '😴 Descanso', 'descripcion': 'Duerme 7-9 horas para rendir mejor.'},
        ]

    return JsonResponse({'recomendaciones': recomendaciones})

# ==================================================
# ESTADÍSTICAS
# ==================================================
@login_required
def estadistica_view(request):
    from datetime import timedelta
    from django.db.models import Avg, Count

    hoy = date.today()
    dias_semana = [(hoy - timedelta(days=i)) for i in range(6, -1, -1)]

    registros_semana = RegistroEmocion.objects.filter(
        usuario=request.user,
        fecha__date__in=dias_semana
    ).select_related('emocion')

    datos_por_dia = {}
    for r in registros_semana:
        dia = r.fecha.date()
        if dia not in datos_por_dia:
            datos_por_dia[dia] = []
        datos_por_dia[dia].append(r.intensidad)

    nombres_dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    grafico_semana = []
    for i, dia in enumerate(dias_semana):
        intensidades = datos_por_dia.get(dia, [])
        promedio = round(sum(intensidades) / len(intensidades), 1) if intensidades else 0
        altura = int(promedio * 40)
        grafico_semana.append({
            "label": nombres_dias[dia.weekday()],
            "altura": altura,
            "promedio": promedio,
        })

    todos_registros = RegistroEmocion.objects.filter(usuario=request.user)
    total_registros = todos_registros.count()

    intensidad_promedio = todos_registros.aggregate(Avg('intensidad'))['intensidad__avg']
    intensidad_promedio = round(intensidad_promedio, 1) if intensidad_promedio else 0

    emocion_frecuente = (
        todos_registros
        .values('emocion__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    emocion_frecuente_nombre = emocion_frecuente['emocion__nombre'] if emocion_frecuente else "Sin datos"

    return render(request, "estadistica.html", {
        "grafico_semana": grafico_semana,
        "total_registros": total_registros,
        "intensidad_promedio": intensidad_promedio,
        "emocion_frecuente": emocion_frecuente_nombre,
    })


# ==================================================
# RECURSOS
# ==================================================
@login_required
def recursos_view(request):
    return render(request, "recursos.html")


# ==================================================
# DIARIO
# ==================================================
@login_required
def diario(request):
    if request.method == 'POST':
        texto = request.POST.get('contenido')

        if texto:
            Diario.objects.create(
                usuario=request.user,
                contenido=texto
            )
            # Verificar logros
            nuevos_logros = verificar_logros(request.user)
            guardar_logros_sesion(request, nuevos_logros)

            messages.success(request, "¡Entrada guardada en tu diario! 📓", extra_tags='diario')
            return redirect('diario')

    entradas = Diario.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'diario.html', {"entradas": entradas})


# ==================================================
# PERFIL
# ==================================================
@login_required
def perfil(request):
    perfil_obj = Perfil.objects.get(usuario=request.user)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "")
        genero = request.POST.get("genero", "")

        if not nombre or not apellido:
            messages.error(request, "Nombre y apellido son obligatorios", extra_tags='perfil')
        else:
            perfil_obj.nombre = nombre
            perfil_obj.apellido = apellido
            perfil_obj.genero = genero
            if fecha_nacimiento:
                try:
                    perfil_obj.fecha_nacimiento = date.fromisoformat(fecha_nacimiento)
                except ValueError:
                    messages.error(request, "Fecha de nacimiento inválida", extra_tags='perfil')
                    return render(request, "perfil.html", {"perfil": perfil_obj})
            perfil_obj.save()

            request.user.first_name = nombre
            request.user.last_name = apellido
            request.user.save()

            messages.success(request, "¡Perfil actualizado correctamente! ✅", extra_tags='perfil')
            return redirect("perfil")

    return render(request, "perfil.html", {"perfil": perfil_obj})


# ==================================================
# LOGROS
# ==================================================
@login_required
def logros_view(request):
    todos = Logro.objects.all()
    obtenidos = LogroUsuario.objects.filter(
        usuario=request.user
    ).select_related('logro')

    obtenidos_ids = {lu.logro.id: lu.fecha_obtenido for lu in obtenidos}

    categorias = {
        'emocion': {'label': '🧠 Emociones', 'logros': []},
        'habito':  {'label': '💪 Hábitos',   'logros': []},
        'diario':  {'label': '📓 Diario',     'logros': []},
        'racha':   {'label': '🔥 Rachas',     'logros': []},
        'general': {'label': '⭐ General',    'logros': []},
    }

    for logro in todos:
        cat = logro.categoria if logro.categoria in categorias else 'general'
        categorias[cat]['logros'].append({
            'logro': logro,
            'obtenido': logro.id in obtenidos_ids,
            'fecha': obtenidos_ids.get(logro.id),
        })

    total_logros    = todos.count()
    total_obtenidos = len(obtenidos_ids)
    porcentaje = round((total_obtenidos / total_logros * 100) if total_logros else 0)

    return render(request, 'logros.html', {
        'logros_por_categoria': categorias,
        'total_logros': total_logros,
        'total_obtenidos': total_obtenidos,
        'porcentaje': porcentaje,
    })


# ==================================================
# LIMPIAR LOGROS SESIÓN (llamado por JS)
# ==================================================
@require_POST
def limpiar_logros_sesion(request):
    request.session.pop('nuevos_logros', None)
    return JsonResponse({'ok': True})



# ==================================================
# VISTAS API PARA APP DE ESCRITORIO
# Agrega esto al FINAL de tu views.py existente
# ==================================================
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Usuario, Perfil, RegistroEmocion, RegistroHabito, Diario
from .serializers import (
    EmocionSerializer, RegistroEmocionSerializer,
    AlumnoResumenSerializer, PerfilSerializer,
    RegistroHabitoSerializer, DiarioSerializer,
)
from .serializers_auth import EmailTokenObtainPairSerializer



class EmocionViewSet(viewsets.ModelViewSet):
    queryset = Emocion.objects.all()
    serializer_class = EmocionSerializer


class RegistroEmocionViewSet(viewsets.ModelViewSet):
    queryset = RegistroEmocion.objects.all()
    serializer_class = RegistroEmocionSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


# ── Nuevas vistas para app escritorio ────────────

class AlumnoListView(generics.ListAPIView):
    """
    GET /api/alumnos/
    Lista todos los usuarios NO admin (alumnos).
    Solo accesible por administradores.
    """
    serializer_class = AlumnoResumenSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Usuario.objects.filter(
            is_staff=False,
            is_superuser=False
        ).select_related('perfil').order_by('perfil__apellido')


class AlumnoPerfilView(generics.RetrieveAPIView):
    """
    GET /api/alumnos/<id>/perfil/
    Devuelve el perfil completo de un alumno.
    """
    serializer_class = PerfilSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        return generics.get_object_or_404(Perfil, usuario__id=self.kwargs['pk'])


class AlumnoEmocionesView(generics.ListAPIView):
    """
    GET /api/alumnos/<id>/emociones/
    Devuelve el historial de emociones de un alumno.
    """
    serializer_class = RegistroEmocionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return RegistroEmocion.objects.filter(
            usuario__id=self.kwargs['pk']
        ).select_related('emocion').order_by('-fecha')


class AlumnoHabitosView(generics.ListAPIView):
    """
    GET /api/alumnos/<id>/habitos/
    Devuelve el historial de hábitos de un alumno.
    """
    serializer_class = RegistroHabitoSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return RegistroHabito.objects.filter(
            usuario__id=self.kwargs['pk']
        ).select_related('habito').order_by('-fecha')


class AlumnoDiarioView(generics.ListAPIView):
    """
    GET /api/alumnos/<id>/diario/
    Devuelve las entradas del diario de un alumno.
    """
    serializer_class = DiarioSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Diario.objects.filter(
            usuario__id=self.kwargs['pk']
        ).order_by('-fecha')

# ==================================================
# VISTA MENSAJES
# Agrega esto en tu views.py
# ==================================================

@login_required
def mensajes_view(request):
    from .models import NotaPsicologo
    notas = NotaPsicologo.objects.filter(
        alumno=request.user
    ).order_by('-fecha')

    # Marcar todos como leídos al abrir la página
    notas.filter(leido=False).update(leido=True)

    return render(request, 'mensajes.html', {'notas': notas})

# ==================================================
# VISTAS API PARA APP DE ESCRITORIO
# ==================================================
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Usuario, Perfil, RegistroEmocion, RegistroHabito, Diario, NotaPsicologo
from .serializers import (
    EmocionSerializer, RegistroEmocionSerializer,
    AlumnoResumenSerializer, PerfilSerializer,
    RegistroHabitoSerializer, DiarioSerializer,
    NotaPsicologoSerializer,
)
from .serializers_auth import EmailTokenObtainPairSerializer


class EmocionViewSet(viewsets.ModelViewSet):
    queryset = Emocion.objects.all()
    serializer_class = EmocionSerializer


class RegistroEmocionViewSet(viewsets.ModelViewSet):
    queryset = RegistroEmocion.objects.all()
    serializer_class = RegistroEmocionSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class AlumnoListView(generics.ListAPIView):
    serializer_class = AlumnoResumenSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Usuario.objects.filter(
            is_staff=False,
            is_superuser=False
        ).select_related('perfil').order_by('perfil__apellido')


class AlumnoPerfilView(generics.RetrieveAPIView):
    serializer_class = PerfilSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        return generics.get_object_or_404(Perfil, usuario__id=self.kwargs['pk'])


class AlumnoEmocionesView(generics.ListAPIView):
    serializer_class = RegistroEmocionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return RegistroEmocion.objects.filter(
            usuario__id=self.kwargs['pk']
        ).select_related('emocion').order_by('-fecha')


class AlumnoHabitosView(generics.ListAPIView):
    serializer_class = RegistroHabitoSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return RegistroHabito.objects.filter(
            usuario__id=self.kwargs['pk']
        ).select_related('habito').order_by('-fecha')


class AlumnoDiarioView(generics.ListAPIView):
    serializer_class = DiarioSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Diario.objects.filter(
            usuario__id=self.kwargs['pk']
        ).order_by('-fecha')


class AlumnoNotasView(generics.ListCreateAPIView):
    serializer_class = NotaPsicologoSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return NotaPsicologo.objects.filter(
            alumno__id=self.kwargs['pk']
        ).order_by('-fecha')

    def perform_create(self, serializer):
        alumno = generics.get_object_or_404(Usuario, id=self.kwargs['pk'])
        serializer.save(alumno=alumno, psicologo=self.request.user)






