from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Dashboard
    path('', views.home_view, name='index'),

    # Data
    path('data/', views.data_view, name='data'),

    # User
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # User profile
    path('profile_add/', views.profile_create, name='profile-add'),
    path('profile/<int:profile_id>/', views.profile_view, name='profile'),
    path('profile/<int:profile_id>/profile_update/', views.profile_update, name='profile-update'),

    # Customer
    path('customer_add/', views.customer_create, name='customer-add'),
    path('customer/<int:pk>/', views.customer_view, name='detail'),
    path('customer/<int:pk>/customer_update/', views.customer_update, name='customer-update'),
    path('customer/<int:pk>/customer_delete/', views.customer_delete, name='customer-delete'),

    # Order
    path('customer/<int:pk>/order_add/', views.order_create, name='order-add'),
    path('customer/<int:pk>/order_update/<int:order_id>/', views.order_update, name='order-update'),
    path('customer/<int:pk>/order_delete/<int:order_id>/', views.order_delete, name='order-delete'),

    # Product
    path('product/', views.product_view, name='product'),
    path('product_add/', views.product_create, name='product-add'),
    path('product/<int:product_id>/product_update/', views.product_update, name='product-update'),
    path('product/<int:product_id>/product_delete/', views.product_delete, name='product-delete'),
]
