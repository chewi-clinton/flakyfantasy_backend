from rest_framework import serializers
from .models import (
    AdminUser, Category, ProductLabel, Product, ProductImage,
    DiscountCode, ProductDiscount, Order, OrderItem, Service, Notification
)

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone']
        read_only_fields = ['id']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']

class ProductLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLabel
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    labels = ProductLabelSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        labels = validated_data.pop('labels', [])
        
        product = Product.objects.create(**validated_data)
        
        if labels:
            product.labels.set(labels)
        
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        
        return product
    
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        labels = validated_data.pop('labels', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if labels is not None:
            instance.labels.set(labels)
        
        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)
        
        return instance
    
    def validate(self, data):
        uploaded_images = data.get('uploaded_images', [])
        product = self.instance
        
        if product:
            current_images = product.images.count()
            total_images = current_images + len(uploaded_images)
        else:
            total_images = len(uploaded_images)
        
        if total_images < 1:
            raise serializers.ValidationError("Product must have at least one image.")
        if total_images > 5:
            raise serializers.ValidationError("Product can have at most five images.")
        
        return data

class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'

class ProductDiscountSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductDiscount
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)
    related_order_number = serializers.CharField(source='related_order.order_number', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'