
from django.urls import path
from . import views

urlpatterns = [
    # ==================== SHOP PAGES ====================
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="About Us"),
    path("contact/", views.contact, name="Contact Us"),
    path("tracker/", views.tracker, name="Track delivery"),
    path("search/", views.search, name="search"),
    path("productview/", views.productview, name="search"),
    path("checkout/", views.checkout, name="checkout"),
    
    # ==================== SHOPPING CART URLS ====================
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path("increase-qty/<int:cart_id>/", views.increase_qty, name="increase_qty"),
    path("decrease-qty/<int:cart_id>/", views.decrease_qty, name="decrease_qty"),
    path("delete-from-cart/<int:cart_id>/", views.delete_from_cart, name="delete_from_cart"),
]
