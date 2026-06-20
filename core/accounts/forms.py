from django import forms

class RegisterForm(forms.Form):
    full_name = forms.CharField(required=False)
    phone_number = forms.CharField(required=False)

class LoginForm(forms.Form):
    phone_number = forms.CharField(required=False)

class VerificationCodeForm(forms.Form):
    code = forms.IntegerField()

class TicketForm(forms.Form):
    subject = forms.CharField(required=True)
    body = forms.CharField()

class TicketReplyForm(forms.Form):
    body = forms.CharField(required = True)

class CustomerForm(forms.Form):
    full_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    
