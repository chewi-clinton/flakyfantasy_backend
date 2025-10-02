import csv
from django.http import HttpResponse
from rest_framework import viewsets, filters, status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    AdminUser, Category, ProductLabel, Product, ProductImage,
    DiscountCode, ProductDiscount, Order, OrderItem, Service, Notification
)
from .serializers import (
    AdminUserSerializer, CategorySerializer, ProductLabelSerializer, ProductSerializer, ProductImageSerializer,
    DiscountCodeSerializer, ProductDiscountSerializer, OrderSerializer, OrderItemSerializer, ServiceSerializer, NotificationSerializer
)

class AdminLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = AdminUser.objects.get(username=request.data['username'])
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save()
        return Response({
            'access': response.data['access'],
            'refresh': response.data['refresh'],
            'user_id': user.pk,
            'role': user.role
        })

class AdminProfileView(viewsets.generics.RetrieveUpdateAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'in_stock', 'labels']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        product = self.get_object()
        quantity = request.data.get('quantity')
        if quantity is not None:
            product.stock_quantity = quantity
            product.save()
            return Response({'status': 'stock updated'})
        return Response({'error': 'quantity not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def set_primary_image(self, request, pk=None):
        product = self.get_object()
        image_id = request.data.get('image_id')
        
        if not image_id:
            return Response({'error': 'image_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            image = product.images.get(id=image_id)
        except ProductImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
        product.images.update(is_primary=False)
        image.is_primary = True
        image.save()
        
        return Response({'status': 'primary image updated'})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductLabelViewSet(viewsets.ModelViewSet):
    queryset = ProductLabel.objects.all()
    serializer_class = ProductLabelSerializer

class DiscountCodeViewSet(viewsets.ModelViewSet):
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        discount = self.get_object()
        discount.is_active = not discount.is_active
        discount.save()
        return Response({'status': 'discount toggled', 'is_active': discount.is_active})

class ProductDiscountViewSet(viewsets.ModelViewSet):
    queryset = ProductDiscount.objects.all()
    serializer_class = ProductDiscountSerializer
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        discount = self.get_object()
        discount.is_active = not discount.is_active
        discount.save()
        return Response({'status': 'discount toggled', 'is_active': discount.is_active})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'customer_name', 'customer_email']
    ordering_fields = ['created_at', 'total_amount', 'status']
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Customer Name', 'Customer Email', 
            'Status', 'Total Amount', 'Created At'
        ])
        
        orders = Order.objects.all()
        for order in orders:
            writer.writerow([
                order.order_number,
                order.customer_name,
                order.customer_email,
                order.status,
                order.total_amount,
                order.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        return response

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def send_order_alert(self, request):
        order_id = request.data.get('order_id')
        message = request.data.get('message')
        
        if not order_id or not message:
            return Response({'error': 'order_id and message required'}, status=status.HTTP_400_BAD_REQUEST)
        
        admins = AdminUser.objects.filter(is_staff=True)
        notifications = []
        for admin in admins:
            notifications.append(Notification(
                recipient=admin,
                notification_type='order',
                title=f"New Order #{order_id}",
                message=message,
                related_order_id=order_id
            ))
        Notification.objects.bulk_create(notifications)
        
        send_mail(
            subject=f"New Order Received #{order_id}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin.email for admin in admins],
            fail_silently=True,
        )
        
        return Response({'status': 'alerts sent'})