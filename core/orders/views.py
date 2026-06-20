from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import *
from .forms import *
import requests
import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.utils import timezone
from accounts.models import Customer
from django.contrib import messages
from utils import CustomerLoginRequiredMixin
from utils import send_new_order_notif


# Create your views here.


MERCHANT = 'ab11efee-695b-4070-a6ac-cb22fba2f2eb'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"


from django.urls import reverse


class CreateOrderView(View):

    def get(self, request, product_id, package_id):
        if request.user.is_authenticated: 
            package = Package.objects.get(id=package_id)
            price = package.off_price if package.off_price != 0 else package.price
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.create(
                package=package,
                customer=customer,
                total_price=price,
                status=False
            )

            return redirect('orders:order_detail', order.id)

        messages.success(request, "لطفا برای ثبت سفارش وارد شوید.")

        login_url = reverse('accounts:customer_authentication')
        return redirect(f"{login_url}?next={request.get_full_path()}")

		
class OrderDetailView(CustomerLoginRequiredMixin, View):
	def get(self, request, order_id):
		order = Order.objects.get(id=order_id)
		form = OrderForm()
		product = order.product
		return render(request, 'orders/order_detail.html', {'form': form, 'product': product, 'order':order})

	def post(self, request, order_id):
		messages_list = []
		order = Order.objects.get(id=order_id)
		form = OrderForm(request.POST)
		customer = Customer.objects.get(user=request.user)
		product = order.product

		if form.is_valid():
			full_name = form.cleaned_data['full_name']
			phone_number = form.cleaned_data['phone_number']
			email = form.cleaned_data['email']
			domain = form.cleaned_data['domain']
			
			# بررسی خالی بودن فیلدها
			if not full_name:
				messages_list.append(('error', 'فیلد نام کامل نمی‌تواند خالی باشد.'))
			if not phone_number:
				messages_list.append(('error', 'فیلد شماره تلفن نمی‌تواند خالی باشد.'))
			if not email:
				messages_list.append(('error', 'فیلد ایمیل نمی‌تواند خالی باشد.'))	

			
							

			# اگر پیام خطایی وجود داشت، صفحه را دوباره رندر کن
			if messages_list:
				for level, message in messages_list:
					messages.add_message(request, getattr(messages, level.upper()), message)
				return redirect('orders:order_detail', order.id)


			return redirect('orders:order_payment', order.id)

		# اگر فرم معتبر نباشد، پیام خطای کلی اضافه کن
		messages_list.append(('error', 'لطفاً اطلاعات فرم را به درستی وارد کنید.'))
		for level, message in messages_list:
			messages.add_message(request, getattr(messages, level.upper()), message)
		return render(request, 'orders/order_detail.html', {'form': form, 'product': product})

class OrderPayView(View):

	def get(self, request, order_id, *args, **kwargs):
		try:
			order = Order.objects.get(id=order_id)
		except Order.DoesNotExist:
			return HttpResponseBadRequest("سفارش یافت نشد")

		# ذخیره سفارش برای verify
		request.session['order_pay'] = {
			'order_id': order.id,
		}

		data = {
			"pin": "FA0A1877498F2D3ED7D8",
			"amount": order.total_price,
			"callback": "https://anisitesaz.ir/orders/order-verify/",
			"mobile": str(request.user.phone_number),
			"email": request.user.email,
			"invoice_id": str(order.id),
			"description": f"پرداخت سفارش شماره {order.id}",
		}

		# ارسال ریفرر صحیح
		headers = {
			"Referer": "https://anisitesaz.ir/"
		}

		response = requests.post(
			"https://panel.aqayepardakht.ir/api/v2/create",
			data=data,
			headers=headers
		)

		if response.status_code == 200:
			json_data = response.json()

			if json_data.get("status") == "success":
				transid = json_data.get("transid")

				# ذخیره transid برای verify
				request.session["transid"] = transid

				# ریدایرکت کاربر به درگاه
				request.session["startpay_url"] = f"https://panel.aqayepardakht.ir/startpay/{transid}"
				return redirect("orders:startpay_redirect_page")

			messages.error(request, f"خطا: {json_data.get('errorMessage')}")
			return redirect("dashboard:customer_dashboard_order_detail", order.id)

		messages.error(request, "خطا در اتصال به درگاه پرداخت")
		return redirect("dashboard:customer_dashboard_order_detail", order.id)

class StartPayRedirectView(View):
	def get(self, request, *args, **kwargs):

		url = request.session.get("startpay_url")
		if not url:
			return HttpResponseBadRequest("آدرس پرداخت یافت نشد")

		return render(request, "orders/startpay_redirect.html", {"url": url})


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
class OrderVerifyView(View):

	def post(self, request, *args, **kwargs):

		transid = request.POST.get("transid")
		status = request.POST.get("status")
		order_id = request.POST.get("invoice_id")

		if not transid or not order_id:
			return HttpResponseBadRequest("اطلاعات ناقص")

		order = get_object_or_404(Order, id=order_id)

		# اگر پرداخت ناموفق بوده
		if status != "1":
			messages.error(request, "پرداخت ناموفق بود")
			return redirect("dashboard:customer_dashboard_order_detail", order.id)

		# مرحله verify
		data = {
			"pin": "FA0A1877498F2D3ED7D8",
			"amount": order.total_price,
			"transid": transid
		}

		response = requests.post(
			"https://panel.aqayepardakht.ir/api/v2/verify",
			data=data
		)

		if response.status_code != 200:
			messages.error(request, "خطا در ارتباط با درگاه")
			return redirect("dashboard:customer_dashboard_order_detail", order.id)

		result = response.json()

		if result.get("status") == "success":

			# ثبت پرداخت موفق
			order.status = True
			# order.payment_ref_id = transid
			order.save()

			product = order.product
			product.stock -= 1
			product.purchase_date = timezone.now()
			product.purchase_num += 1
			product.save()
			about = AboutDescription.objects.first()
			send_new_order_notif(about.phone, order.id)
			messages.success(request, "پرداخت با موفقیت انجام شد")
			
			return redirect("dashboard:customer_dashboard_order_detail", order.id)

		messages.error(request, "تراکنش تایید نشد")
		return redirect("dashboard:customer_dashboard_order_detail", order.id)


class OrderFactorView(View):
	template_name = 'dashboard/customer-dashboard-order-factor.html'

	def get(self, request, order_id):
		order = Order.objects.get(id=order_id)
		return render(request, self.template_name, {'order':order})

class CouponApplyView(View):

	def post(self, request, order_id):
		order = Order.objects.get(id=order_id)
		form = CouponForm(request.POST)
		if order.used_coupon:
			messages.error(request, "قبلا برای این سفارش کد تخفیف ثبت شده است")
			return redirect('orders:order_detail', order.id)
		if form.is_valid():
			code = form.cleaned_data['code']
			coupon = Coupon.objects.filter(code = code).first()
			if coupon == None:
				messages.error(request, "کد وارد شده نامعتبر یا منقضی شده است.")
				return redirect('orders:order_detail', order.id)
			if coupon.is_valid():
				if coupon.category.filter(id__in=order.product.category.all()).exists():
					if coupon.used_times <= coupon.usage_limit:
						if coupon.discount_type.name == 'percent':
							discount = (order.product.get_active_price()*coupon.discount)/100
						else:
							discount = coupon.discount
						coupon.used_times = coupon.used_times + 1
						coupon.save()
						order.total_price = order.total_price - discount
						order.used_coupon = coupon
						order.save()
						messages.success(request, "کد تخفیف شما با موفقیت اعمال شد.")
						return redirect('orders:order_detail', order.id)
					messages.error(request, "تعداد دفعات مجاز برای استفاده از این کد به پایان رسیده است.")
					return redirect('orders:order_detail', order.id)
				messages.error(request, "کد وارد شده مربوط به دسته‌بندی محصول سفارش شما نیست.")
				return redirect('orders:order_detail', order.id)
			messages.error(request, "کد وارد شده منقضی شده است.")
			return redirect('orders:order_detail', order.id)
			
			



