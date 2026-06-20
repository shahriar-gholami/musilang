from django.db import models
from ckeditor.fields import RichTextField
from khayyam import JalaliDatetime
from django.templatetags.static import static
from django.urls import reverse
import os
import uuid


# تابع مدیریت مسیر آپلود
def upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]

    # تعیین پوشه بر اساس نوع مدل
    folder = instance.__class__.__name__.lower()

    return f"music/{folder}/{uuid.uuid4().hex}{ext}"


# Create your models here.

class BlogCategory(models.Model):
	name = models.CharField(max_length=250)
	slug = models.CharField(max_length=250, blank=True, null=True)
	description = models.TextField(null=True, blank=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			slug = (self.name.replace(' ','-')) 
			slug = slug.replace('/','')
			self.slug = slug
		super().save(*args, **kwargs)

	def get_slug(self):
		slug = (self.name.replace(' ','-')).lower()
		slug = slug.replace('/','')
		return slug

	def __str__(self):
		return self.name
	
class BlogTag(models.Model):
	name = models.CharField(max_length=250)
	slug = models.CharField(max_length=250, blank=True, null=True)
	description = models.TextField(null=True, blank=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			slug = (self.name.replace(' ','-')) 
			slug = slug.replace('/','')
			self.slug = slug
		super().save(*args, **kwargs)

	def get_slug(self):
		slug = (self.name.replace(' ','-')).lower()
		slug = slug.replace('/','')
		return slug
	
	def __str__(self):
		return self.name

class BlogPost(models.Model):
	title = models.CharField(max_length=250)
	slug = models.CharField(max_length = 250)
	category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, null=True, blank=True)
	tags = models.ManyToManyField(BlogTag)
	body = RichTextField(default = "insert the post body")
	created_date = models.DateTimeField(auto_now_add=True)
	published = models.BooleanField(default=False)
	meta_description = models.TextField()
	image = models.ImageField(upload_to=upload_to, default='media/11.png')

	def get_faqs(self):
		return PostFAQ.objects.filter(post=self)

	@property
	def shamsi_created_date(self):
		return JalaliDatetime(self.created).strftime('%Y/%m/%d')
	
	def get_body(self):
		return self.body.replace('\n', '<br>')
	
	def get_thumbnail(self):
		main_image = self.image
		if main_image == None:
			return static('assets/images/11.jpg')
		else:
			main_image_url = main_image.url.split('?')[0]
		return main_image_url

	def get_absolute_url(self):
		return reverse('blog:post_detail', kwargs={'post_slug':self.slug})

	@property
	def shamsi_created_date(self):
		return JalaliDatetime(self.created_date).strftime('%Y/%m/%d')
	
	class Meta:
		ordering = ('-created_date',)

class PostFAQ(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="faqs"
    )
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question

