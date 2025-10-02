from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AdminLoginView, AdminProfileView,
    ProductViewSet, CategoryViewSet, ProductLabelViewSet,
    DiscountCodeViewSet, ProductDiscountViewSet,
    OrderViewSet, OrderItemViewSet,
    ServiceViewSet,
    NotificationViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'product-labels', ProductLabelViewSet)
router.register(r'discount-codes', DiscountCodeViewSet)
router.register(r'product-discounts', ProductDiscountViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('auth/login/', AdminLoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', AdminProfileView.as_view()),
    path('', include(router.urls)),
]