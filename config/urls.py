from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from artelie.views import BrandViewSet
from artelie.views import CategoryViewSet
from artelie.views import UserViewSet

router = DefaultRouter()

router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include(router.urls)),
]