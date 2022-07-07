from unicodedata import category
from django import forms
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, null = True,blank=True ,on_delete=models.CASCADE)
    phone = models.CharField(max_length=200, null=True )
    profile_pic = models.ImageField(default="profile.png",null = True,blank = True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

class Category(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class Color(models.Model):
    color = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.color

class Size(models.Model):
    size = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.size



class Product(models.Model):
    name = models.CharField(max_length=200,blank = True, null=True)
    price = models.FloatField(default=0,null=True)
    category = models.ManyToManyField(Category)
    description = models.CharField(max_length=2000, null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    quantity = models.CharField(max_length=100,blank = True, null=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    color = models.ManyToManyField(Color)
    size = models.ManyToManyField(Size)
    stock = models.IntegerField(default=0, null = True,blank = True)
    discount = models.IntegerField(default=0, null = True,blank = True)
    discount_amount = models.FloatField(default=0, null = True,blank = True)
    rate = models.FloatField(default=0, null = True,blank = True)

    def __str__(self):
        return self.name

class ProductImages(models.Model):
    product =  models.ForeignKey(Product, null=True, on_delete= models.CASCADE)
    img = models.ImageField(default="product-pic.jpg",null = True,blank = True)

class Order(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered','Delivered'),
        ('Take','Take')
    )
    customer = models.ForeignKey(Customer, null=True, on_delete= models.CASCADE)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    delivery_fee = models.FloatField(default=0,blank=True,null=True)
    total = models.FloatField(default=0,blank=True,null=True)
    status = models.CharField(default="Pending",max_length=200,blank=True, null=True,choices=STATUS)
    taken_user = models.ForeignKey(User, null=True, on_delete= models.CASCADE)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    

class Delivery_charge(models.Model):
    fee = models.FloatField(default=0,blank=True,null=True)
    discount = models.IntegerField(default=0,blank=True,null=True)

class OrderItem(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered','Delivered')
    )
    customer = models.ForeignKey(Customer, null=True, on_delete= models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0,null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.CharField(default="Pending",max_length=200,blank=True, null=True,choices=STATUS)

    def __str__(self):
        return self.product.name

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.city

class Review(models.Model):
    user = models.ForeignKey(Customer, models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    comment = models.TextField(max_length=250)
    rate = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)