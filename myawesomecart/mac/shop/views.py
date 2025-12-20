"""
Shop Application Views
======================
This module contains all view functions for the shop application.
Views are Python functions that receive a web request and return a web response.
"""

from math import ceil
from django.shortcuts import render
from django.http import HttpResponse
from .models import Product

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
    
    # Dictionary of data to pass to template
    params = {
        'no_of_slides': nslides,           # Number of carousel slides
        'range': range(nslides),            # Range object for looping in template
        'products': products                # All products to display
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
    Currently just renders a basic template.
    """
    return render(request, 'shop/about.html')


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
    if request.method == 'POST':
        # TODO: Process form submission
        # Validate data, save to database, send emails
        pass
    
    return render(request, 'shop/contact.html')


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
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
        # TODO: Query Order by ID and display tracking info
    
    return render(request, 'shop/tracker.html')


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
    return render(request, 'shop/search.html')


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
    return HttpResponse("This is checkout page")
