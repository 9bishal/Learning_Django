
from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="About Us"),
    path("contact/", views.contact, name="Contact Us"),
    path("tracker/", views.tracker, name="Track delivery"),
    path("search/", views.search, name="search"),
    path("productview/", views.productview, name="search"),
    path("checkout/", views.checkout, name="checkout"),
]
