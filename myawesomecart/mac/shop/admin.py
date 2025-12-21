"""
Django Admin Configuration
==========================
This file customizes how models appear in Django Admin interface.
"""

from django.contrib import admin
from .models import Product, Order, OrderItem, Cart


# ============================================
# PRODUCT ADMIN
# ============================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Customize Product display in admin"""
    list_display = ['product_id', 'product_name', 'category', 'price', 'pub_date']
    list_display_links = ['product_name']
    list_filter = ['category', 'pub_date']
    search_fields = ['product_name', 'category']
    ordering = ['-pub_date']


# ============================================
# CART ADMIN
# ============================================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Customize Cart display in admin - View user shopping carts"""
    list_display = ['user', 'product', 'quantity', 'date_added', 'get_total_price']
    list_filter = ['date_added', 'user']
    search_fields = ['user__username', 'product__product_name']
    readonly_fields = ['date_added', 'get_total_price']
    
    def get_total_price(self, obj):
        """Display total price for this cart item"""
        return f"₹{obj.get_total_price()}"
    get_total_price.short_description = "Total Price"


# ============================================
# ORDER ADMIN
# ============================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Customize Order display in admin"""
    list_display = ['order_id', 'customer_name', 'email', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['customer_name', 'email', 'order_id']
    readonly_fields = ['order_id', 'order_date']


# ============================================
# ORDER ITEM ADMIN
# ============================================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Customize OrderItem display in admin"""
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__order_date']
    search_fields = ['product__product_name', 'order__order_id']