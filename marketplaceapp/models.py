import uuid

from django.db import models

# Create your models here.
class Farmer(models.Model):
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=250)
    password = models.CharField(max_length=255)  # Consider hashing passwords securely

    def __str__(self):
        return self.username

class Customer(models.Model):
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.email

class Product(models.Model):
    farmer = models.ForeignKey('Farmer', on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    product_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} by {self.farmer.username}"

class Delivery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="deliveries")
    customer_name = models.CharField(max_length=100, default='Unknown')
    customer_email = models.EmailField()
    county = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery for {self.customer_name} to {self.town}"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.name