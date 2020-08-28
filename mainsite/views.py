from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.urls import reverse
from django.utils.http import urlencode
from django.utils import timezone
import json

import logging

from . import models

logger = logging.getLogger("mylogger")


class CompleteCategory():
    def __init__(self, parrent_category):
        self.parrent_category = parrent_category
        self.child_categories = []

    def addSubCategory(self, child_categories):
        self.child_categories.append(child_categories)

    def setSubCategoryList(self, child_categories_list):
        self.child_categories = child_categories_list


def get_category_list():
    all_categories = models.Category.objects.all().filter(category_parentId=0)
    ret_category_list = []

    for category in all_categories:
        complete_category = CompleteCategory(category)
        child_categories = models.Category.objects.all().filter(category_parentId=category.id)
        # holecategory.sub_categories = sub_categories
        complete_category.setSubCategoryList(child_categories)
        ret_category_list.append(complete_category)

    return ret_category_list

def index(request):
    product_list = models.Product.objects.all()[:30]
    # category_list = Category.objects.all()[:5]
    category_list = get_category_list()
    req_user = request.user
    action = 'none'

    if request.GET.get('action'):
        action = request.GET.get('action')
    
    context = {
        'product_list': product_list,
        'category_list': category_list,
        'action': action,
        'req_user': req_user,
    }
    return render(request, 'mainsite/index.html', context)

def category(request, cate_urlname):
    category_list = get_category_list()
    req_user = request.user

    try:
        current_category = models.Category.objects.get(category_urlname=cate_urlname)
    except (KeyError, models.Category.DoesNotExist):
        return HttpResponseRedirect('/')
    product_list = models.Product.objects.filter(product_category=current_category)

    context = {
        'current_category': current_category,
        'product_list': product_list,
        'category_list': category_list,
        'req_user': req_user,
    }

    return render(request, 'mainsite/category.html', context)

def product(request, prod_id):
    category_list = get_category_list()
    req_user = request.user
    
    try:
        selected_product = models.Product.objects.get(pk=prod_id)
    except (KeyError, models.Product.DoesNotExist):
        return render(request, 'mainsite/product.html', {'category_list': category_list, 'req_user': req_user})
    
    if selected_product.product_stock < 10:
        stock_color = 'badge-danger'
    elif selected_product.product_stock < 20:
        stock_color = 'badge-warning'
    else:
        stock_color = 'badge-success'
    
    url_product_name = selected_product.product_name.replace(' ','-')

    if not url_product_name in request.path:
        url_product_name = '%s-%i' % (url_product_name, selected_product.id)
        return HttpResponseRedirect('/product/%s/' % url_product_name)
    
    context = {
        'product': selected_product,
        'category_list': category_list,
        'stock_color': stock_color,
        'req_user':req_user, 
        }
    return render(request, 'mainsite/product.html', context)

def register(request):
    category_list = get_category_list()
    req_user = request.user
    register_error = 'none'
    can_register = True
    if request.user.is_authenticated:
        code = '?%s'% urlencode({'action': 'login_success'})
        url = reverse('mainsite:index')
        return HttpResponseRedirect('%s%s' % (url, ''))
    if request.method == 'POST':
        account_login = request.POST.get('UsernameInput')
        account_password = request.POST.get('PasswordInput')
        account_firstname = request.POST.get('FirstNameInput')
        account_lastname = request.POST.get('LastNameInput')
        account_email = request.POST.get('EmailInput')
        
        try:
            user = User.objects.create_user(username=account_login, password=account_password, first_name=account_firstname, last_name=account_lastname, email=account_email)
        except (IntegrityError):
            register_error = 'acc_exist'
        else:
            logger.info('%s' % (user))

    context = {
        'category_list': category_list,
        'register_error': register_error,
        'can_register': can_register,
        'req_user': req_user,
    }

    return render(request, 'mainsite/registration-form.html', context)

def login_form(request):
    category_list = get_category_list()
    login_error = 'none' #TODO(zakrzu): rename to login_status
    can_login = True

    if request.user.is_authenticated:
        login_error = 'authallow'
        can_login = False

    if request.method == 'POST':
        if request.POST.get('logout') == 'true':
            logout(request)
            can_login = True
        else:
            account_username = request.POST.get('UsernameInput')
            account_password = request.POST.get('PasswordInput')

            user = authenticate(username=account_username, password=account_password)
            if user is not None:
                login(request, user)
                login_error = 'logged'
                can_login = False
            else:
                login_error = 'acc_badnameorpassword'

    req_user = request.user
    context = {
        'category_list': category_list,
        'login_error': login_error,
        'can_login': can_login,
        'req_user': req_user,
    }
    return render(request, 'mainsite/login-form.html', context)

@login_required(login_url='/login/')
def cart_check(request):
    category_list = get_category_list()
    try:
        cart_list = models.Cart.objects.all().filter(cart_user=request.user)
    except (KeyError, models.Cart.DoesNotExist, TypeError):
        cart_list = 'empty'
    
    if not cart_list:
        cart_list = 'empty'
    req_user = request.user
    context = {
        'category_list': category_list,
        'cart_list': cart_list,
        'req_user': req_user,
    }
    return render(request, 'mainsite/cart.html', context)

@login_required(login_url='/login/')
def cart_add(request, prod_id):
    req_user = request.user
    try:
        get_product = models.Product.objects.get(pk=prod_id)
    except (KeyError, models.Product.DoesNotExist):
        return HttpResponseRedirect(reverse('mainsite:index'))

    new_cart_item = models.Cart(cart_product=get_product, cart_user=req_user)
    new_cart_item.save()
    return HttpResponseRedirect(reverse('mainsite:product', args=(get_product.id,)))

@login_required(login_url='/login/')
def cart_del(request, cart_id):
    response = HttpResponse()
    response.status_code = 200
    try:
        get_cart = models.Cart.objects.get(pk=cart_id)
    except (KeyError, models.Cart.DoesNotExist):
        return HttpResponseRedirect(reverse('mainsite:index'))
    get_cart.delete()
    return HttpResponseRedirect(reverse('mainsite:cart'))

@login_required(login_url='/login/')
def cart_update(request, prod_id):
    response = HttpResponse()
    response.status_code = 404

    if request.method == 'POST':
        body = json.loads(request.body)
        quantity = body.get('cart_quantity')
    else:
        return HttpResponseRedirect(reverse('mainsite:index'))

    try:
        get_cart = models.Cart.objects.get(pk=prod_id)
        get_product = models.Product.objects.get(pk=get_cart.cart_product.id)
    except (KeyError, models.Cart.DoesNotExist):
        return response
    
    if int(quantity) <= 0 or int(quantity) > int(get_product.product_stock):
        response.status_code = 403
        return response

    get_cart.cart_quantity = quantity
    get_cart.save()
    response.status_code = 200
    return response

class CompleteOrder():
    def __init__(self, m_order):
        self.main_order = m_order
        self.ordered_products = []
    def addProductName(self, product):
        self.ordered_products.append(product)

def orders(request):
    category_list = get_category_list()
    req_user = request.user
    if request.method == 'POST':
        cart = models.Cart.objects.all().filter(cart_user=req_user)
        user = User.objects.get(pk=req_user.id)
        order_new = models.Order(user=user, date=timezone.now(), status_id=1)
        order_new.save()
        for item in cart:
            product = item.cart_product
            quantity = item.cart_quantity
            ordered_product = models.OrderedProduct(ordered_product=product, ordered_price=product.product_price, ordered_quantity=quantity, order_id=order_new)
            order_new.cost = order_new.cost + (float(product.product_price) * int(quantity))
            order_new.save()
            ordered_product.save()
        cart.delete()
        response = HttpResponse()
        response.status_code = 200
        return response
    

    corders = []
    try:
        orders = models.Order.objects.all().filter(user=req_user)
    except (KeyError, models.Order.DoesNotExist):
        corders = 'empty'
    
    if len(orders) > 0: 
        for act_order in orders:
            ord_prod = models.OrderedProduct.objects.all().filter(order_id=act_order)
            corder_new = CompleteOrder(act_order)
            for prod in ord_prod:
                corder_new.addProductName(prod.ordered_product.product_name)
            corders.append(corder_new)
    else:
        corders = 'empty'

    context = {
        'category_list': category_list,
        'req_user': req_user,
        'orders_list': corders,
    }
    return render(request, 'mainsite/order-list.html', context)

def orders_mod(request, user_id, order_id):
    return HttpResponseRedirect(reverse('mainsite:index'))

def order_process(request):
    category_list = get_category_list()
    req_user = request.user
    context = {
        'category_list': category_list,
        'req_user': req_user,
    }

    if request.method == 'POST':
        if request.POST.items():
            logger.info(request.POST)
        return render(request, 'mainsite/order-complete.html', context)
        

    return render(request, 'mainsite/order-address-form.html', context)

@login_required(login_url='/login/')
def customer_settings(request, selected_setting):
    category_list = get_category_list()
    req_user = request.user
    action = ''

    if request.method == 'POST':
        if request.POST.get('action') == 'updateAccountInfo':
            post_data = request.POST
            if post_data.get('firstName') != req_user.first_name:
                req_user.first_name = post_data.get('firstName')
                action = 'updateAccountInfo_success'

            if post_data.get('lastName') != req_user.last_name:
                req_user.last_name = post_data.get('lastName')
                action = 'updateAccountInfo_success'

            if post_data.get('email') != req_user.email:
                req_user.email = post_data.get('email')
                action = 'updateAccountInfo_success'
            
        if request.POST.get('action') == 'changePassword':
            post_data = request.POST
            if post_data.get('oldPassword') is not None and post_data.get('newPassword') is not None and post_data.get('confirmNewPassword') is not None:
                if req_user.check_password(post_data.get('oldPassword')):
                    if post_data.get('newPassword') == post_data.get('confirmNewPassword'):
                        req_user.set_password(post_data.get('newPassword'))
                        action = 'changePassword_success'
                    else:
                        action = 'changePassword_error'
                else:
                    action = 'changePassword_error'
        req_user.save()     

        if request.POST.get('action') == 'updateAddress':
            try:
                details = models.CustomerDetails.objects.get(user=req_user)
            except (KeyError, models.CustomerDetails.DoesNotExist): 
                details = models.CustomerDetails.objects.create_request_post(request)
            else:
                details.update_request_post(request)

    context = {
        'category_list': category_list,
        'req_user': req_user,
        'action': action,
    }

    if selected_setting == 'address':
        try:
            details = models.CustomerDetails.objects.get(user=req_user)
        except (KeyError, models.CustomerDetails.DoesNotExist):
            details = models.CustomerDetails.objects.create_empty(req_user)

        context_address = {
            'shipping_address': details.shipping_address,
            'billing_address': details.billing_address,
        }
        context.update(context_address)

    settings_list = {
        'main': 'mainsite/customer-settings.html',
        'address': 'mainsite/customer-address.html',
    }

    # settings_context = {
    #     'address': get_customer_addresses(req_user),
    # }

    # context.update(settings_context.get(selected_setting, ''))

    return render(request, settings_list.get(selected_setting, 'mainsite/customer-settings.html'), context)

def test_template(request):
    category_list = get_category_list()
    req_user = request.user
    context = {
        'category_list': category_list,
        'req_user': req_user,
    }
    return render(request, 'mainsite/order-address-form.html', context)