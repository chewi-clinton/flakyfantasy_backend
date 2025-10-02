from django.contrib import admin
from .models import (
    AdminUser, Category, ProductLabel, Product, ProductImage,
    DiscountCode, ProductDiscount, Order, OrderItem, Service, Notification
)

from django.contrib.auth.admin import UserAdmin
admin.site.register(AdminUser, UserAdmin)

admin.site.register(Category)
admin.site.register(ProductLabel)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(DiscountCode)
admin.site.register(ProductDiscount)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Service)
admin.site.register(Notification)