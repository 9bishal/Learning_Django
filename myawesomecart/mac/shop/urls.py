
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

    # ==================== USER AUTHENTICATION URLS ====================
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("add-address/", views.add_address, name="add_address"),
    path("edit-address/<int:address_id>/", views.edit_address, name="edit_address"),
    path("delete-address/<int:address_id>/", views.delete_address, name="delete_address"),

    # ==================== ORDER HISTORY URLS ====================
    path("order-history/", views.order_history, name="order_history"),
    path("order/<str:order_id>/", views.order_detail, name="order_detail"),
]
