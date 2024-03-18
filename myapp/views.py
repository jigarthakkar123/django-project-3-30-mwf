from django.shortcuts import render,redirect
from .models import User,Event,BookEvent
import random
import requests
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'

@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'product_data': {
					'name': 'Checkout Session Data',
					},
				'unit_amount': final_amount,
				},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',)
	return JsonResponse({'id': session.id})

def success(request):
	user=User.objects.get(email=request.session['email'])
	bookevents=BookEvent.objects.filter(user=user)
	for i in bookevents:
		i.payment_status=True
		i.save()
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')


# Create your views here.
def index(request):
	return render(request,'index.html')

def rent_venue(request):
	return render(request,'rent-venue.html')

def about(request):
	return render(request,'about.html')

def rent_venue(request):
	return render(request,'rent-venue.html')

def tickets(request):
	return render(request,'tickets.html')

def signup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						usertype=request.POST['usertype'],
						profile_picture=request.FILES['profile_picture']
					)
				msg="User Sign Up Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.usertype=="user":
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_picture']=user.profile_picture.url
					return render(request,'index.html')
				else:
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_picture']=user.profile_picture.url
					return render(request,'manager-index.html')
			else:
				msg="Invalid Password"
				return render(request,'login.html',{'msg':msg})
		except:
			msg="Email Not Registered"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def shows_events(request):
	events=Event.objects.all()
	return render(request,'shows-events.html',{'events':events})

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				if user.usertype=="user":
					return render(request,'change-password.html',{'msg':msg})
				else:
					return render(request,'manager-change-password.html',{'msg':msg})
		else:
			msg="Old Password Does Not Matched"
			if user.usertype=="user":
				return render(request,'change-password.html',{'msg':msg})
			else:
				return render(request,'manager-change-password.html',{'msg':msg})
	else:
		if user.usertype=="user":
			return render(request,'change-password.html')
		else:
			return render(request,'manager-change-password.html')
def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_picture=request.FILES['profile_picture']
		except:
			pass
		user.save()
		msg="Profile Updated Successfully"
		request.session['profile_picture']=user.profile_picture.url
		if user.usertype=="user":
			return render(request,'profile.html',{'user':user,'msg':msg})
		else:
			return render(request,'manager-profile.html',{'user':user,'msg':msg})
	else:
		if user.usertype=="user":
			return render(request,'profile.html',{'user':user})
		else:
			return render(request,'manager-profile.html',{'user':user})

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(mobile=request.POST['mobile'])
			mobile=str(user.mobile)
			otp=random.randint(1000,9999)
			url = "https://www.fast2sms.com/dev/bulkV2"
			querystring = {"authorization":"EM5TxhCfzI9UyJ80Nijw7soGmOrVaAbtQ3nFZeRYqdB2KgWv61ikQ0M538obtfGCvKAlR7xrVXF6mOY9","variables_values":str(otp),"route":"otp","numbers":mobile}
			headers = {'cache-control': "no-cache"}
			response = requests.request("GET", url, headers=headers, params=querystring)
			print(response.text)
			return render(request,'otp.html',{'otp':otp,'mobile':mobile})
		except:
			msg="Mobile Not Registered"
			return render(request,'forgot-password.html',{'msg':msg})
	else:
		return render(request,'forgot-password.html')

def verify_otp(request):
	mobile=request.POST['mobile']
	otp=int(request.POST['otp'])
	uotp=int(request.POST['uotp'])

	if otp==uotp:
		return render(request,'new-password.html',{'mobile':mobile})
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'otp':otp,'mobile':mobile,'msg':msg})

def update_password(request):
	mobile=request.POST['mobile']
	np=request.POST['new_password']
	cnp=request.POST['cnew_password']

	if np==cnp:
		user=User.objects.get(mobile=mobile)
		user.password=np
		user.save()
		msg="Password Updated Successfully"
		return render(request,'login.html',{'msg':msg})
	else:
		msg="New Password & Confirm New Password Does Not Matched"
		return render(request,'new-password.html',{'mobile':mobile,'msg':msg})

def manager_index(request):
	return render(request,'manager-index.html')

def manager_add_event(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		Event.objects.create(
				manager=user,
				event_name=request.POST['event_name'],
				event_date=request.POST['event_date'],
				event_time=request.POST['event_time'],
				event_venue=request.POST['event_venue'],
				event_price=request.POST['event_price'],
				event_desc=request.POST['event_desc'],
				event_image=request.FILES['event_image']
			)
		msg="Event Added Successfully"
		return render(request,'manager-add-event.html',{'msg':msg})
	else:
		return render(request,'manager-add-event.html')

def manager_view_event(request):
	manager=User.objects.get(email=request.session['email'])
	events=Event.objects.filter(manager=manager)
	return render(request,'manager-view-event.html',{'events':events})

def manager_edit_event(request,pk):
	event=Event.objects.get(pk=pk)
	if request.method=="POST":
		print(request.POST['event_price'])
		event.event_name=request.POST['event_name']
		event.event_date=request.POST['event_date']
		event.event_time=request.POST['event_time']
		event.event_venue=request.POST['event_venue']
		event.event_price=request.POST['event_price']
		event.event_desc=request.POST['event_desc']
		try:
			event.event_image=request.FILES['event_image']
		except:
			pass
		event.save()
		msg="Event Updated Successfully"
		return render(request,'manager-edit-event.html',{'event':event,'msg':msg})
	else:
		return render(request,'manager-edit-event.html',{'event':event})

def manager_delete_event(request,pk):
	event=Event.objects.get(pk=pk)
	event.delete()
	return redirect('manager-view-event')

def event_details(request,pk):
	event=Event.objects.get(pk=pk)
	return render(request,'event-details.html',{'event':event})

def book_event(request,pk):
	user=User.objects.get(email=request.session['email'])
	event=Event.objects.get(pk=pk)
	BookEvent.objects.create(user=user,event=event)
	events=BookEvent.objects.filter(user=user)
	msg="Event Booked Successfully. Please Proceed For Payment."
	return render(request,'myevents.html',{'events':events,'msg':msg})

def myevent(request):
	user=User.objects.get(email=request.session['email'])
	events=BookEvent.objects.filter(user=user)
	return render(request,'myevents.html',{'events':events})

def checkout(request,pk):
	bookevent=BookEvent.objects.get(pk=pk)
	net_price=bookevent.event.event_price
	return render(request,'checkout.html',{'bookevent':bookevent,'net_price':net_price})