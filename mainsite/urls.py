from django.urls import path, re_path

from . import views

app_name = 'mainsite'
urlpatterns = [
    path('', views.index, name='index'),
    path('category/<str:cate_urlname>/', views.category, name='category'),
    re_path(r'^product\/(?:.*)\-(.+)\/$', views.product, name='product'),
    path('register/', views.register, name='register'),
    path('login/', views.login_form, name='login'),
    path('cart/', views.cart_check, name='cart'),
    path('cart/add/<int:prod_id>', views.cart_add, name='cart-add'),
    path('cart/del/<int:cart_id>', views.cart_del, name='cart-del'),
    path('cart/update/<int:prod_id>', views.cart_update, name='cart-update'),
    path('orders/', views.orders, name='customer-orders'),
    path('order/', views.order_process, name='order-process'),
    path('customer/<int:user_id>/orders/<int:order_id>/', views.orders_mod, name='customer-orders-modify'),
    path('customer/settings/', views.customer_settings, kwargs={'selected_setting': 'main'}, name='customer-settings'),
    path('customer/settings/<str:selected_setting>', views.customer_settings, name='customer-setting'),
    path('test/template/', views.test_template, name='test-template'),
]