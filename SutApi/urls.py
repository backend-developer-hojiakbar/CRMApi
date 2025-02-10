from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from all.views import UserViewSet, OmborViewSet, KategoriyaViewSet, BirlikViewSet, MahsulotViewSet, PurchaseViewSet, PurchaseItemViewSet, SotuvViewSet, SotuvItemViewSet, PaymentViewSet, sotuv_hisoboti, xarid_hisoboti, ombor_hisoboti, LoginAPIView, LogoutAPIView, TokenAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="CRM API",
        default_version='v1',
        description="Mall official site description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'omborlar', OmborViewSet)
router.register(r'kategoriyalar', KategoriyaViewSet)
router.register(r'birliklar', BirlikViewSet)
router.register(r'mahsulotlar', MahsulotViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'purchaseitems', PurchaseItemViewSet)
router.register(r'sotuvlar', SotuvViewSet)
router.register(r'sotuvitems', SotuvItemViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('sotuv-hisoboti/', sotuv_hisoboti, name='sotuv_hisoboti'),
    path('xarid-hisoboti/', xarid_hisoboti, name='xarid_hisoboti'),
    path('ombor-hisoboti/', ombor_hisoboti, name='ombor_hisoboti'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/', TokenAPIView.as_view(), name='token_obtain_pair'),
]
app_name = 'all'
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)