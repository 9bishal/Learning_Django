"""
Shop Application Models
=======================
Models are Python classes that define the structure of database tables.
Each model = one table, each field = one column
"""

from django.db import models
from django.contrib.auth.models import User


# ============================================
# PRODUCT MODEL
# ============================================
class Product(models.Model):
    """
    Represents a product in the e-commerce store.
    
    This model stores all information about products that customers can buy.
    Each instance of this model is one row in the 'shop_product' table.
    """
    
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images", default="")
    
    def __str__(self):
        return self.product_name
    
    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Product"
        verbose_name_plural = "Products"


# ============================================
# CART MODEL
# ============================================
class Cart(models.Model):
    """
    Represents items in a user's shopping cart.
    
    Each Cart record = one item in the user's cart
    When user adds product → new Cart row created
    When user increases qty → quantity field updated
    When user decreases qty to 0 → row deleted
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} (qty: {self.quantity})"
    
    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ['user', 'product']
        
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.product.price * self.quantity


# ============================================
# USER PROFILE MODEL
# ============================================
class UserProfile(models.Model):
    """
    Extended user profile to store additional user information
    
    Why? Django's built-in User model doesn't have phone, address, etc.
    This model extends User with extra fields.
    
    Relationship: One User → One UserProfile (One-to-One)
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, blank=True, default="India")
    profile_picture = models.ImageField(upload_to="shop/profile_pics", default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        verbose_name_plural = "User Profiles"


# ============================================
# ADDRESS MODEL
# ============================================
class Address(models.Model):
    """
    Stores multiple addresses for a user.
    
    Relationship: One User → Many Addresses (One-to-Many)
    
    Why? Users might have multiple delivery addresses
    This model allows saving multiple addresses and selecting one at checkout
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    
    address_type = models.CharField(
        max_length=20,
        choices=[
            ('home', 'Home'),
            ('work', 'Work'),
            ('other', 'Other')
        ],
        default='home'
    )
    
    street_address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="India")
    phone = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street_address}, {self.city} - {self.user.username}"
    
    class Meta:
        verbose_name_plural = "Addresses"


# ============================================
# ORDER MODEL
# ============================================
class Order(models.Model):
    """
    Store completed orders for order history
    
    Relationship: One User → Many Orders (One-to-Many)
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Order details
    order_id = models.CharField(max_length=100, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, default='Credit Card')
    
    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Orders"


# ============================================
# ORDER ITEM MODEL
# ============================================
class OrderItem(models.Model):
    """
    Individual items in an order
    
    Relationship: One Order → Many OrderItems
    
    Example: Order #123 has:
    - OrderItem 1: Laptop x1
    - OrderItem 2: Mouse x2
    """
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.product_name} in Order {self.order.order_id}"
    
    def get_total(self):
        """Calculate total for this item"""
        return self.quantity * self.price
