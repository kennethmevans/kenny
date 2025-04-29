from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ESDocumentViewSet

router = DefaultRouter()
router.register(r'es_api', ESDocumentViewSet, basename='es-document')

urlpatterns = [
    path('', include(router.urls)),
]
