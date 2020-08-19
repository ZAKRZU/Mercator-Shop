from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

class Category(models.Model):
    category_urlname = models.CharField(max_length=200)
    category_name = models.CharField(max_length=200)
    category_description = models.TextField(max_length=1000)
    category_parentId = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_description = models.TextField(max_length=1000)
    product_price = models.FloatField(default=0.0)
    product_image = models.CharField(max_length=255)
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_buy = models.IntegerField(default=0)
    product_stock = models.IntegerField(default=0) # stock value cannot be less than 0 where 0 mean that product isn't available, and any other number shows how many is available for sell
    def __str__(self):
        return self.product_name

    def stock_update(self, new_stock):
        if new_stock < 0:
            return
        self.product_stock = new_stock

class Cart(models.Model):
    cart_user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return ('%s: %s') % (self.cart_user, self.cart_product)

class OrderStatus(models.Model):
    status_name = models.CharField(max_length=255)
    status_code = models.IntegerField()
    def __str__(self):
        return self.status_name

class Order(models.Model):
    order_user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    order_cost = models.FloatField(default=0.0)

class OrderedProduct(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    ordered_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_price = models.FloatField(default=0.0)
    ordered_quantity = models.IntegerField(default=1)
    
    