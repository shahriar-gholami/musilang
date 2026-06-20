from django.urls import path, include
from . import views

app_name = "accounts"



urlpatterns = [

    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("verify-otp/<str:phone_number>/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),

]