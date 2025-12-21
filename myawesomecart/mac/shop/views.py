"""
Shop Application Views
======================
This module contains all view functions for the shop application.
Views are Python functions that receive a web request and return a web response.
"""

from math import ceil
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Cart
from django.contrib.auth.models import User


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_cart_count(user):
    """
    Helper function to get total items in cart for a user
    
    Usage: cart_count = get_cart_count(request.user)
    """
    if user.is_authenticated:
        return Cart.objects.filter(user=user).count()
    return 0


# ============================================
# PRODUCT LISTING VIEW
# ============================================
def index(request):
    """
    Display all products on the home page with carousel pagination.
    
    Context Variables:
    - products: All products from database
    - no_of_slides: Number of carousel slides needed (groups of 4 products)
    - range: Range object for template iteration
    - cart_count: Number of items in user's shopping cart (shows in navbar)
    
    Explanation:
    Each carousel slide shows 4 products in a row.
    We calculate how many slides needed using: nslides = n//4 + ceil((n/4)-(n//4))
    Example: 12 products → 3 slides (4 products each)
    """
    products = Product.objects.all()
    print(products)
    n = len(products)
    nslides = n // 4 + ceil((n / 4) - (n // 4))
    cart_count = get_cart_count(request.user)
    
    params = {
        'no_of_slides': nslides,
        'range': range(nslides),
        'products': products,
        'cart_count': cart_count
    }
    
    return render(request, "shop/index.html", params)


# ============================================
# ABOUT PAGE VIEW
# ============================================
def about(request):
    """Display the about page."""
    cart_count = get_cart_count(request.user)
    return render(request, 'shop/about.html', {'cart_count': cart_count})


# ============================================
# CONTACT PAGE VIEW
# ============================================
def contact(request):
    """Display contact page with contact form."""
    cart_count = get_cart_count(request.user)
    
    if request.method == 'POST':
        pass
    
    return render(request, 'shop/contact.html', {'cart_count': cart_count})


# ============================================
# ORDER TRACKING VIEW
# ============================================
def tracker(request):
    """Track user orders by order ID."""
    cart_count = get_cart_count(request.user)
    
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
    
    return render(request, 'shop/tracker.html', {'cart_count': cart_count})


# ============================================
# SEARCH VIEW
# ============================================
def search(request):
    """Search for products by name or category."""
    cart_count = get_cart_count(request.user)
    return render(request, 'shop/search.html', {'cart_count': cart_count})


# ============================================
# PRODUCT DETAIL VIEW
# ============================================
def productview(request):
    """Display details of a single product."""
    cart_count = get_cart_count(request.user)
    return HttpResponse("This is product view page")


# ============================================
# CHECKOUT VIEW
# ============================================
def checkout(request):
    """Handle checkout process."""
    cart_count = get_cart_count(request.user)
    return HttpResponse("This is checkout page")


# ============================================
# SHOPPING CART VIEWS
# ============================================

@login_required(login_url='/admin/login/')
def add_to_cart(request, product_id):
    """Add product to cart or increase quantity if already exists"""
    try:
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
        
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    except Product.DoesNotExist:
        return redirect('/shop/')


@login_required(login_url='/admin/login/')
def view_cart(request):
    """Display all items in user's shopping cart"""
    cart_items = Cart.objects.filter(user=request.user)
    
    total_price = 0
    for item in cart_items:
        total_price += item.get_total_price()
    
    cart_count = cart_items.count()
    
    params = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': cart_count
    }
    
    return render(request, 'shop/cart.html', params)


@login_required(login_url='/admin/login/')
def increase_qty(request, cart_id):
    """Increase quantity of item in cart by 1"""
    try:
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        cart_item.quantity += 1
        cart_item.save()
    
    except Cart.DoesNotExist:
        pass
    
    return redirect('/shop/cart/')


@login_required(login_url='/admin/login/')
def decrease_qty(request, cart_id):
    """Decrease quantity of item in cart by 1"""
    try:
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    
    except Cart.DoesNotExist:
        pass
    
    return redirect('/shop/cart/')


@login_required(login_url='/admin/login/')
def delete_from_cart(request, cart_id):
    """Remove item from cart completely"""
    try:
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        cart_item.delete()
    
    except Cart.DoesNotExist:
        pass
    
    return redirect('/shop/cart/')


# ============================================
# USER REGISTRATION VIEW
# ============================================
def register(request):
    """User registration/signup page"""
    if request.user.is_authenticated:
        return redirect('/shop/profile/')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account created successfully.")
            return redirect('/shop/profile/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    cart_count = get_cart_count(request.user)
    return render(request, 'shop/register.html', {
        'form': form,
        'cart_count': cart_count
    })


# ============================================
# USER LOGIN VIEW
# ============================================
def user_login(request):
    """User login page"""
    if request.user.is_authenticated:
        return redirect('/shop/profile/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', '/shop/profile/')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password!")
    
    cart_count = get_cart_count(request.user)
    return render(request, 'shop/login.html', {'cart_count': cart_count})


# ============================================
# USER LOGOUT VIEW
# ============================================
def user_logout(request):
    """Log user out"""
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('/shop/')


# ============================================
# USER PROFILE VIEW
# ============================================
@login_required(login_url='/shop/login/')
def profile(request):
    """Display and edit user profile"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('/shop/profile/')
    else:
        form = UserProfileForm(instance=user_profile)
    
    cart_count = get_cart_count(request.user)
    
    return render(request, 'shop/profile.html', {
        'form': form,
        'addresses': addresses,
        'cart_count': cart_count
    })


# ============================================
# ADD ADDRESS VIEW
# ============================================
@login_required(login_url='/shop/login/')
def add_address(request):
    """Add a new delivery address"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect('/shop/profile/')
    else:
        form = AddressForm()
    
    cart_count = get_cart_count(request.user)
    
    return render(request, 'shop/add_address.html', {
        'form': form,
        'cart_count': cart_count
    })


# ============================================
# EDIT ADDRESS VIEW
# ============================================
@login_required(login_url='/shop/login/')
def edit_address(request, address_id):
    """Edit an existing address"""
    try:
        address = Address.objects.get(id=address_id, user=request.user)
    except Address.DoesNotExist:
        messages.error(request, "Address not found!")
        return redirect('/shop/profile/')
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully!")
            return redirect('/shop/profile/')
    else:
        form = AddressForm(instance=address)
    
    cart_count = get_cart_count(request.user)
    
    return render(request, 'shop/edit_address.html', {
        'form': form,
        'address': address,
        'cart_count': cart_count
    })


# ============================================
# DELETE ADDRESS VIEW
# ============================================
@login_required(login_url='/shop/login/')
def delete_address(request, address_id):
    """Delete an address"""
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        address.delete()
        messages.success(request, "Address deleted successfully!")
    except Address.DoesNotExist:
        messages.error(request, "Address not found!")
    
    return redirect('/shop/profile/')


# ============================================
# ORDER HISTORY VIEW
# ============================================
@login_required(login_url='/shop/login/')
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    cart_count = get_cart_count(request.user)
    
    return render(request, 'shop/order_history.html', {
        'orders': orders,
        'cart_count': cart_count
    })


# ============================================
# ORDER DETAIL VIEW
# ============================================
@login_required(login_url='/shop/login/')
def order_detail(request, order_id):
    """Display details of a specific order"""
    try:
        order = Order.objects.get(order_id=order_id, user=request.user)
        order_items = order.order_items.all()
    except Order.DoesNotExist:
        messages.error(request, "Order not found!")
        return redirect('/shop/order_history/')
    
    cart_count = get_cart_count(request.user)
    
    return render(request, 'shop/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'cart_count': cart_count
    })
