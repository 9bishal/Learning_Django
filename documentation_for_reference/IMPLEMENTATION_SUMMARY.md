# Django E-Commerce Application - Complete Implementation Summary

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Database Models & Relationships](#database-models--relationships)
4. [Forms Implementation](#forms-implementation)
5. [Views Implementation](#views-implementation)
6. [Templates Implementation](#templates-implementation)
7. [URL Routing](#url-routing)
8. [Key Features Added](#key-features-added)
9. [Interview Questions & Answers](#interview-questions--answers)

---

## 🎯 Project Overview

### What Was Built
A complete Django e-commerce application with user authentication, product shopping cart, and user profile management.

### Main Tasks Completed
1. **User Authentication System** - Login, Registration, Logout
2. **Shopping Cart** - Add/Remove/Update products
3. **User Profile Management** - Edit profile, manage addresses
4. **Responsive Navbar** - With search, cart badge, and profile dropdown
5. **Order Management** - Order history and order details tracking
6. **Form Validation** - Custom validation for all user inputs

---

## 🔧 Technology Stack

### Backend
- **Framework**: Django 5.2.7
- **Database**: SQLite3
- **Python Version**: 3.12.2
- **ORM**: Django ORM (Object-Relational Mapping)

### Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 4.2.1
- **JavaScript**: jQuery 3.3.1
- **Icons**: Unicode Emojis (🛒, 👤, 📝, 🔐, etc.)

### Dependencies
```
Django==5.2.7
Python==3.12.2
SQLite3 (built-in)
```

---

## 🗄️ Database Models & Relationships

### 1. **User Model** (Django Built-in)
```
User (from django.contrib.auth.models)
├── id (Primary Key - Auto-generated)
├── username (CharField, unique)
├── email (EmailField)
├── password (hashed)
├── first_name (CharField)
├── last_name (CharField)
└── is_authenticated (Boolean)
```

### 2. **UserProfile Model** (Custom)
```
UserProfile
├── id (Primary Key - AutoField)
├── user (ForeignKey → User) ⭐ ONE-TO-ONE Relationship
├── phone (CharField)
├── address (TextField)
├── city (CharField)
├── state (CharField)
├── pincode (CharField)
├── country (CharField)
└── created_at (DateTimeField)
```

**Relationship Explanation:**
```
User (1) -------- (1) UserProfile
  |                     |
  ├─ id: 1         ├─ user_id: 1 (Foreign Key)
  └─ username      └─ phone, address, etc.
```

### 3. **Product Model** (Custom)
```
Product
├── id (Primary Key - AutoField)
├── product_id (CharField, unique)
├── product_name (CharField)
├── desc (TextField)
├── price (IntegerField)
├── category (CharField)
└── image (ImageField)
```

### 4. **Cart Model** (Custom)
```
Cart
├── id (Primary Key - AutoField)
├── user (ForeignKey → User) ⭐ MANY-TO-ONE Relationship
├── product (ForeignKey → Product) ⭐ MANY-TO-ONE Relationship
└── quantity (IntegerField)
```

**Relationship Diagram:**
```
       User (1) -------- (*) Cart
         |                  |
         |                  └─── user_id (Foreign Key)
         |
    UserProfile


      Product (1) -------- (*) Cart
                              |
                              └─── product_id (Foreign Key)
```

**Example Data:**
```
User Table:
| id | username | email          |
|----|----------|----------------|
| 1  | john_doe | john@email.com |
| 2  | jane_doe | jane@email.com |

Product Table:
| id | product_name | price |
|----|--------------|-------|
| 1  | Laptop       | 50000 |
| 2  | Phone        | 20000 |

Cart Table:
| id | user_id | product_id | quantity |
|----|---------|-----------|----------|
| 1  | 1       | 1         | 2        | ← John has 2 Laptops
| 2  | 1       | 2         | 1        | ← John has 1 Phone
| 3  | 2       | 1         | 1        | ← Jane has 1 Laptop
```

### 5. **Address Model** (Custom)
```
Address
├── id (Primary Key - AutoField)
├── user (ForeignKey → User) ⭐ MANY-TO-ONE Relationship
├── address_type (CharField - "Home" or "Office")
├── street_address (CharField)
├── city (CharField)
├── state (CharField)
├── pincode (CharField)
├── country (CharField)
├── phone (CharField)
└── is_default (BooleanField)
```

### 6. **Order Model** (Custom)
```
Order
├── id (Primary Key - AutoField)
├── order_id (CharField, unique - UUID)
├── user (ForeignKey → User) ⭐ MANY-TO-ONE Relationship
├── total_price (IntegerField)
├── status (CharField - "Pending", "Shipped", etc.)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

### 7. **OrderItem Model** (Custom)
```
OrderItem
├── id (Primary Key - AutoField)
├── order (ForeignKey → Order) ⭐ MANY-TO-ONE Relationship
├── product (ForeignKey → Product) ⭐ MANY-TO-ONE Relationship
├── quantity (IntegerField)
└── price (IntegerField - price at time of order)
```

**Complete Relationship Picture:**
```
┌─────────────────────────────────────────────────────────────┐
│                        USER (1)                              │
│ ├─ id (PK)                                                   │
│ ├─ username, email, password                                 │
│ └─ first_name, last_name                                     │
└───────┬──────────────────────────────────────────────────────┘
        │
        ├──────────── (1-1) ────────── UserProfile
        │                              ├─ id (PK)
        │                              ├─ user_id (FK) ⭐
        │                              └─ phone, address, etc.
        │
        ├──────────── (1-M) ────────── Cart
        │                              ├─ id (PK)
        │                              ├─ user_id (FK) ⭐
        │                              ├─ product_id (FK) ⭐
        │                              └─ quantity
        │
        ├──────────── (1-M) ────────── Address
        │                              ├─ id (PK)
        │                              ├─ user_id (FK) ⭐
        │                              └─ street_address, etc.
        │
        └──────────── (1-M) ────────── Order
                                       ├─ id (PK)
                                       ├─ order_id (unique)
                                       ├─ user_id (FK) ⭐
                                       ├─ total_price
                                       └─ status

        PRODUCT (1) ──────────── (M) ────────── Cart
                                                ├─ product_id (FK) ⭐
                                                └─ quantity

        ORDER (1) ──────────── (M) ────────── OrderItem
                                             ├─ order_id (FK) ⭐
                                             ├─ product_id (FK) ⭐
                                             └─ quantity, price
```

### Primary Keys vs Foreign Keys

**Primary Key (PK)**
- Unique identifier for each record
- Cannot be NULL
- Each table has exactly ONE primary key
- Example: `id` in User model

**Foreign Key (FK)**
- References the PRIMARY KEY of another table
- Creates relationship between tables
- Can be NULL (optional relationship)
- Multiple records can share same FK value
- Example: `user_id` in Cart model references `User.id`

**Visual Example:**
```
User Table (Primary Key highlighted)
┌────────┬──────────────┐
│ id ⭐  │ username     │  ← 'id' is PRIMARY KEY
├────────┼──────────────┤
│ 1      │ john_doe     │
│ 2      │ jane_smith   │
└────────┴──────────────┘

Cart Table (Foreign Key highlighted)
┌────┬──────────┬──────────────┬──────────┐
│ id │ user_id  │ product_id   │ quantity │
│    │ (FK) ⭐  │ (FK) ⭐      │          │
├────┼──────────┼──────────────┼──────────┤
│ 1  │ 1 ─────► │ 1            │ 2        │
│ 2  │ 1 ─────► │ 2            │ 1        │
│ 3  │ 2 ─────► │ 1            │ 1        │
└────┴──────────┴──────────────┴──────────┘
     │
     └─ Points to User.id = 1 (john_doe)
```

---

## 📝 Forms Implementation

### 1. **UserLoginForm** (Custom Form)
```python
class UserLoginForm(forms.Form):
    username = CharField(max_length=100)
    password = CharField(widget=PasswordInput)
```

**Fields:**
- `username` - CharField
- `password` - CharField with PasswordInput widget

**Purpose:** Authenticate user login

---

### 2. **UserRegistrationForm** (ModelForm)
```python
class UserRegistrationForm(forms.ModelForm):
    password = CharField(widget=PasswordInput)
    password2 = CharField(widget=PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email']
```

**Fields:**
- `username` - CharField (from User model)
- `email` - EmailField (from User model)
- `password` - CharField (custom)
- `password2` - CharField (custom, for confirmation)

**Validations:**
- Check if passwords match
- Check if username is unique
- Check if email is unique

---

### 3. **UserProfileForm** (ModelForm)
```python
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'state', 'pincode', 'country']
```

**Fields:**
- `phone` - CharField
- `address` - TextField
- `city` - CharField
- `state` - CharField
- `pincode` - CharField
- `country` - CharField

**Purpose:** Update user profile information

---

### 4. **AddressForm** (ModelForm)
```python
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_type', 'street_address', 'city', 'state', 
                 'pincode', 'country', 'phone']
```

**Fields:**
- `address_type` - Select field ("Home" or "Office")
- `street_address` - CharField
- `city`, `state`, `pincode`, `country` - CharField
- `phone` - CharField

**Purpose:** Add/Edit delivery addresses

---

## 🔄 Views Implementation

### View Function Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   DJANGO VIEWS                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌────────────────────────────────────────────────────┐ │
│ │ PUBLIC VIEWS (No Login Required)                   │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ 1. index() → Homepage with products                │ │
│ │ 2. about() → About page                            │ │
│ │ 3. contact() → Contact page                        │ │
│ │ 4. search() → Product search                       │ │
│ │ 5. user_login() → Login form + authentication      │ │
│ │ 6. register() → Registration form + user creation  │ │
│ │ 7. user_logout() → Logout user                     │ │
│ │ 8. tracker() → Order tracking                      │ │
│ │ 9. productview() → Product details                 │ │
│ │ 10. checkout() → Checkout page                     │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ ┌────────────────────────────────────────────────────┐ │
│ │ PROTECTED VIEWS (Login Required)                   │ │
│ │ @login_required decorator                          │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ 1. add_to_cart() → Add product to cart             │ │
│ │ 2. view_cart() → Display cart items                │ │
│ │ 3. increase_qty() → Increase quantity              │ │
│ │ 4. decrease_qty() → Decrease quantity              │ │
│ │ 5. delete_from_cart() → Remove from cart           │ │
│ │ 6. profile() → User profile page                   │ │
│ │ 7. add_address() → Add new address                 │ │
│ │ 8. edit_address() → Edit existing address          │ │
│ │ 9. delete_address() → Remove address               │ │
│ │ 10. order_history() → Show all orders              │ │
│ │ 11. order_detail() → Show order details            │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Views Explained

#### 1. **register(request)** - User Registration
```python
def register(request):
    if request.method == 'POST':
        form = forms.UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('/shop/profile/')
```

**Flow:**
1. User submits form with username, email, password
2. Form validates all fields
3. Create User object (don't save yet)
4. Hash password using `set_password()`
5. Save User to database
6. Create UserProfile for this user
7. Log user in automatically
8. Redirect to profile page

**Data Flow:**
```
User Input → Form Validation → User Object
         → Password Hashing → Save to DB
         → Create UserProfile → Auto Login
         → Redirect to Profile
```

#### 2. **user_login(request)** - User Login
```python
def user_login(request):
    if request.method == 'POST':
        form = forms.UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/shop/profile/')
```

**Flow:**
1. User submits username and password
2. Form validates
3. `authenticate()` checks credentials against database
4. If valid, create session
5. Redirect to profile

#### 3. **add_to_cart(request, product_id)** - Add Product to Cart
```python
def add_to_cart(request, product_id):
    product = Product.objects.get(product_id=product_id)
    cart_item = Cart.objects.filter(user=request.user, product=product).first()
    
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(
            user=request.user,
            product=product,
            quantity=1
        )
```

**Database Operations:**
```
Before:
Cart table is empty for this user

After (first time):
INSERT INTO shop_cart (user_id, product_id, quantity)
VALUES (1, 5, 1)

After (second time - same product):
UPDATE shop_cart SET quantity = 2
WHERE user_id = 1 AND product_id = 5
```

#### 4. **view_cart(request)** - Display Cart
```python
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
```

**Database Query:**
```sql
SELECT * FROM shop_cart WHERE user_id = 1
```

#### 5. **profile(request)** - User Profile Page
```python
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
```

**Relationships in Action:**
```
1 User → 1 UserProfile (one-to-one)
1 User → M Address (one-to-many)
1 User → M Order (one-to-many)
```

---

## 🎨 Templates Implementation

### Base Template Structure
```html
base.html
├── Head Section
│   ├── Meta tags
│   ├── Bootstrap CSS
│   └── Custom CSS
├── Body Section
│   ├── Navbar
│   │   ├── Brand/Logo
│   │   ├── Search Bar
│   │   ├── Navigation Links
│   │   ├── Cart Badge (shows count)
│   │   ├── Profile Dropdown (if logged in)
│   │   └── Login/Register Links (if anonymous)
│   ├── {% block body %} Content
│   └── Footer
└── JavaScript
    ├── jQuery
    ├── Bootstrap JS
    └── Custom JS
```

### Key Templates Created

#### 1. **login.html**
```html
<form method="post">
    {% csrf_token %}
    <input type="text" name="username" placeholder="Enter your username">
    <input type="password" name="password" placeholder="Enter your password">
    <button type="submit">Login</button>
</form>
```

**Features:**
- CSRF protection token
- Username input field
- Password input field
- Error display
- Link to register page

#### 2. **register.html**
```html
<form method="post">
    {% csrf_token %}
    <input type="text" name="username" placeholder="Choose a username">
    <input type="email" name="email" placeholder="Enter your email">
    <input type="password" name="password" placeholder="Enter password">
    <input type="password" name="password2" placeholder="Confirm password">
    <button type="submit">Register</button>
</form>
```

**Features:**
- Username field
- Email field
- Password field
- Confirm password field
- Validation errors display

#### 3. **base.html - Navbar**
```html
<nav class="navbar">
    <!-- Logo/Brand -->
    <a href="/">🛒 My Awesome Cart</a>
    
    <!-- Search Bar -->
    <form action="/shop/search/">
        <input type="search" name="query" placeholder="Search products...">
        <button type="submit">Search</button>
    </form>
    
    <!-- Cart -->
    <a href="/shop/cart/">
        🛒 Cart
        {% if cart_count > 0 %}
            <span class="badge">{{ cart_count }}</span>
        {% endif %}
    </a>
    
    <!-- Profile Dropdown (if authenticated) -->
    {% if user.is_authenticated %}
        <div class="dropdown">
            <a href="#">👤 {{ user.username }}</a>
            <div class="dropdown-menu">
                <a href="/shop/profile/">📋 My Profile</a>
                <a href="/shop/order-history/">📦 Order History</a>
                <a href="/shop/logout/">🚪 Logout</a>
            </div>
        </div>
    {% else %}
        <a href="/shop/login/">🔐 Login</a>
        <a href="/shop/register/">📝 Register</a>
    {% endif %}
</nav>
```

---

## 🌐 URL Routing

### URL Configuration

```python
# /shop/urls.py

urlpatterns = [
    # Public Pages
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="About Us"),
    path("contact/", views.contact, name="Contact Us"),
    path("search/", views.search, name="search"),
    
    # Authentication
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    
    # Cart Management
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path("increase-qty/<int:cart_id>/", views.increase_qty, name="increase_qty"),
    path("decrease-qty/<int:cart_id>/", views.decrease_qty, name="decrease_qty"),
    path("delete-from-cart/<int:cart_id>/", views.delete_from_cart, name="delete_from_cart"),
    
    # User Profile
    path("profile/", views.profile, name="profile"),
    path("add-address/", views.add_address, name="add_address"),
    path("edit-address/<int:address_id>/", views.edit_address, name="edit_address"),
    path("delete-address/<int:address_id>/", views.delete_address, name="delete_address"),
    
    # Orders
    path("order-history/", views.order_history, name="order_history"),
    path("order/<str:order_id>/", views.order_detail, name="order_detail"),
]
```

### Request-Response Flow

```
User Request
    ↓
URL Router (/shop/login/)
    ↓
View Function (user_login)
    ↓
Form Processing
    ↓
Database Query (authenticate user)
    ↓
Template Rendering (login.html)
    ↓
HTML Response to Browser
```

---

## ✨ Key Features Added

### 1. User Authentication System
- ✅ User Registration with validation
- ✅ User Login with password verification
- ✅ User Logout
- ✅ Session management
- ✅ Login-required protection on views

### 2. Shopping Cart
- ✅ Add products to cart
- ✅ View cart items
- ✅ Increase/Decrease quantity
- ✅ Remove items from cart
- ✅ Cart count badge in navbar

### 3. User Profile
- ✅ View user profile
- ✅ Edit profile information
- ✅ Manage multiple addresses
- ✅ View order history
- ✅ View order details

### 4. Responsive Navbar
- ✅ Site title/logo (clickable)
- ✅ Search bar
- ✅ Home link
- ✅ Cart with badge count
- ✅ Profile dropdown (logged-in users)
- ✅ Login/Register links (anonymous users)
- ✅ Logout option

### 5. Form Validation
- ✅ Username uniqueness check
- ✅ Email uniqueness check
- ✅ Password matching validation
- ✅ Email format validation
- ✅ Required field validation
- ✅ Bootstrap styling
- ✅ Error message display

### 6. Data Relationships
- ✅ One-to-One: User ↔ UserProfile
- ✅ One-to-Many: User → Cart
- ✅ One-to-Many: User → Address
- ✅ One-to-Many: User → Order
- ✅ Many-to-Many: Cart connects User & Product

---

## 📚 Interview Questions & Answers

### Database & ORM Questions

#### Q1: What is a Foreign Key? Explain with an example.
**Answer:**
A Foreign Key is a column that references the Primary Key of another table, establishing a relationship between tables.

**Example:**
```
Cart table has user_id which references User.id
- Cart.user_id (Foreign Key) → User.id (Primary Key)
- This means each cart item belongs to exactly one user
- Multiple cart items can belong to the same user (One-to-Many)
```

---

#### Q2: Explain the difference between Primary Key and Foreign Key.
**Answer:**
| Feature | Primary Key | Foreign Key |
|---------|------------|------------|
| Purpose | Uniquely identifies a record | References a record in another table |
| Uniqueness | Must be unique | Can be duplicated |
| Null Values | Cannot be NULL | Can be NULL (optional) |
| Per Table | Exactly one per table | Can be multiple per table |
| Constraint | UNIQUE + NOT NULL | References PK of another table |

**Example:**
```
User Table:
id (PK) - unique, cannot be null

Cart Table:
user_id (FK) - references User.id, can be duplicated
```

---

#### Q3: What is Django ORM? How does it work?
**Answer:**
Django ORM (Object-Relational Mapping) is a tool that allows you to interact with databases using Python code instead of SQL.

**How it works:**
```python
# Without ORM (Raw SQL)
cursor.execute("SELECT * FROM user WHERE username = 'john'")
user = cursor.fetchone()

# With Django ORM (Pythonic)
user = User.objects.get(username='john')

# Benefits:
# 1. No SQL injection vulnerability
# 2. Database-agnostic
# 3. Readable Python code
# 4. Automatic escaping
```

---

#### Q4: Explain One-to-Many relationship with example.
**Answer:**
One-to-Many (1-M) relationship means one record in table A can have multiple related records in table B.

**Example: User → Cart**
```
One User can have Many Cart items
One User can have Many Orders
One User can have Many Addresses

Database Representation:
User (1) ──────────── (*) Cart
┌──────┐              ┌────────────┐
│ id   │◄─────────────│ user_id    │
│ 1    │              │ 1, 1, 2    │
│ 2    │              │ (duplicated)│
└──────┘              └────────────┘

Django Model:
class Cart(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    # This creates the 1-M relationship
```

---

#### Q5: How do you query related objects in Django?
**Answer:**
```python
# Get all carts for a user
user = User.objects.get(id=1)
carts = Cart.objects.filter(user=user)
# OR
carts = user.cart_set.all()

# Get cart details with related product
cart = Cart.objects.select_related('product').get(id=1)

# Get user with all related data
user = User.objects.prefetch_related('cart_set', 'address_set').get(id=1)
```

---

### Views & Logic Questions

#### Q6: What is @login_required decorator? Why is it used?
**Answer:**
`@login_required` is a Django decorator that restricts access to a view to authenticated users only.

**How it works:**
```python
@login_required(login_url='/shop/login/')
def add_to_cart(request, product_id):
    # If user not authenticated, redirect to login page
    # If authenticated, execute view
    pass

# What happens:
1. Anonymous user tries to access /shop/add-to-cart/1/
2. @login_required checks if user.is_authenticated
3. If False → Redirect to /shop/login/
4. If True → Execute view
```

**Benefits:**
- Security: Prevents unauthorized access
- User experience: Clear redirect to login
- Code cleanliness: Single decorator vs manual checks

---

#### Q7: Explain the registration flow step-by-step.
**Answer:**
```
1. User visits /shop/register/
   ↓
2. GET request → render register.html with empty form
   ↓
3. User fills form (username, email, password, password2)
   ↓
4. User clicks Submit → POST request
   ↓
5. Form validation in register view:
   - Check username doesn't exist
   - Check email doesn't exist
   - Check passwords match
   ↓
6. If valid:
   a. Create User object (commit=False)
   b. Hash password using set_password()
   c. Save User to database
   d. Create UserProfile (linked via ForeignKey)
   e. Create session (login automatically)
   f. Redirect to /shop/profile/
   ↓
7. If invalid:
   - Display error messages
   - Re-render form with errors
```

---

#### Q8: What's the difference between form.save() and form.save(commit=False)?
**Answer:**
```python
# form.save() - Saves immediately
form.save()
# Directly saves to database
# Returns the saved object

# form.save(commit=False) - Don't save yet
user = form.save(commit=False)
# Returns object but doesn't save to DB
# Allows modification before saving
user.is_active = True  # Modify
user.save()            # Now save

# Use case in registration:
user = form.save(commit=False)
user.set_password(form.cleaned_data['password'])  # Hash password
user.save()  # Save hashed version
```

---

#### Q9: How does authentication work in Django?
**Answer:**
```python
from django.contrib.auth import authenticate, login

# Step 1: Get credentials from form
username = form.cleaned_data.get('username')
password = form.cleaned_data.get('password')

# Step 2: Authenticate
user = authenticate(request, username=username, password=password)

# Step 3: Check if valid
if user is not None:
    # Step 4: Create session
    login(request, user)
    # Step 5: Session cookie sent to browser
    # Step 6: Subsequent requests include session ID
else:
    # Authentication failed
    error = "Invalid credentials"

# Behind the scenes:
# authenticate() → Hashes provided password
#              → Compares with stored hash
#              → Returns User object if match
#              → Returns None if no match
```

---

### Models & Relationships Questions

#### Q10: Explain the UserProfile model and why it's needed.
**Answer:**
**Why create UserProfile separately from User?**

```python
# Option 1: Store everything in User (Bad)
class User:
    username
    email
    phone          # ❌ Not in built-in User model
    address        # ❌ Not in built-in User model
    
# Problems:
# - Changes to built-in User model are risky
# - Adds fields only e-commerce needs
# - Hard to maintain

# Option 2: Separate UserProfile (Good)
class User:  # Built-in Django model
    username
    email
    password

class UserProfile:  # Custom model
    user = ForeignKey(User)  # One-to-One relationship
    phone
    address
    city
    country

# Benefits:
# 1. Separation of concerns
# 2. Can extend without modifying User
# 3. Clear structure
# 4. Easy to understand
```

**One-to-One Relationship:**
```python
# Each User has exactly one UserProfile
# Each UserProfile belongs to exactly one User

user = User.objects.get(id=1)
profile = user.userprofile  # Access related profile
# OR
profile = UserProfile.objects.get(user=user)
```

---

#### Q11: What happens when you delete a User? Explain on_delete=models.CASCADE.
**Answer:**
`on_delete=models.CASCADE` specifies what to do when referenced record is deleted.

**Options:**
```python
# CASCADE - Delete related records too
class Cart(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)

# If User is deleted:
DELETE User WHERE id=1
→ All Cart records with user_id=1 are deleted too

# PROTECT - Prevent deletion if related records exist
class Address(models.Model):
    user = ForeignKey(User, on_delete=models.PROTECT)

# If User is deleted and has Address:
→ Django raises ProtectedError
→ User deletion fails

# SET_NULL - Set FK to NULL if record deleted
class Comment(models.Model):
    user = ForeignKey(User, on_delete=models.SET_NULL, null=True)

# If User is deleted:
→ Comment.user_id = NULL
→ Comment still exists but no user

# SET_DEFAULT - Set FK to default value
class Post(models.Model):
    user = ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
```

---

### Forms & Validation Questions

#### Q12: What is form validation in Django? Explain clean_() methods.
**Answer:**
Form validation ensures data is correct before saving to database.

**Types of validation:**
```python
class UserRegistrationForm(forms.ModelForm):
    password = CharField()
    password2 = CharField()
    
    class Meta:
        model = User
        fields = ['username', 'email']
    
    # FIELD-LEVEL VALIDATION (clean_fieldname)
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken!")
        return username
    
    # FORM-LEVEL VALIDATION (clean)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2:
            if password != password2:
                raise ValidationError("Passwords don't match!")
        
        return cleaned_data

# Validation flow:
1. Field validation → clean_fieldname() called
2. Form validation → clean() called
3. If all pass → form.is_valid() returns True
4. If any fail → form.errors dict populated
```

---

#### Q13: What's the difference between Form and ModelForm?
**Answer:**
| Feature | Form | ModelForm |
|---------|------|-----------|
| Purpose | Generic form | Form for Django model |
| Data Source | Manual fields | Auto-generated from model |
| Save | Manual saving | form.save() method |
| Validation | Custom logic | Model validations included |
| Use Case | Contact form, Search | Create/Update model instances |

**Example:**
```python
# Regular Form (no model)
class ContactForm(forms.Form):
    name = CharField()
    email = EmailField()
    message = CharField(widget=Textarea)
    
    # Manual save
    def send_email(self):
        # Custom logic
        send_mail(...)

# ModelForm (linked to model)
class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
    
    # Built-in save
    user = form.save()  # Saves to User model
```

---

### URL Routing Questions

#### Q14: Explain URL patterns with parameters. Give shopping cart example.
**Answer:**
URL parameters allow dynamic URLs based on data.

**Syntax:**
```python
# No parameter
path("", views.index)
# URL: /shop/

# String parameter
path("search/", views.search)
# URL: /shop/search/?query=laptop

# Integer parameter (path converter)
path("add-to-cart/<int:product_id>/", views.add_to_cart)
# URL: /shop/add-to-cart/5/
#      product_id = 5

# Multiple parameters
path("edit-address/<int:user_id>/<int:address_id>/", views.edit_address)
# URL: /shop/edit-address/1/3/
#      user_id = 1, address_id = 3
```

**Shopping Cart Example:**
```python
urlpatterns = [
    path("cart/", views.view_cart),  # View cart
    path("add-to-cart/<int:product_id>/", views.add_to_cart),  # Add specific product
    path("delete-from-cart/<int:cart_id>/", views.delete_from_cart),  # Delete specific item
]

# URLs generated:
/shop/cart/                    → view all cart items
/shop/add-to-cart/5/          → add product 5 to cart
/shop/add-to-cart/10/         → add product 10 to cart
/shop/delete-from-cart/2/     → delete cart item 2
```

---

### Security Questions

#### Q15: Why do we use {% csrf_token %} in forms?
**Answer:**
CSRF (Cross-Site Request Forgery) token prevents unauthorized form submissions.

**Attack scenario:**
```
1. User logs into myawesomecart.com
2. User visits malicious-site.com
3. Malicious site has: <img src="myawesomecart.com/delete-account">
4. Browser automatically sends with user's session
5. Account gets deleted without consent
```

**Protection with CSRF token:**
```html
<!-- Form includes token -->
<form method="post">
    {% csrf_token %}  <!-- Generates unique token -->
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>

<!-- Django checks:
1. Token in cookie
2. Token in form data
3. If don't match → reject request
4. Malicious site doesn't have token → attack fails
```

**How it works:**
```
1. Server generates random token
2. Token sent to browser in cookie AND form
3. When form submitted, browser includes both
4. Server verifies they match
5. If attacker tries, they don't have token
```

---

#### Q16: How does Django secure passwords?
**Answer:**
Django uses PBKDF2 hashing algorithm to secure passwords.

```python
from django.contrib.auth.models import User

# NEVER do this:
user.password = "mypassword123"  # ❌ Storing plain text
user.save()

# DO this:
user.set_password("mypassword123")  # ✅ Hashes password
user.save()

# How hashing works:
1. User enters: "mypassword123"
2. Django applies PBKDF2 algorithm
3. Generates hash: "pbkdf2_sha256$600000$xyz$abc..."
4. Only hash is stored in database
5. Original password never stored

# When user logs in:
1. User enters: "mypassword123"
2. Django hashes provided password
3. Compares hash with stored hash
4. If match → authentication success
```

---

### Performance Questions

#### Q17: What is N+1 query problem? How to solve it?
**Answer:**
N+1 problem occurs when you query related data inefficiently.

**Problem example:**
```python
# ❌ INEFFICIENT (N+1 queries)
users = User.objects.all()  # 1 query
for user in users:
    print(user.userprofile)  # N additional queries (one per user)

# Total: 1 + N queries (if 100 users → 101 queries)

# ✅ EFFICIENT (2 queries)
users = User.objects.select_related('userprofile')
# This uses JOIN to fetch user AND profile in one query

# For multiple related objects:
users = User.objects.prefetch_related('cart_set', 'address_set')
# Fetches users, then carts in batch, then addresses in batch
```

**Performance impact:**
```
# 1000 users, N+1 problem = 1001 database queries ❌
# 1000 users, select_related = 2 database queries ✅
# Speed improvement: 500x faster
```

---

### Testing Questions

#### Q18: How would you test the registration view?
**Answer:**
```python
from django.test import TestCase, Client
from django.contrib.auth.models import User

class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    # Test 1: Can access registration page
    def test_register_page_loads(self):
        response = self.client.get('/shop/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/register.html')
    
    # Test 2: Valid registration creates user
    def test_valid_registration(self):
        response = self.client.post('/shop/register/', {
            'username': 'newuser',
            'email': 'new@email.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    # Test 3: Duplicate username rejected
    def test_duplicate_username(self):
        User.objects.create_user(username='john', email='john@email.com', password='pass')
        response = self.client.post('/shop/register/', {
            'username': 'john',
            'email': 'different@email.com',
            'password': 'pass123',
            'password2': 'pass123'
        })
        self.assertFormError(response, 'form', 'username', 'Username already taken!')
    
    # Test 4: Mismatched passwords rejected
    def test_password_mismatch(self):
        response = self.client.post('/shop/register/', {
            'username': 'user',
            'email': 'user@email.com',
            'password': 'pass123',
            'password2': 'different'
        })
        self.assertFormError(response, 'form', None, 'Passwords don\'t match!')
```

---

## 📊 Tech Stack Summary Table

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | Django | 5.2.7 |
| **Language** | Python | 3.12.2 |
| **Database** | SQLite3 | Built-in |
| **Frontend** | HTML5 | Latest |
| **CSS** | Bootstrap | 4.2.1 |
| **JavaScript** | jQuery | 3.3.1 |
| **ORM** | Django ORM | Built-in |
| **Auth** | Django Auth | Built-in |

---

## 🎓 Summary

### What You've Learned
1. **Database Design** - Primary/Foreign keys, relationships
2. **Django ORM** - QuerySet operations, relationships
3. **User Authentication** - Login, registration, sessions
4. **Form Handling** - Validation, ModelForms, custom validation
5. **Views** - Request-response cycle, decorators
6. **Templates** - Template tags, inheritance
7. **URL Routing** - URL patterns, parameters
8. **Security** - CSRF tokens, password hashing
9. **Best Practices** - Code organization, separation of concerns

### Key Takeaways
- ✅ Foreign Keys establish relationships between models
- ✅ @login_required protects sensitive views
- ✅ Form validation happens before database operations
- ✅ Django ORM prevents SQL injection
- ✅ select_related/prefetch_related solve N+1 queries
- ✅ CSRF tokens prevent unauthorized submissions
- ✅ Password hashing with set_password() is essential

---

**Last Updated:** December 21, 2025
**Django Version:** 5.2.7
**Python Version:** 3.12.2
