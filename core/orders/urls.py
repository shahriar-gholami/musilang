from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from . import views


app_name = 'orders'

urlpatterns = [ 

    path('create-order/<int:product_id>/<int:package_id>/', views.CreateOrderView.as_view(), name='create_order'),
    path('order-detail/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order-factor/<int:order_id>/', views.OrderFactorView.as_view(), name='order_factor'),
    # path('order-final-check/<int:order_id>/', views.OrderFinalCheckView.as_view(), name='order_final_check'),
    path('apply-coupon/<int:order_id>/', views.CouponApplyView.as_view(), name='apply_coupon'),
    path('order-payment/<int:order_id>/', views.OrderPayView.as_view(), name='order_payment'),
    path('order-verify/', views.OrderVerifyView.as_view(), name='order_verify'),
    path("startpay-redirect/", views.StartPayRedirectView.as_view(), name="startpay_redirect_page"),
]