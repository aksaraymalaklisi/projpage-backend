from rest_framework.routers import DefaultRouter
from django.conf import settings
from .views import TrackViewSet

router = DefaultRouter()
router.register(r'tracks', TrackViewSet)

if not settings.DEBUG:
    router.include_root_view = False

urlpatterns = router.urls