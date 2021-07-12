from django.shortcuts import render
import razorpay
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User
import random
import string

client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET))

@login_required
def payment(request):
    
    current_user = request.user.username

    callback_url = 'payment_handler/'

    notes = {
        'order-type' : 'Mebership',
        'key' : 'value'
        }
    reciept_id = current_user +  ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 7))
    
    order = client.order.create(
            dict(amount=100, 
            currency ="INR",
            payment_capture='0' ) 
        )
    
    context = {
        'razorpay_order_id' : order['id'],
        'razorpay_merchant_key' : settings.RAZORPAY_API_KEY,
        'razorpay_amount' : order['amount'],
        'currency' : order['currency'],
        'callback_url' : callback_url,
        'name' : current_user
    }

    return render(request, "subscription/payment.html", context=context)


@csrf_exempt
def payment_handler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id','')
            signature = request.POST.get('razorpay_signature','')
            params_dict = { 
            'razorpay_order_id': order_id, 
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
            }
            try:
                user1 = User.objects.get(username=request.user.username)
            except:
                return HttpResponse("505 Not Found")
            
           
            result = client.utility.verify_payment_signature(
                params_dict)
            
            
            if result is None:
                amount = 20000  # Rs. 200
                try:
                    client.payment.capture(payment_id, amount)
                  
                    return render(request, 'subscription/success.html', {'paymentid' : payment_id, 'orderid' : order_id} )
                except:
  
                    # if there is an error while capturing payment.
                    return render(request, 'subscription/fail.html', {'paymentid' : payment_id, 'orderid' : order_id})
            else:
  
                # if signature verification fails.
                return render(request, 'subscription/fail.html', {'paymentid' : payment_id, 'orderid' : order_id})
        except:
  
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()