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
    # Fetch all products from the database using ORM (Object-Relational Mapping)
    # Product.objects.all() returns a QuerySet (list-like object)
    products = Product.objects.all()
    
    # Debug: Print products to console (useful for development)
    print(products)
    
    # Calculate number of products
    n = len(products)
    
    # Calculate number of carousel slides needed (4 products per slide)
    # n//4 = integer division, ceil() = round up
    # Example: 12 products = 12//4 = 3 slides
    nslides = n // 4 + ceil((n / 4) - (n // 4))
    
    # Get cart count for current user (for navbar badge)
    cart_count = get_cart_count(request.user)
    
    # Dictionary of data to pass to template
    params = {
        'no_of_slides': nslides,           # Number of carousel slides
        'range': range(nslides),            # Range object for looping in template
        'products': products,               # All products to display
        'cart_count': cart_count            # Number of items in cart (shows in navbar)
    }
    
    # Render the template with context data
    # render() takes: (request, template_path, context_dictionary)
    return render(request, "shop/index.html", params)


# ============================================
# ABOUT PAGE VIEW
# ============================================
def about(request):
    """
    Display the about page.
    
    Pass cart_count for navbar badge
    """
    cart_count = get_cart_count(request.user)
    return render(request, 'shop/about.html', {'cart_count': cart_count})


# ============================================
# CONTACT PAGE VIEW
# ============================================
def contact(request):
    """
    Display contact page with contact form.
    
    Handles both GET (display form) and POST (process form submission) requests.
    
    POST Parameters:
    - name: User's full name
    - email: User's email address
    - phone: User's phone number (optional)
    - subject: Category of inquiry
    - message: User's message content
    
    TODO: Implement functionality to:
    1. Save contact messages to database (create Contact model)
    2. Send confirmation email to user
    3. Send notification email to admin
    """
    cart_count = get_cart_count(request.user)
    
    if request.method == 'POST':
        # TODO: Process form submission
        # Validate data, save to database, send emails
        pass
    
    return render(request, 'shop/contact.html', {'cart_count': cart_count})


# ============================================
# ORDER TRACKING VIEW
# ============================================
def tracker(request):
    """
    Track user orders by order ID.
    
    GET Parameters:
    - order_id: The unique ID of the order to track
    
    Displays:
    - Order status (Processing, Shipped, Out for Delivery, Delivered)
    - Tracking number
    - Estimated delivery date
    - Order items and total price
    
    TODO: Implement order status tracking
    - Accept order ID from user
    - Query Order model
    - Display current order status and timeline
    """
    cart_count = get_cart_count(request.user)
    
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
        # TODO: Query Order by ID and display tracking info
    
    return render(request, 'shop/tracker.html', {'cart_count': cart_count})


# ============================================
# SEARCH VIEW
# ============================================
def search(request):
    """
    Search for products by name or category.
    
    GET Parameters:
    - query: Search term to find products
    
    Returns:
    - List of matching products
    - Search query displayed in results
    
    Search Logic:
    - Searches product name (case-insensitive)
    - Could be extended to search descriptions, categories
    - Uses icontains for partial matches (e.g., "phone" matches "smartphone")
    
    Example:
        If user searches "phone", returns all products with "phone" in the name
    
    TODO: Implement search functionality
    Example:
        query = request.GET.get('query')
        products = Product.objects.filter(product_name__icontains=query)
        return render(request, 'shop/search_results.html', {'products': products})
    """
    cart_count = get_cart_count(request.user)
    return render(request, 'shop/search.html', {'cart_count': cart_count})


# ============================================
# PRODUCT DETAIL VIEW
# ============================================
def productview(request):
    """
    Display details of a single product.
    
    TODO: Implement to show:
    - Full product description
    - High-resolution images
    - Customer reviews
    - Related products
    - Add to cart button
    
    Example implementation:
        product_id = request.GET.get('id')
        product = Product.objects.get(product_id=product_id)
        return render(request, 'shop/product_detail.html', {'product': product})
    """
    cart_count = get_cart_count(request.user)
    return HttpResponse("This is product view page")


# ============================================
# CHECKOUT VIEW
# ============================================
def checkout(request):
    """
    Handle checkout process.
    
    TODO: Implement checkout flow:
    1. Display items in cart
    2. Get shipping address from user
    3. Calculate total price with tax
    4. Process payment
    5. Create Order and OrderItem records
    6. Clear cart
    7. Show order confirmation
    
    Note: Method name has typo 'checkpout' instead of 'checkout'
    """
    cart_count = get_cart_count(request.user)
    return HttpResponse("This is checkout page")


# ============================================
# SHOPPING CART VIEWS
# ============================================

@login_required(login_url='/admin/login/')
def add_to_cart(request, product_id):
    """
    Add product to cart or increase quantity if already exists
    
    URL: /shop/add-to-cart/{product_id}/
    
    Logic:
    1. Get product by ID
    2. Check if product already in user's cart
    3. If yes → increase quantity by 1
    4. If no → create new cart item
    5. Redirect to previous page
    """
    try:
        # Get the product from database
        product = Product.objects.get(product_id=product_id)
        
        # Check if this product already in this user's cart
        cart_item = Cart.objects.filter(user=request.user, product=product).first()
        
        if cart_item:
            # Product already in cart - increase quantity
            cart_item.quantity += 1
            cart_item.save()
        else:
            # Product not in cart - add new item
            Cart.objects.create(
                user=request.user,
                product=product,
                quantity=1
            )
        
        # Redirect back to shop or product page
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    except Product.DoesNotExist:
        # Product not found - redirect to shop
        return redirect('/shop/')


@login_required(login_url='/admin/login/')
def view_cart(request):
    """
    Display all items in user's shopping cart
    
    URL: /shop/cart/
    
    Shows:
    - All products in user's cart
    - Quantity of each product
    - Total price calculation
    - Increase/Decrease/Delete buttons
    """
    # Get all items in this user's cart
    cart_items = Cart.objects.filter(user=request.user)
    
    # Calculate total price
    total_price = 0
    for item in cart_items:
        total_price += item.get_total_price()
    
    # Get cart count for navbar
    cart_count = cart_items.count()
    
    params = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': cart_count
    }
    
    return render(request, 'shop/cart.html', params)


@login_required(login_url='/admin/login/')
def increase_qty(request, cart_id):
    """
    Increase quantity of item in cart by 1
    
    URL: /shop/increase-qty/{cart_id}/
    
    Example:
    - User has Laptop x2 in cart
    - Clicks + button
    - Quantity becomes x3
    """
    try:
        # Get cart item for this user
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        
        # Increase quantity
        cart_item.quantity += 1
        cart_item.save()
    
    except Cart.DoesNotExist:
        # Cart item not found or doesn't belong to user
        pass
    
    # Redirect back to cart
    return redirect('/shop/cart/')


@login_required(login_url='/admin/login/')
def decrease_qty(request, cart_id):
    """
    Decrease quantity of item in cart by 1
    
    URL: /shop/decrease-qty/{cart_id}/
    
    Logic:
    - If quantity > 1 → decrease by 1
    - If quantity = 1 → delete the item from cart
    
    Example:
    - User has Laptop x2 in cart
    - Clicks − button
    - Quantity becomes x1
    - Click − again → item deleted
    """
    try:
        # Get cart item for this user
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        
        if cart_item.quantity > 1:
            # Quantity is more than 1 - just decrease it
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # Quantity is 1 - delete the item completely
            cart_item.delete()
    
    except Cart.DoesNotExist:
        # Cart item not found or doesn't belong to user
        pass
    
    # Redirect back to cart
    return redirect('/shop/cart/')


@login_required(login_url='/admin/login/')
def delete_from_cart(request, cart_id):
    """
    Remove item from cart completely (regardless of quantity)
    
    URL: /shop/delete-from-cart/{cart_id}/
    
    This is a "Delete" button - removes item immediately
    regardless of how many are in cart
    
    Example:
    - User has Laptop x5 in cart
    - Clicks Delete button
    - All 5 removed at once
    """
    try:
        # Get cart item for this user
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        
        # Delete the item
        cart_item.delete()
    
    except Cart.DoesNotExist:
        # Cart item not found or doesn't belong to user
        pass
    
    # Redirect back to cart
    return redirect('/shop/cart/')
