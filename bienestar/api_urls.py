from rest_framework.routers import DefaultRouter
from .views import EmocionViewSet, RegistroEmocionViewSet

router = DefaultRouter()
router.register(r'emociones', EmocionViewSet)
router.register(r'registros', RegistroEmocionViewSet)

urlpatterns = router.urls
