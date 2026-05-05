from django import forms
from .models import Emocion

class EmocionForm(forms.ModelForm):
    class Meta:
        model = Emocion
        fields = ['nombre', 'emoji']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Ej: Feliz'
            }),
            'emoji': forms.TextInput(attrs={
                'class': 'input',
                'id': 'emoji-input',
                'placeholder': 'Selecciona un emoji 😊'
            }),
        }