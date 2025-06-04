from rest_framework.routers import DefaultRouter
from django.conf import settings
from .views import TrackViewSet, UserRegisterViewSet, UserViewSet, RatingViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include

router = DefaultRouter()
router.register(r'tracks', TrackViewSet)
router.register(r'users', UserViewSet, basename='user')
router.register(r'register', UserRegisterViewSet, basename='register')
router.register(r'ratings', RatingViewSet, basename='rating')

if not settings.DEBUG:
    router.include_root_view = False

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]