from django.contrib import admin
from .models import (
    EstadoAnimo,
    TipoHabito,
    Habito
)

admin.site.register(EstadoAnimo)
admin.site.register(TipoHabito)
admin.site.register(Habito)
