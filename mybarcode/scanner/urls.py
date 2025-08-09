from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('check_barcode/', views.check_barcode, name='check_barcode'),
    path('update_product_quantity/', views.update_product_quantity, name='update_product_quantity'),
]