from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.forms.models import BaseInlineFormSet
from .models import (
    AdminUser, Category, ProductLabel, Product, ProductImage,
    DiscountCode, ProductDiscount, Order, OrderItem, Service, Notification
)

from django.contrib.auth.admin import UserAdmin
admin.site.register(AdminUser, UserAdmin)
admin.site.register(Category)
admin.site.register(ProductLabel)
admin.site.register(DiscountCode)
admin.site.register(ProductDiscount)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Service)
admin.site.register(Notification)

# Custom formset to validate image count
class ProductImageFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        # Count non-deleted forms with image data
        count = 0
        for form in self.forms:
            # Check if the form has image data and is not marked for deletion
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('image'):
                    count += 1
        
        # Validate count
        if count < 1:
            raise forms.ValidationError("Product must have at least one image.")
        if count > 5:
            raise forms.ValidationError("Product can have at most five images.")

# Custom ProductImage inline to show image preview
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    formset = ProductImageFormSet
    extra = 3  # Number of empty image upload fields to show
    fields = ('image_preview', 'image', 'alt_text', 'is_primary')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.id and obj.image:
            return format_html('<img src="{}" width="100" height="100" />'.format(obj.image.url))
        return "Upload an image"
    image_preview.short_description = 'Preview'

# Custom Product admin with image upload in the same form
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'in_stock', 'created_at')
    list_filter = ('category', 'in_stock', 'labels')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price', 'category')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'labels')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Ensure at least one image is marked as primary
        if obj.pk:  # Only if the product is saved
            images = obj.images.all()
            if images and not images.filter(is_primary=True).exists():
                # If no primary image is set, make the first one primary
                first_image = images.first()
                if first_image:
                    first_image.is_primary = True
                    first_image.save()
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ProductImage) and not instance.pk:
                instance.product = form.instance  # Set the product for new images
            instance.save()
        formset.save_m2m()