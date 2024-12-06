
from django.contrib import admin
from django.urls import path
from marketplaceapp import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('starter/', views.starter, name='starter'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('register-farmer/', views.register_farmer, name='register-farmer'),
    path('create-account/', views.create_account, name='create-account'),
    path('login-customer/', views.login_customer, name='login-customer'),
    path('login-farmer/', views.login_farmer, name='login-farmer'),
    path('farmer-dashboard/', views.farmer_dashboard, name='farmer-dashboard'),
    path('post-product/', views.post_product, name='post-product'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('buy-product/<uuid:product_id>/', views.buy_product, name='buy-product'),
    path('error', views.error, name='error'),
    path('product/<uuid:product_id>/', views.product_details, name='product-details'),
    path('checkout/<uuid:product_id>/', views.checkout, name='checkout'),
    path('purchse-summary/<uuid:product_id>/', views.purchase_summary, name='purchase-summary'),
    path('pay/<uuid:product_id>/', views.pay, name='pay'),
    path('stk/<uuid:product_id>/', views.stk, name='stk'),
    path('token/', views.token, name='token'),
    path('search/', views.search_results, name='search-results'),
    path('logout/', views.logout_farmer, name='logout'),
]
