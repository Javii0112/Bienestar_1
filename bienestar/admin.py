from django.contrib import admin
from .models import (
    Emocion,
    TipoHabito,
    Habito
)

admin.site.register(Emocion)
admin.site.register(TipoHabito)
admin.site.register(Habito)
