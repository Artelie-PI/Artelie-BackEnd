from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from artelie.views import BrandViewSet

router = DefaultRouter()

router.register(r'brands', BrandViewSet, basename='brand')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]