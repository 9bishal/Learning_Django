from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_form, name='home'),
    path('form/', views.user_form, name='user_form'),
    path('list/', views.user_list, name='user_list'),
    path('edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('delete/<int:pk>/', views.user_delete, name='user_delete'),
]
