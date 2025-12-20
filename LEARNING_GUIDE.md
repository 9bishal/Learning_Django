# Django E-Commerce Application - Quick Start Guide

## What We've Built So Far ✅

1. **Product Model** - Database structure for products
2. **Product Display** - Shows all products in carousel on homepage
3. **Navigation** - Navbar with links to different pages
4. **Bootstrap Styling** - Professional look and feel
5. **Comments & Documentation** - Explained every line of code

---

## 🎯 What You're Learning

### Concept 1: MTV Architecture
```
Request from Browser
        ↓
    URL Router (urls.py) - "Which view should handle this?"
        ↓
    View Function (views.py) - "Get data and prepare response"
        ↓
    Model/Database (models.py) - "Get product data"
        ↓
    Template (index.html) - "Display the HTML to user"
        ↓
    Browser Shows Page to User
```

### Concept 2: How a Request Flows

When user visits `http://localhost:8000/shop/`:

1. Django checks `urls.py` for matching pattern
2. Finds: `path('', views.index, name='shop-index')`
3. Calls: `index(request)` function in `views.py`
4. Function does: `Product.objects.all()` - gets data from database
5. Renders: `shop/index.html` with product data
6. Browser displays the HTML page

### Concept 3: Database Queries (ORM)

Instead of writing SQL:
```sql
SELECT * FROM product WHERE price < 100;
```

Django lets you write Python:
```python
cheap_products = Product.objects.filter(price__lt=100)
```

---

## 📋 Key Interview Questions & Answers

### Q1: What's the difference between a Django Project and Django App?
**A:** 
- **Project**: The entire website (e.g., "myawesomecart")
- **App**: A modular component (e.g., "shop", "blog", "accounts")
- One project can have many apps

### Q2: What does `models.py` do?
**A:** Defines database table structures using Python classes. Django converts models to database tables automatically.

### Q3: What is the purpose of migrations?
**A:** Migrations are version control for your database schema.
- `makemigrations` - Creates migration files based on model changes
- `migrate` - Applies migrations to actual database 

### Q4: Explain ForeignKey
**A:** Links two models together. One-to-Many relationship.
```python
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
```
Means: One customer can have many orders.

### Q5: What does `{% %}` mean in templates?
**A:** Django template tags for logic:
- `{% for %}` - Loop
- `{% if %}` - Condition
- `{% load %}` - Load template tag library
- `{% block %}` - Define replaceable section

### Q6: What does `{{ }}` mean in templates?
**A:** Display Python variables in HTML:
```html
<h1>{{ product.product_name }}</h1>
<!-- Shows product name here -->
```

### Q7: What's the benefit of template inheritance?
**A:** Reduces code duplication. Define common HTML (navbar, footer) once in base template, all other templates use it.

### Q8: How do you pass data from view to template?
**A:** Using context dictionary:
```python
context = {'products': products, 'total': 100}
return render(request, 'shop/index.html', context)
```

### Q9: What is `QuerySet`?
**A:** List-like object returned by database queries. Examples:
- `Product.objects.all()` - Returns QuerySet
- `Product.objects.filter(price=100)` - Returns QuerySet
- Can chain multiple filters

### Q10: How does Django protect against SQL Injection?
**A:** Django uses parameterized queries with the ORM, never concatenates user input directly into SQL.

---

## 🔄 Common Tasks & How To Do Them

### Task 1: Display a Single Product
**View:**
```python
def product_detail(request, product_id):
    product = Product.objects.get(product_id=product_id)
    return render(request, 'product_detail.html', {'product': product})
```

**URL:**
```python
path('product/<int:product_id>/', views.product_detail)
```

**Template:**
```html
<h1>{{ product.product_name }}</h1>
<p>Price: ${{ product.price }}</p>
<img src="{{ product.image.url }}" alt="{{ product.product_name }}">
```

### Task 2: Filter Products by Category
**View:**
```python
def electronics(request):
    products = Product.objects.filter(category="Electronics")
    return render(request, 'products.html', {'products': products})
```

### Task 3: Search Products
**View:**
```python
def search(request):
    query = request.GET.get('q', '')  # Get search term from URL
    if query:
        products = Product.objects.filter(
            product_name__icontains=query  # Case-insensitive search
        )
    else:
        products = []
    return render(request, 'search.html', {'products': products, 'query': query})
```

**HTML Form:**
```html
<form method="GET" action="/shop/search/">
    <input type="text" name="q" placeholder="Search products">
    <button type="submit">Search</button>
</form>
```

### Task 4: Sort Products
**View:**
```python
# Newest first
products = Product.objects.order_by('-pub_date')

# Most expensive first
products = Product.objects.order_by('-price')

# Alphabetically
products = Product.objects.order_by('product_name')
```

### Task 5: Limit Results
**View:**
```python
# Get top 5 newest products
top_products = Product.objects.order_by('-pub_date')[:5]

# Get products 10-20
page_2 = Product.objects.all()[10:20]
```

---

## ⚠️ Common Mistakes & How to Fix Them

### Mistake 1: Using `=` instead of `==` in filter
❌ Wrong:
```python
Product.objects.filter(price = 100)
```

✅ Correct:
```python
Product.objects.filter(price=100)
```

### Mistake 2: Forgetting `auto_now_add=True`
❌ This will cause errors:
```python
created_at = models.DateTimeField()  # You must provide date
```

✅ Correct:
```python
created_at = models.DateTimeField(auto_now_add=True)  # Auto set when created
```

### Mistake 3: Not calling `.all()` or `.get()`
❌ Wrong:
```python
products = Product.objects  # Returns manager object, not products
for product in products:
    print(product)  # Error!
```

✅ Correct:
```python
products = Product.objects.all()  # Returns QuerySet
for product in products:
    print(product)  # Works!
```

### Mistake 4: Template variable name doesn't match
❌ View sends `products` but template looks for `items`:
```python
return render(request, 'index.html', {'products': products})
```
```html
{% for item in items %}  ❌ Won't work
```

✅ Match the names:
```html
{% for product in products %}  ✅ Works
```

### Mistake 5: Not running migrations
```bash
python manage.py makemigrations  # Must run this first
python manage.py migrate          # Then run this
```

---

## 🏗️ Next Features to Build

### Feature 1: Shopping Cart
**What to add:**
- Cart model to store items
- Add to cart button
- Cart page showing all items
- Increase/decrease quantity
- Remove item button

**Database tables needed:**
```
Cart (id, user_id, created_date)
CartItem (id, cart_id, product_id, quantity)
```

### Feature 2: User Authentication
**What to build:**
- Register page (create new user)
- Login page (authenticate user)
- Logout functionality
- Protected pages (only logged-in users can checkout)

**Use Django's built-in User model:**
```python
from django.contrib.auth.models import User
```

### Feature 3: Order Management
**What to implement:**
- Checkout page
- Order confirmation
- Order history page
- Order status tracking

**New models:**
```
Order (id, user, total_price, status, created_date)
OrderItem (id, order, product, quantity, price)
```

### Feature 4: Payment Integration
**Third-party services:**
- Stripe (credit cards)
- PayPal (PayPal accounts)
- Razorpay (India-based)

### Feature 5: Admin Features
**For store owners:**
- Add/edit/delete products
- View orders
- Manage inventory
- Sales reports

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                        │
└────────────┬────────────────────────────────────────────┘
             │ GET /shop/
             ▼
┌─────────────────────────────────────────────────────────┐
│              Django URL Router (urls.py)               │
│  Matches: path('', views.index, name='shop-index')    │
└────────────┬────────────────────────────────────────────┘
             │ Calls index(request)
             ▼
┌─────────────────────────────────────────────────────────┐
│               View Function (views.py)                 │
│  - Receives request from user                         │
│  - Gets data from database                           │
│  - Prepares context dictionary                       │
└────────────┬────────────────────────────────────────────┘
             │ products = Product.objects.all()
             ▼
┌─────────────────────────────────────────────────────────┐
│          Database (SQLite / PostgreSQL)                │
│  Returns: All products from product table             │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│            Template Engine (templates)                  │
│  - Receives context: {'products': [Product, ...]}    │
│  - Renders HTML with product data                    │
└────────────┬────────────────────────────────────────────┘
             │ HTML Page
             ▼
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                        │
│  Displays: Products with images and prices           │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Development Workflow

Every time you add a feature:

1. **Design Database**
   - Create/modify models in `models.py`

2. **Create Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create View Function**
   - Write logic in `views.py`

4. **Add URL Pattern**
   - Add route in `urls.py`

5. **Create Template**
   - Write HTML in `templates/`

6. **Test**
   - Run server and test in browser
   - Check Django debug messages

7. **Register in Admin** (if needed)
   - Add model to `admin.py`

---

## 💡 Learning Tips

1. **Read error messages carefully** - They usually tell you exactly what's wrong
2. **Use `print()` statements** - Debug by printing variables in views
3. **Use Django Shell** - Test database queries interactively:
   ```bash
   python manage.py shell
   >>> from shop.models import Product
   >>> products = Product.objects.all()
   >>> print(products)
   ```
4. **Check Django documentation** - It's excellent and always helpful
5. **Build small features first** - Don't try to build everything at once
6. **Ask questions** - Learning is about asking and experimenting

---

## 📚 Useful Links

- Django Official Docs: https://docs.djangoproject.com/
- Django Models: https://docs.djangoproject.com/en/stable/topics/db/models/
- Django QuerySet API: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- Bootstrap 4 Docs: https://getbootstrap.com/docs/4.0/
- Pillow (for images): https://python-pillow.org/

---

**Remember: Every expert was once a beginner. Keep practicing and learning! 🎓**
