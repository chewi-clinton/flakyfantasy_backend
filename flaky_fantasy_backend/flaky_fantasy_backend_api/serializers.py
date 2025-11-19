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
    
    
    image_files = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    primary_image_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'labels', 
            'stock_quantity', 'in_stock', 'created_at', 'updated_at',
            'images', 'category_name', 'image_files', 'primary_image_id'
        ]
        read_only_fields = ('created_at', 'updated_at', 'in_stock')
    
    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        primary_image_id = validated_data.pop('primary_image_id', None)
        labels = validated_data.pop('labels', [])
        
        product = Product.objects.create(**validated_data)
        
        if labels:
            product.labels.set(labels)
        
        # Create product images
        for i, image_file in enumerate(image_files):
            is_primary = (i == 0) if primary_image_id is None else False
            image = ProductImage.objects.create(
                product=product, 
                image=image_file,
                is_primary=is_primary
            )
            if image.id == primary_image_id:
                image.is_primary = True
                image.save()
        
        # If primary_image_id is specified, set that image as primary
        if primary_image_id and primary_image_id != image.id:
            try:
                primary_image = product.images.get(id=primary_image_id)
                # Reset all images to non-primary first
                product.images.update(is_primary=False)
                primary_image.is_primary = True
                primary_image.save()
            except ProductImage.DoesNotExist:
                pass
        
        return product
    
    def update(self, instance, validated_data):
        image_files = validated_data.pop('image_files', [])
        primary_image_id = validated_data.pop('primary_image_id', None)
        labels = validated_data.pop('labels', None)
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update labels if provided
        if labels is not None:
            instance.labels.set(labels)
        
        # Add new images if provided
        for image_file in image_files:
            ProductImage.objects.create(
                product=instance, 
                image=image_file,
                is_primary=False
            )
        
        # Set primary image if specified
        if primary_image_id is not None:
            try:
                primary_image = instance.images.get(id=primary_image_id)
                # Reset all images to non-primary first
                instance.images.update(is_primary=False)
                primary_image.is_primary = True
                primary_image.save()
            except ProductImage.DoesNotExist:
                pass
        
        return instance
    
    def validate(self, data):
        image_files = data.get('image_files', [])
        product = self.instance
        
        # For new products, require at least one image
        if not product and not image_files:
            raise serializers.ValidationError("Product must have at least one image.")
        
        # For existing products, check if there would be at least one image after update
        if product:
            current_images = product.images.count()
            total_images = current_images + len(image_files)
            if total_images < 1:
                raise serializers.ValidationError("Product must have at least one image.")
            if total_images > 5:
                raise serializers.ValidationError("Product can have at most five images.")
        else:
            if len(image_files) > 5:
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

class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    database = serializers.CharField(required=False)
    message = serializers.CharField(required=False)