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
    
    # PRIMARY KEY - Unique identifier for each product
    # AutoField automatically creates 1, 2, 3, etc.
    product_id = models.AutoField(primary_key=True)
    
    # Product name - Text field with max 50 characters
    # Required field (no default, no null=True)
    product_name = models.CharField(max_length=50)
    
    # Product category - Groups products (Electronics, Clothing, etc.)
    # Has default value of empty string
    category = models.CharField(max_length=50, default="")
    
    # Sub-category - Smaller grouping within category
    # Example: category="Electronics", subcategory="Smartphones"
    subcategory = models.CharField(max_length=50, default="")
    
    # Product price in dollars/cents
    # IntegerField stores whole numbers (100 means $100)
    # Consider using DecimalField for precise pricing
    price = models.IntegerField(default=0)
    
    # Product description - Short text about the product
    # CharField limited to 300 characters
    desc = models.CharField(max_length=300)
    
    # Publication date - When product was added to store
    # DateField stores only date (no time)
    pub_date = models.DateField()
    
    # Product image - File upload field
    # upload_to="shop/images" saves images in media/shop/images/
    # default="" means image is optional
    image = models.ImageField(upload_to="shop/images", default="")
    
    # TODO: Add these fields for better e-commerce functionality:
    # stock = models.IntegerField(default=0)  # Quantity available
    # rating = models.FloatField(default=0)   # Average rating (0-5)
    # is_active = models.BooleanField(default=True)  # Is product available?
    # created_at = models.DateTimeField(auto_now_add=True)  # When created
    # updated_at = models.DateTimeField(auto_now=True)  # Last modified
    
    def __str__(self):
        """
        String representation of product.
        Shows this in Django admin panel instead of "Product object (1)"
        """
        return self.product_name
    
    class Meta:
        """Metadata options for the model"""
        # Display products newest first in admin
        ordering = ['-pub_date']
        # Custom table name (optional)
        # db_table = 'ecommerce_product'
        # Verbose name for admin
        verbose_name = "Product"
        verbose_name_plural = "Products"


# ============================================
# ORDER MODEL (TODO: Implement)
# ============================================
class Order(models.Model):
    """
    Represents a customer order.
    
    This model stores information about orders placed by customers.
    Links to Product through OrderItem (many-to-many relationship)
    """
    
    # Unique order ID
    order_id = models.AutoField(primary_key=True)
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Shipping address
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100, default="")
    state = models.CharField(max_length=100, default="")
    zipcode = models.CharField(max_length=10, default="")
    
    # Order status
    # 'Pending', 'Shipped', 'Delivered', 'Cancelled'
    status = models.CharField(max_length=20, default="Pending")
    
    # Order dates
    order_date = models.DateTimeField(auto_now_add=True)  # Created when order placed
    updated_date = models.DateTimeField(auto_now=True)    # Updated when status changes
    
    # Link to user who placed order (Foreign Key)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Total price of order
    total_price = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Order #{self.order_id} - {self.customer_name}"


# ============================================
# ORDER ITEM MODEL (TODO: Implement)
# ============================================
class OrderItem(models.Model):
    """
    Represents individual items in an order.
    
    One Order can have many OrderItems
    Example: Order #1 contains OrderItem (Product A x2) and OrderItem (Product B x1)
    """
    
    # Foreign Key to Order
    # When order is deleted, all its items are also deleted (CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Foreign Key to Product
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Quantity ordered
    quantity = models.IntegerField(default=1)
    
    # Price paid (might differ from current product price)
    price = models.IntegerField()
    
    def __str__(self):
        return f"{self.product.product_name} (x{self.quantity})"


# ============================================
# USEFUL FIELD TYPES REFERENCE
# ============================================
"""
CharField(max_length=X)        - Short text (name, email, etc.)
TextField()                    - Long text (descriptions, comments)
IntegerField()                 - Whole numbers
FloatField()                   - Decimal numbers
DecimalField(max_digits=10, decimal_places=2) - Money (more precise)
BooleanField()                 - True/False
DateField()                    - Date (2025-12-20)
DateTimeField()                - Date and time (2025-12-20 15:30:45)
EmailField()                   - Email with validation
URLField()                     - URL with validation
ImageField()                   - Image upload
FileField()                    - File upload
ForeignKey()                   - Link to another model (One-to-Many)
ManyToManyField()              - Many-to-Many relationship
"""

# ============================================
# QUERY EXAMPLES
# ============================================
"""
# Get all products
Product.objects.all()

# Get first product
Product.objects.first()

# Get product by ID
Product.objects.get(product_id=5)

# Filter products
Product.objects.filter(category="Electronics")
Product.objects.filter(price__lt=100)  # price less than 100
Product.objects.filter(product_name__icontains="phone")  # contains "phone" (case-insensitive)

# Count
Product.objects.count()

# Order by
Product.objects.order_by('-price')  # newest first (minus sign = descending)

# Get or create
product, created = Product.objects.get_or_create(product_id=5)

# Update
Product.objects.filter(product_id=5).update(price=999)

# Delete
Product.objects.filter(product_id=5).delete()
"""

def __str__(self):
    return self.product_name