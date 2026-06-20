from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
import os
import uuid 
from django.utils import timezone
import random
from khayyam import JalaliDatetime
from django.utils.translation import gettext_lazy as _

def upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]
    slug = getattr(instance, 'name', 'general')
    return f"music/accounts/{slug.replace(' ','-')}/{uuid.uuid4().hex}{ext}"

class Package(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    duration_days = models.IntegerField(default=30)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, null=True, blank=True, verbose_name='مشتری')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True)
    total_price = models.IntegerField(verbose_name='مبلغ کل', null=True, blank=True)
    status = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add = True, verbose_name='تاریخ ایجاد')

    @property
    def shamsi_created_date(self):
        return JalaliDatetime(self.created_date).strftime('%Y/%m/%d')