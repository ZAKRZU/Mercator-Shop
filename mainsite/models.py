from django.db import models
from django.contrib.auth.models import User

class AddressManager(models.Manager):
    def create_address(self, first_name, last_name, country='PL', city='', address='', address2='', post_code='', state=''):
        address = Address(first_name=first_name, last_name=last_name, country=country, city=city, address=address, address2=address2, post_code=post_code, state=state)
        
        return address

class CustomerDetailsManager(models.Manager):
    def create_empty(self, user, different=False):
        shipping_address = Address.objects.create_address(user.first_name, user.last_name)
        shipping_address.save()
        
        if different:
            billing_address = Address.objects.create_address(user.first_name, user.last_name)
            billing_address.save()
        else:
            billing_address = shipping_address

        customer_details = CustomerDetails(user=user, shipping_address=shipping_address, different_billing_address=different, billing_address=billing_address)
        customer_details.save()

        return customer_details

    def create_request_post(self, request):
        shipping_address = Address.objects.create_address(
            first_name=request.POST.get('firstName'),
            last_name=request.POST.get('lastName'),
            country=request.POST.get('country'),
            city=request.POST.get('city'),
            address=request.POST.get('address'),
            address2=request.POST.get('address2'),
            post_code=request.POST.get('postalCode'),
            state=request.POST.get('state')
            )
        shipping_address.save()

        if request.POST.get('radio') == 'diffAddress':
            billing_address = Address.objects.create_address(
                first_name=request.POST.get('diff_firstName'),
                last_name=request.POST.get('diff_lastName'),
                country=request.POST.get('diff_country'),
                city=request.POST.get('diff_city'),
                address=request.POST.get('diff_address'),
                address2=request.POST.get('diff_address2'),
                post_code=request.POST.get('diff_postalCode'),
                state=request.POST.get('diff_state')
                )
            billing_address.save()
        else:
            billing_address = shipping_address

        customer_details = CustomerDetails(user=request.user, shipping_address=shipping_address, different_billing_address=(True if request.POST.get('radio') == 'diffAddress' else False), billing_address=billing_address)
        customer_details.save()

        return customer_details

    

class Address(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    country = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def update_from_POST(self, address, request):
        self.first_name = request.POST.get('firstName')
        self.last_name = request.POST.get('lastName')
        self.country = request.POST.get('country')
        self.city = request.POST.get('city')
        self.address = request.POST.get('address')
        self.address2 = request.POST.get('address2')
        self.post_code = request.POST.get('postalCode')
        self.state = request.POST.get('state')

    objects = AddressManager()

class CustomerDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='shipping_address')
    different_billing_address = models.BooleanField(default=False)
    billing_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='billing_address')

    objects = CustomerDetailsManager()

    def __str__(self):
        return self.user.username

    def update_request_post(self, request):
        self.shipping_address.first_name = request.POST.get('firstName')
        self.shipping_address.last_name = request.POST.get('lastName')
        self.shipping_address.country = request.POST.get('country')
        self.shipping_address.city = request.POST.get('city')
        self.shipping_address.address = request.POST.get('address')
        self.shipping_address.address2 = request.POST.get('address2')
        self.shipping_address.post_code = request.POST.get('postalCode')
        self.shipping_address.state = request.POST.get('state')
        self.shipping_address.save()

        self.different_billing_address = (True if request.POST.get('radio') == 'diffAddress' else False)


        #TODO(zakrzu): make different billing address working
        """
        When defined that user will use different address it should create new object and fill it
        but when user decide that he will use the same address then it should delete this object
        and override value with shipping_address
        """
        if self.different_billing_address:
            self.billing_address.first_name = request.POST.get('diff_firstName')
            self.billing_address.last_name = request.POST.get('diff_lastName')
            self.billing_address.country = request.POST.get('diff_country')
            self.billing_address.city = request.POST.get('diff_city')
            self.billing_address.address = request.POST.get('diff_address')
            self.billing_address.address2 = request.POST.get('diff_address2')
            self.billing_address.post_code = request.POST.get('diff_postalCode')
            self.billing_address.state = request.POST.get('diff_state')
            self.billing_address.save()

        return True

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
    product_stock = models.IntegerField(default=0)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    cost = models.FloatField(default=0.0)

class OrderedProduct(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    ordered_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_price = models.FloatField(default=0.0)
    ordered_quantity = models.IntegerField(default=1)
    
    