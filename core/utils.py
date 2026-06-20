import requests
import json
import boto3


def send_otp_code(phone_number, code):
	url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

	payload = json.dumps({
	"code": "gskiz2lm6os5ucg",
	"sender": "+983000505",
	"recipient": phone_number,
	"variable": {
		"verification-code": code

	}
	})
	headers = {
	'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
	'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=payload)

def send_new_order_notif(phone_number, code):
	url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"
	print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaa')
	payload = json.dumps({
	"code": "z86xdhllvf2g4vt",
	"sender": "+983000505",
	"recipient": phone_number,
	"variable": {
		"code": code
	}
	})
	headers = {
	'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
	'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=payload)

from django.contrib.auth.mixins import UserPassesTestMixin
from urllib.parse import urlparse
from accounts.models import Customer
from django.shortcuts import redirect
from django.urls import reverse


	
class IsCustomerUserMixin(UserPassesTestMixin):
	def test_func(self):
		if self.request.user.is_authenticated:
			current_path = self.request.path
			parsed_url = urlparse(current_path)
			path_segments = parsed_url.path.split('/')
			customer = Customer.objects.filter(user = self.request.user).first()
			if customer != None:
				return True
			return False
		return False
	

class CustomerLoginRequiredMixin:
    """
    اگر کاربر لاگین نکرده باشه یا Customer نداشته باشه،
    ریدایرکت میشه به صفحه احراز هویت.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:customer_authentication')}?next={request.get_full_path()}")

        # بررسی اینکه یوزر، Customer داره یا نه
        # if not hasattr(request.user, 'customer'):
        #     return redirect(reverse('accounts:customer_authentication'))

        return super().dispatch(request, *args, **kwargs)
