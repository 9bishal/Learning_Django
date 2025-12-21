"""
Django Admin Configuration
==========================
This file customizes how models appear in Django Admin interface.
"""

from django.contrib import admin
from .models import Product, Order, OrderItem, Cart, UserProfile, Address


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
# USER PROFILE ADMIN
# ============================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Customize UserProfile display in admin"""
    list_display = ['user', 'phone', 'city', 'state', 'created_at']
    list_filter = ['created_at', 'country']
    search_fields = ['user__username', 'phone', 'city']
    readonly_fields = ['created_at', 'updated_at']


# ============================================
# ADDRESS ADMIN
# ============================================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Customize Address display in admin"""
    list_display = ['user', 'address_type', 'city', 'state', 'is_default']
    list_filter = ['address_type', 'is_default', 'country']
    search_fields = ['user__username', 'city', 'street_address']
    readonly_fields = ['created_at', 'updated_at']


# ============================================
# ORDER ADMIN
# ============================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Customize Order display in admin"""
    list_display = ['order_id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'order_id']
    readonly_fields = ['order_id', 'created_at', 'updated_at']


# ============================================
# ORDER ITEM ADMIN
# ============================================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Customize OrderItem display in admin"""
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__created_at']
    search_fields = ['product__product_name', 'order__order_id']
