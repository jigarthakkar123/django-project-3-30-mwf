from django.db import models
from django.utils import timezone
# Create your models here.
class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	address=models.TextField()
	password=models.CharField(max_length=100)
	usertype=models.CharField(max_length=100,default="user")
	profile_picture=models.ImageField(upload_to="profile_picture/",default="")

	def __str__(self):
		return self.fname+" "+self.lname

class Event(models.Model):
	manager=models.ForeignKey(User,on_delete=models.CASCADE)
	event_name=models.CharField(max_length=100)
	event_date=models.CharField(max_length=100)
	event_venue=models.CharField(max_length=100)
	event_time=models.CharField(max_length=100)
	event_price=models.PositiveIntegerField()
	event_desc=models.TextField()
	event_image=models.ImageField(upload_to="event_images/")


	def __str__(self):
		return self.manager.fname+" - "+self.event_name

class BookEvent(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	event=models.ForeignKey(Event,on_delete=models.CASCADE)
	booking_date=models.DateTimeField(default=timezone.now)
	payment_status=models.BooleanField(default=False)

	def __str__(self):
		return self.user.fname+" - "+self.event.event_name