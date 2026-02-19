from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Perfil
from datetime import date
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import re
from .models import (
    Habito,
    RegistroEmocion,
    RegistroHabito,
    Diario,
    Emocion
)

User = get_user_model()

def registro_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        email = request.POST.get("email")
        password1 = request.POST.get("password")
        password2 = request.POST.get("password2")
        genero = request.POST.get("genero")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")

        # Validaciones
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

        # Crear usuario
        user = User.objects.create_user(
            email=email,
            password=password1,
            first_name=nombre,
            last_name=apellido
        )

        Perfil.objects.create(
            usuario=user,
            genero=genero,
            fecha_nacimiento=fecha_nac
        )

        login(request, user)
        messages.success(request, "Usuario registrado correctamente")
        return redirect("login")

    return render(request, "registro.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Correo o contraseña incorrectos")

    return render(request, "login.html")

@login_required
def dashboard_view(request):
    # Obtener emociones desde la BD (o usar datos de ejemplo si no tienes BD)
    emociones = Emocion.objects.all()
    
    # Si no tienes BD aún, usa esto temporalmente:
    # emociones = [
    #     {'id': 1, 'nombre': 'Feliz'},
    #     {'id': 2, 'nombre': 'Triste'},
    #     {'id': 3, 'nombre': 'Emocionado/a'},
    #     {'id': 4, 'nombre': 'Angustiado/a'},
    #     {'id': 5, 'nombre': 'Decepcionado/a'},
    #     {'id': 6, 'nombre': 'Extraño/a'},
    # ]

    if request.method == "POST":
        # ===============================
        # GUARDAR EMOCIÓN
        # ===============================
        if "guardar_emocion" in request.POST:
            emocion_id = request.POST.get("emocion")
            intensidad = request.POST.get("intensidad")
            comentario = request.POST.get("comentario", "")

            # Validaciones
            if not emocion_id or emocion_id == "":
                messages.error(request, "Por favor selecciona una emoción")
            elif not intensidad or intensidad == "":
                messages.error(request, "Por favor selecciona una intensidad")
            else:
                try:
                    # Descomentar cuando tengas BD lista:
                    RegistroEmocion.objects.create(
                        usuario=request.user,
                        emocion_id=int(emocion_id),
                        intensidad=int(intensidad),
                        comentario=comentario
                    )
                    messages.success(request, "¡Emoción registrada exitosamente! 💚")
                    
                    # Para modo demo sin BD:
                    # messages.info(request, "Modo demo - La emoción no se guardó (sin BD)")
                    
                except Exception as e:
                    messages.error(request, f"Error al guardar: {str(e)}")

            return redirect("dashboard")

    return render(request, "dashboard.html", {
        "emociones": emociones,
    })

@login_required
def registro_habitos(request):
    habitos = Habito.objects.all()

    if request.method == "POST":
        habito_id = request.POST.get("habito")
        valor = request.POST.get("valor")

        if habito_id and valor:
            habito = Habito.objects.filter(id=habito_id).first()

            if habito:
                RegistroHabito.objects.create(
                    usuario=request.user,
                    habito=habito,
                    fecha=date.today(),
                    valor=int(valor)
                )

        return redirect("registro_habitos")

    return render(request, "habitos.html", {
        "habitos": habitos
    })

@login_required
def estadistica_view(request):
    return render(request, "estadistica.html")


@login_required
def recursos_view(request):
    return render(request, "recursos.html")


@login_required
def diario(request):
    if request.method == 'POST':
        texto = request.POST.get('contenido')

        if texto:
            Diario.objects.create(
                usuario=request.user,
                contenido=texto
            )
            return redirect('diario')  # vuelve al diario

    return render(request, 'diario.html')


@login_required
def perfil(request):
    return render(request, 'perfil.html')

#api rest
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmocionSerializer, RegistroEmocionSerializer
from .models import Emocion, RegistroEmocion
from .serializers_auth import EmailTokenObtainPairSerializer

class EmocionViewSet(viewsets.ModelViewSet):
    queryset = Emocion.objects.all()
    serializer_class = EmocionSerializer


class RegistroEmocionViewSet(viewsets.ModelViewSet):
    queryset = RegistroEmocion.objects.all()
    serializer_class = RegistroEmocionSerializer

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer