# E-Commerce Application - Complete Guide

## Project Overview
This is a Django-based e-commerce application called "My Awesome Cart" where users can browse products, add them to cart, and checkout.

---

## 📁 Project Structure

```
myawesomecart/mac/
├── db.sqlite3              # SQLite database
├── manage.py               # Django management script
├── shop/                   # Main app for products
│   ├── models.py           # Database models (Product, Order, etc.)
│   ├── views.py            # Views to handle requests
│   ├── urls.py             # URL routing for shop app
│   ├── admin.py            # Django admin configuration
│   ├── templates/shop/     # HTML templates for shop
│   │   ├── basic.html      # Base template (navbar, footer)
│   │   └── index.html      # Product listing page
│   └── static/shop/        # Static files (CSS, JS, images)
└── mac/                    # Main project settings
    ├── settings.py         # Configuration (DB, apps, middleware)
    ├── urls.py             # Main URL routing
    └── wsgi.py             # WSGI configuration for deployment
```

---

## 🏗️ Key Concepts

### 1. **Django Models** (Database)
Models define the structure of your database tables.

**Current Product Model:**
```python
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)#ensure unique id
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images", default="")
```

**What each field does:**
- `AutoField`: Automatically incrementing primary key
- `CharField`: Text field with maximum length
- `IntegerField`: Whole numbers
- `DateField`: Date values
- `ImageField`: For uploading product images

### 2. **Django Views** (Business Logic)
Views process user requests and return responses.

**Example View:**
```python
# shop/views.py
from django.shortcuts import render
from .models import Product

def index(request):
    # Fetch all products from database
    products = Product.objects.all()
    # Pass products to template
    return render(request, "shop/index.html", {'products': products})
```

### 3. **URL Routing** (Navigation)
Maps URLs to views.

**Example URL Pattern:**
```python
# shop/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='shop-index'),  # http://localhost:8000/shop/
    path('about', views.about, name='shop-about'),  # http://localhost:8000/shop/about
]
```

### 4. **Templates** (HTML)
Django templates allow dynamic HTML with Python-like syntax.

**Example Template:**
```html
{% extends 'shop/basic.html' %}  <!-- Inherit from base template -->

{% block body %}
    {% for product in products %}  <!-- Loop through products -->
        <h3>{{ product.product_name }}</h3>  <!-- Display product name -->
        <p>Price: ${{ product.price }}</p>
    {% endfor %}
{% endblock %}
```

---

## 🔧 How to Build E-Commerce Features

### Feature 1: Product Listing (Already Done)
✅ Display all products with images and prices

### Feature 2: Product Details Page (To Build)
Show detailed information about a single product.

```python
# In views.py
def productview(request, id):
    product = Product.objects.filter(product_id=id).first()
    return render(request, 'shop/productdetail.html', {'product': product})

# In urls.py
path('product/<int:id>', views.productview, name='product-detail'),
```

### Feature 3: Shopping Cart (To Build)
Store selected products for checkout.

```python
# Models to add:
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    order_date = models.DateField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)#means if order deleted, items deleted
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
```

### Feature 4: User Authentication (To Build)
Allow users to register and login.

```python
# Use Django's built-in User model
from django.contrib.auth.models import User

# Create login view
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('shop-index')
    return render(request, 'shop/login.html')
```

---

## 🎓 Interview Questions for Beginners

### Django Basics
1. **What is Django?**
   - A Python web framework that follows the MTV (Model-Template-View) pattern
   - Provides built-in admin, authentication, and ORM

2. **Explain MVT Architecture:**
   - **Model**: Database schema (models.py)
   - **View**: Logic to process requests (views.py)
   - **Template**: HTML to display data (templates/)

3. **What is an ORM (Object-Relational Mapping)?**
   - Allows you to interact with database using Python objects instead of SQL
   - `Product.objects.all()` instead of SQL queries

4. **Difference between CharField and TextField?**
   - CharField: Limited length (max_length required)
   - TextField: Unlimited length, better for large text

### Database & Models
5. **What is a primary key?**
   - Unique identifier for each record
   - AutoField automatically generates sequential numbers (1, 2, 3...)

6. **What is a ForeignKey?**
   - Links two models together
   - Example: Order linked to Customer (one customer has many orders)

7. **What does `on_delete=models.CASCADE` mean?**
   - If parent record is deleted, all related child records are deleted too

### Views & URLs
8. **What is the difference between a view and a template?**
   - View: Python function that processes logic
   - Template: HTML that displays the result

9. **How does URL routing work?**
   - Django matches URL patterns in urls.py to views
   - When user visits URL, Django calls the corresponding view function

10. **What does `render()` do?**
    - Takes template name and context (data) dictionary
    - Returns HTML with data inserted into template

### Templates
11. **What are Django template tags?**
    - `{% %}` - for logic (if, for, etc.)
    - `{{ }}` - for displaying variables
    - Example: `{% for product in products %}` and `{{ product.name }}`

12. **What is template inheritance?**
    - Child templates extend parent templates using `{% extends %}`
    - Reuse common HTML (navbar, footer) across pages

### E-Commerce Specific
13. **How would you implement a shopping cart?**
    - Store cart in session: `request.session['cart']`
    - Or in database: create Order and OrderItem models

14. **How to handle payments?**
    - Use third-party services: Stripe, PayPal, Razorpay
    - Never store sensitive payment info in your database

15. **How to secure your e-commerce site?**
    - Use HTTPS for all transactions
    - Validate all user inputs
    - Use CSRF tokens (Django includes this)
    - Hash passwords (Django does this automatically)

---

## 📝 Common Code Patterns

### Pattern 1: List All Objects
```python
# View
products = Product.objects.all()

# Template
{% for product in products %}
    {{ product.product_name }}
{% endfor %}
```

### Pattern 2: Get Single Object
```python
# View
product = Product.objects.filter(product_id=5).first()
# or
product = Product.objects.get(product_id=5)

# Template
{{ product.product_name }}
```

### Pattern 3: Filter Objects
```python
# Get products in category "Electronics"
electronics = Product.objects.filter(category="Electronics")
 
# Get products priced under 100
cheap_products = Product.objects.filter(price__lt=100)

# Get products with name containing "phone"
phones = Product.objects.filter(product_name__icontains="phone")
```

### Pattern 4: Order Objects
```python
# Get newest products first
products = Product.objects.order_by('-pub_date')

# Alphabetically
products = Product.objects.order_by('product_name')
```

### Pattern 5: Count Objects
```python
total_products = Product.objects.count()
```

---

## 🚀 Step-by-Step Building Features

### Step 1: Update Product Model (Add more fields)
```python
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    price = models.IntegerField()
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images")
    quantity = models.IntegerField(default=0)  # NEW: Track stock
    rating = models.FloatField(default=0)      # NEW: Product rating
    
    def __str__(self):
        return self.product_name  # Show this in admin
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Register Model in Admin
```python
# shop/admin.py
from django.contrib import admin
from .models import Product

@admin.register(Product) #dictates admin site to manage Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'category', 'quantity']
    list_filter = ['category']
    search_fields = ['product_name']
```

### Step 4: Create Views for CRUD (Create, Read, Update, Delete)
```python
# shop/views.py

# READ - List all products
def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

# READ - Single product
def product_detail(request, id):
    product = Product.objects.get(product_id=id)
    return render(request, 'shop/product_detail.html', {'product': product})

# CREATE - Add new product (admin only)
def create_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        Product.objects.create(
            product_name=name,
            price=int(price)
        )
        return redirect('product-list')
    return render(request, 'shop/create_product.html')

# UPDATE - Edit product
def update_product(request, id):
    product = Product.objects.get(product_id=id)
    if request.method == 'POST':
        product.product_name = request.POST.get('name')
        product.price = int(request.POST.get('price'))
        product.save()
        return redirect('product-detail', id=id)
    return render(request, 'shop/edit_product.html', {'product': product})

# DELETE - Remove product
def delete_product(request, id):
    product = Product.objects.get(product_id=id)
    product.delete()
    return redirect('product-list')
```

---

## 🛡️ Best Practices

1. **Always validate user input**
   ```python
   if not request.POST.get('email'):
       return HttpResponse("Email is required")
   ```

2. **Use Django Forms instead of manual HTML forms**
   ```python
   from django import forms
   class ProductForm(forms.ModelForm):
       class Meta:
           model = Product
           fields = ['product_name', 'price', 'category']
   ```

3. **Protect sensitive views with decorators**
   ```python
   from django.contrib.auth.decorators import login_required
   
   @login_required
   def checkout(request):
       # Only logged-in users can access this
       pass
   ```

4. **Use Django QuerySet efficiently**
   ```python
   # BAD: 100 database queries
   for product in Product.objects.all():
       print(product.category.name)
   
   # GOOD: 1 database query
   products = Product.objects.select_related('category')
   ```

5. **Always use HTTPS in production**
6. **Keep SECRET_KEY secret** (use environment variables)
7. **Use database transactions for important operations**
   ```python
   from django.db import transaction
   
   @transaction.atomic
   def create_order(request):
       # If any error occurs, entire transaction rolls back
       pass
   ```

---

## 📚 Learning Resources

- Django Official Docs: https://docs.djangoproject.com/
- Django ORM QuerySet: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- Bootstrap for styling: https://getbootstrap.com/docs/

---

## 💡 Next Steps

1. ✅ Build Product Listing (DONE)
2. 🔄 Add Product Details Page
3. 🔄 Implement Shopping Cart
4. 🔄 Create Order System
5. 🔄 Add User Authentication
6. 🔄 Implement Payment Gateway
7. 🔄 Add Search & Filters
8. 🔄 Deploy to Production

---

**Happy Learning! Ask questions and experiment with the code!**
