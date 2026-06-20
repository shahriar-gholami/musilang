from django import forms


class CouponApplyForm(forms.Form):
	code = forms.CharField()

class OrderForm(forms.Form):
	full_name = forms.CharField(required=False)
	phone_number = forms.CharField(required=False)
	email = forms.EmailField(required=False)
	domain = forms.CharField(required=False)

class ReferalCodrForm(forms.Form):
	referal = forms.CharField(required=False)

class CouponForm(forms.Form):
	code = forms.CharField(required=False)
	