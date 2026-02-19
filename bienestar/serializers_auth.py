from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # Aquí simplemente dejamos que SimpleJWT maneje todo
        data = super().validate({
            "email": attrs.get("email"),
            "password": attrs.get("password"),
        })

        return data