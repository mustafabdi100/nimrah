# admin.py

from django.contrib import admin
from .models import Category, Product, ProductSize, Order, OrderItem,ProductImage

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_price', 'size')
    list_filter = ('category', 'uncategorized')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSizeInline, ProductImageInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'image', 'description')
        }),
        ('Single Size Product', {
            'fields': ('price', 'size'),
            'classes': ('collapse',),
            'description': "Only fill these if the product comes in a single size. Otherwise, use the 'Product Sizes' section below."
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'product_size', 'quantity', 'price')
    can_delete = False
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('total_price', 'shipping_price', 'created_at')
    fieldsets = (
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Shipping Address', {
            'fields': ('street_address_1', 'street_address_2', 'city', 'state_county')
        }),
        ('Order Details', {
            'fields': ('order_notes', 'total_price', 'shipping_price', 'created_at')
        }),
    )
    inlines = [OrderItemInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
