from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=200, null=True)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    start_date = models.DateField(auto_now_add=True)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    address = models.CharField(max_length=300)

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.last_name)


class Customer(models.Model):
    user_profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200, null=True)
    join_date = models.DateField(auto_now_add=True)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    address = models.CharField(max_length=300)

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    STOCK_LEVEL = (
        ('In Stock', 'In Stock'),
        ('Out of Stock', 'Out of Stock'),
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    inventory = models.IntegerField(default=0, blank=False)
    stock = models.CharField(max_length=100, choices=STOCK_LEVEL, default='')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.inventory >= 1:
            self.stock = 'In Stock'
        else:
            self.stock = 'Out of Stock'
        super().save(*args, **kwargs)


class Order(models.Model):
    ORDER_STATUS = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )

    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, choices=ORDER_STATUS)
    order_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product.name + ' - ' + str(self.quantity)

    def total_price(self):
        total_price = self.quantity * self.product.price
        return total_price

    def get_absolute_url(self):
        return reverse('sales:detail', kwargs={'pk': self.customer.pk})
