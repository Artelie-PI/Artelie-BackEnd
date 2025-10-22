from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from uploader.router import router as uploader_router
from rest_framework.routers import DefaultRouter
from artelie.views import (
    BrandViewSet, CategoryViewSet, UserViewSet, AddressViewSet,
    SupplierViewSet, ProfileView, ProductViewSet, OrderViewSet,
    CartViewSet, CartItemViewSet, ReviewViewSet
)
from artelie.views.register import RegisterView
from artelie.views.email_verification import EmailVerificationView, ResendVerificationEmailView
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()

router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'users', UserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include(router.urls)),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="user_profile"),
    path('register/', RegisterView.as_view(), name='register'),
    path('api/verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('api/resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path("api/media/", include(uploader_router.urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)