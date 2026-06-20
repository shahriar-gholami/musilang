from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.views.generic import DeleteView
from .forms import *
from django.views import View
import random
from accounts.models import User
from utils import send_otp_code
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import *

# Create your views here.



def convert_to_english_digits(number_str):
	translation_table = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
	return number_str.translate(translation_table)

class LoginView(View):
    template_name = 'accounts/login_register.html'

    def get(self, request):
        next_url = request.GET.get('next')
        if next_url:
            request.session['next_url'] = next_url

        return render(request, self.template_name, {
            'login_form': LoginForm(),
            'register_form': RegisterForm(),
        })

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            phone_number = convert_to_english_digits(form.cleaned_data['phone_number'])

            if not phone_number:
                messages.error(request, 'فیلد شماره تلفن نمی‌تواند خالی باشد.')
                return render(request, self.template_name, {
                    'login_form': form,
                    'register_form': RegisterForm()
                })

            user = User.objects.filter(phone_number=phone_number).first()
            if user == None:
                messages.error(request, 'کاربری با این شماره تلفن یافت نشد. لطفاً ثبت‌نام کنید.')
                return redirect('accounts:register')

            OtpCode.objects.filter(phone_number=phone_number).delete()

            random_code = random.randint(100000, 999999)
            send_otp_code(phone_number, random_code)
            OtpCode.objects.create(phone_number=phone_number, code=random_code)

            return redirect('accounts:verify_otp', phone_number)

        messages.error(request, 'ورودی نامعتبر است.')
        return render(request, self.template_name, {
            'login_form': form,
            'register_form': RegisterForm()
        })


class RegisterView(View):
	template_name = 'accounts/register.html'

	def get(self , request):
		form = RegisterForm(request.POST)
		next_url = request.GET.get('next')
		if next_url:
			request.session['next_url'] = next_url
		return render(request, self.template_name, {
					'form': RegisterForm()
				})

	def post(self, request):
		form = RegisterForm(request.POST)
		next_url = request.POST.get('next', '/')

		if form.is_valid():
			full_name = form.cleaned_data['full_name']
			if not full_name:
				messages.error(request, 'فیلد نام و نام خانوادگی نمی‌تواند خالی باشد.')
				return render(request, self.template_name, {
					'form': RegisterForm()
				})
			phone_number = convert_to_english_digits(form.cleaned_data['phone_number'])
			if not phone_number:
				messages.error(request, 'فیلد شماره تلفن نمی‌تواند خالی باشد.')
				return render(request, self.template_name, {
					'form': RegisterForm()
				})

			user = User.objects.filter(phone_number=phone_number).first()
			if user:
				messages.error(request, 'کاربری با این شماره تلفن قبلا ثبت‌نام شده است. لطفا وارد حساب خود شوید.')
				return redirect('accounts:login')
				

			new_user = User.objects.create(
				phone_number = phone_number,
				full_name = full_name,
			)

			new_customer = Customer.objects.create(
				user=new_user,
			)

			# حذف کدهای OTP قبلی
			OtpCode.objects.filter(phone_number=phone_number).delete()
			# تولید و ارسال کد OTP
			random_code = random.randint(100000, 999999)
			send_otp_code(phone_number, random_code)  # فرض می‌کنیم این تابع تعریف شده است
			OtpCode.objects.create(phone_number=phone_number, code=random_code)
			
			request.session['next_url'] = next_url
			return redirect('accounts:verify_otp', phone_number)  # ریدایرکت به ویوی تأیید OTP

		# در صورت نامعتبر بودن فرم
		messages.error(request, 'ورودی نامعتبر است.')
		return render(request, self.template_name, {
			'form': RegisterForm()
		})
	
class VerifyOTPView(View):
	template_name = 'accounts/verify_otp.html'

	def get(self, request, phone_number):
		form = VerificationCodeForm
		return render(request, self.template_name, {'form':form,
											  'phone_number':phone_number})
	
	def post(self, request, phone_number, *args, **kwargs):
		form = VerificationCodeForm(request.POST)
		if form.is_valid():
			user = User.objects.filter(phone_number=phone_number).first()
			customer = Customer.objects.filter(user=user).first()
			last_sent_otp = OtpCode.objects.filter(phone_number = phone_number).first()
			recieved_code = form.cleaned_data['code']
			if last_sent_otp.code == recieved_code:
				login(request, user)
				return_url = request.session.pop('next_url', None)
				redirect_to = request.session.pop('after_login_redirect', 'musics:index') 
				# 'home' آدرس پیش‌فرضی است که اگر مقصدی در سشن نبود، کاربر به آنجا برود
				if return_url != None:
					return redirect(return_url)
				return redirect(redirect_to)
			messages.error(request, 'کد ارسالی اشتباه و یا منقضی است.')
			form = VerificationCodeForm
			return render(request, self.template_name, {'form':form})
		messages.error(request, 'ورودی نامعتبر.')
		form = VerificationCodeForm
		return render(request, self.template_name, {'form':form})
	

class UserLogoutView(View):

	def get(self, request):
		logout(request)
		return redirect('shop:index')

