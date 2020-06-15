from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.signIn, name='login'),
    path('authcheck/', views.authCheck, name='authcheck'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signuprequest/', views.signup_request, name='signuprequest'),
    path('mappoint/', views.map_point, name='mappoint'),
    path('keymap/', views.map_with_key, name='keymap'),
    path('productlist/', views.listProduct, name='productlist'),
    path('productdetails/<slug:key>/<slug:uid>/', views.product_details, name='productdetails'),
    path('businesslist', views.business_list, name='businesslist'),
    path('businessmap', views.business_map, name='businessmap'),
    path('addproduct', views.add_product, name='addproduct'),
    path('addproductfirebase', views.add_product_firebase, name='addproductfirebase'),
    path('updateinfo', views.update_info, name='updateinfo'),
    path('storedetails/<key>/', views.store_details, name='storedetails'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('storeproducts', views.store_products, name='storeproducts'),
    path('change_password', views.change_password, name='change_password'),
    path('addbusinessfirebase', views.add_business_firebase, name='addbusinessfirebase'),
    path('submitproduct', views.submitproduct, name='submitproduct'),
]