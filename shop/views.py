from django.shortcuts import render
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum

# Create your views here.
from django.http import HttpResponse

MERCHANT_KEY = 'Vz27mm5IxGCV#AGB';

def index(request):
    allProds = []
    # Fetching the Category
    catprods = Product.objects.values('category')
    # Fetching the item's category for items linked with categories.
    cats = {item['category'] for item in catprods}

    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds}

    return render(request, 'shop/index.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html',{'thank':thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates,order[0].items_json],default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')


def search(request):

    return render(request, 'shop/search.html')


def productView(request, myid):
    # Fetch the product using the id.
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product': product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        amount = request.POST.get('amount', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + \
            " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone_number = request.POST.get('phone_number', '')
        orders = Order(items_json=items_json, name=name, email=email, address=address,
                       city=city, state=state, zip_code=zip_code, phone_number=phone_number,amount=amount)
        orders.save()
        update = OrderUpdate(order_id=orders.order_id,
                             update_desc="The order has been placed")
        update.save()
        id = orders.order_id
        thank = True

        # return render(request, 'shop/checkout.html', {'thank': thank, 'id': id})
        # request paytm to transfer the amount to your account after payment by user
        param_dict = {
            'MID': 'qLCrPl26522047936443',
            'ORDER_ID': str(orders.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': 'email',
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})
    return render(request, 'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE']=='01':
            print('order successful')
        else:
            print('order was not succesful because' +response_dict['RESPMSG'])
    return render(request,'shop/paymentstatus.html',{'response':response_dict})