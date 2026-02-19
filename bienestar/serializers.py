from rest_framework import serializers
from .models import Emocion, RegistroEmocion


class EmocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emocion
        fields = "__all__"


class RegistroEmocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroEmocion
        fields = "__all__"
