from django.shortcuts import render, get_object_or_404
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import OrderCreated
from django.shortcuts import render, redirect, render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import base64
from Crypto.Cipher import AES
from django.http import Http404
from django.utils.translation import ugettext as _
import hashlib
from urllib.parse import quote
from django.template import RequestContext
import random
import datetime
import weasyprint
import requests
import base64
import json
import math


@staff_member_required
def AdminOrderPDF(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=order_{}.pdf'.format(order.id)
    weasyprint.HTML(string=html).write_pdf(response,
               stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/bootstrap.min.css')])
    return response

@staff_member_required
def AdminOrderDetail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})

def OrderCreate(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        delivery = request.POST['delivery-or-pickup']
        shipping = None
        if 'shipping-method' in request.POST:
            shipping = request.POST['shipping-method']
        if delivery == 'pickup':
            shipping_method = 'Самовывоз'
            ship_price = 0
        elif shipping == 'postpay':
            shipping_method = 'Почта России Наложенный Платеж'
            ship_price = int(request.POST['shipping_cost_postpay'])
        elif shipping == 'post':
            shipping_method = 'Почта России Предоплата'
            ship_price = int(request.POST['shipping_cost_post'])
        elif 'dl_type' in request.POST:
            dellin = request.POST['dl_type']
            if dellin == 'home':
                shipping_method = 'Деловые линии доставка до дома'
                ship_price = int(request.POST['shipping_cost_dl_home'])
            elif dellin == 'terminal':
                shipping_method = 'Деловые линии доставка до терминала'
                ship_price = int(request.POST['shipping_cost_dl_terminal'])        
        if ship_price == '':
            ship_price = 0
        if form.is_valid():
            order = form.save(commit=False)
            order.shipping_method = shipping_method
            order.ship_price = ship_price
            rand = random.randrange(100000, 999999)
            today = datetime.datetime.today()
            time = today.strftime("%Y%m%d%H%M%S")
            order.pageid = time + str(rand)
            if cart.cupon:
                order.cupon = cart.cupon
                order.discount = cart.cupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
             # отправка сообщения
            subject = 'Заказ c номером {}, создан'.format(order.id)
            if shipping_method == 'Почта России Наложенный Платеж':
                message = ''' {}, Ваш заказ, с номером {}, успешно создан.

                Заказ будет обработан и отправлен по почте в ближайшее время.

                Ожидайте трек номер почтового отправления следующим письмом.'''.format(order.name, order.id)
            else:
                message = ''' {}, Ваш заказ, с номером {}, успешно создан.

                Заказ будет обработан и отправлен после предоплаты в размере {} руб.

                Страница для оплаты и управления вашим заказом https://microline.ru/order/{} '''.format(order.name, order.id, str(order.get_total_cost()), order.pageid)
            send_mail(subject, message, 'office@microline.ru', [order.email])
            send_mail(subject, message, 'office@microline.ru', ['office@microline.ru'])
            cart.clear()
            return redirect('orders:OrderPage', pageid=order.pageid)

    form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart,
                                                        'form': form})
#Dostavka
def TestPost(request):
    cart = Cart(request)
    total_price = cart.get_total_price_after_discount()
    total_mass = cart.get_total_mass()
    return render(request, 'orders/order/testpost.html', {'total_price': total_price,
                                                           'total_mass': total_mass})

def round_price(price, n):
    return int(math.ceil(price/n)*n)

#Страница заказа + NetPay
def OrderPage(request, pageid):
    order = get_object_or_404(Order, pageid=pageid)
    API_KEY = "*************"
    AuthSign = '**********'
    url_net2pay_pay = 'https://my.net2pay.ru/billingService/paypage/'
    SUCCESS_URL = 'http://microline.ru/order/*********/'
    FAIL_URL = 'http://microline.ru/order/***********/'

    def md5_base64(text):
        # функция для кодирования текста в md5 с последующим base64
        m = hashlib.md5()
        m.update(text.encode())
        r = m.digest()
        return base64.b64encode(r).decode().strip()

    def crypt_param(val, key):
        #Функция для шифрования параметров AES
        BLOCK_SIZE = 16
        PADDING = chr(BLOCK_SIZE - len(val) % BLOCK_SIZE)
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        cipher = AES.new(key)
        encoded = EncodeAES(cipher, val)
        # print 'Encrypted string:', encoded
        return encoded

    #Создаем нужные ключи для шифрования
    md5_api_key = md5_base64(API_KEY)
    order_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%dV%H:%M:%S")
    # order_date = '2014-06-28V13:39:49'
    crypt_key = md5_base64(md5_api_key + order_date)[:16]
    
    # Формируем параметры
    params = {}
    params['description'] = 'ORDER %s' % order.id
    params['amount'] = order.get_total_cost()
    params['currency'] = 'RUB'
    params['orderID'] = order.id
    params['cardHolderCity'] = ""
    params['cardHolderCountry'] = ""
    params['cardHolderPostal'] = ""
    params['cardHolderRegion'] = ""
    params['successUrl'] = reverse('orders:OrderPageSucc', kwargs={'pageid': order.pageid})
    params['failUrl'] = reverse('orders:OrderPageSucc', kwargs={'pageid': order.pageid})

    shipping_item = []
    if order.ship_price:
        shipping_item = [
            {
                'name': 'Доставка',
                'tax': 'vat18',
                'price': order.ship_price,
                'quantity': 1,
                'sum': order.ship_price
            }
        ]

    cashbox_data = {
        'timestamp': '',
        'service': {
            'inn': '5245028309',
            'payment_address': 'microline.ru',
            'callback_url': ''
        },
        'receipt': {
            'items': [
                {
                    'name': item.product.name,
                    'tax': 'vat18',
                    'price': str(item.price),
                    'quantity': item.quantity,
                    'sum': str(item.get_cost()),
                }
                for item in order.items.all()
            ] + shipping_item,

            'total': str(order.get_total_cost()),
            'payments': [
                {'sum': str(order.get_total_cost()), 'type': 1}
            ],
            'attributes': {
                'email': order.email,
            }
        }
    }
    params['cashbox_data'] = json.dumps(cashbox_data)

    # Шифруем параметры
    params_crypted = []
    for k, v in params.items():
        r = crypt_param('%s=%s' % (k, v), crypt_key).decode()
        params_crypted.append(r)
    data = quote('&'.join(params_crypted))
    
    #данные формы для отправки на Netpay
    context = {}
    context["action"] = url_net2pay_pay
    context["data"] = data
    context["auth"] = AuthSign
    context["order_date"] = quote(order_date)

    return render(request, 'netpay_payment.html', {'order': order, **context})

def OrderPageSucc(request, pageid):
    order = get_object_or_404(Order, pageid=pageid)
    order.paid = True
    order.save()
     # отправка сообщения
    subject = 'Статус заказа, c номером {}, изменен.'.format(order.id)
    message = ''' {}, Заказ, с номером {}, успешно оплачен.

    Заказ будет отправлен в службу доставки в ближайшее время.'''.format(order.name, order.id)
    send_mail(subject, message, '*******@microline.ru', [order.email])
    return render(request, 'orders/order/*********.html', {'order': order})

def OrderPageFail(request, pageid):
    order = get_object_or_404(Order, pageid=pageid)
    return render(request, 'orders/order/*******.html', {'order': order})

#Подтверждение от NETPAY    
def ConfirmPay(request):
    if request.method == 'GET':
        orderID = request.GET['orderID']
        transactionType = request.GET['transactionType']
        status = request.GET['status']
        order = get_object_or_404(Order, id=orderID)
        cont = {}
        if status == 'APPROVED':
            order.paid = True
            order.status = 'confirmed'
            order.save()
             # отправка сообщения
            subject = 'Статус заказа, c номером {}, изменен.'.format(order.id)
            message = ''' {}, Заказ, с номером {}, успешно оплачен.

            Заказ будет отправлен в службу доставки в ближайшее время.'''.format(order.name, order.id)
            send_mail(subject, message, 'office@microline.ru', [order.email])
            cont['orderID'] = orderID
            cont['transactionType'] = transactionType
            cont['status'] = 1
        else:
            cont['orderID'] = orderID
            cont['transactionType'] = transactionType
            cont['status'] = 0
        return render(request, 'confpay.xml', {**cont})    

#Russianpost
def russian_post(request):
    def to_base64(str):
        return base64.b64encode(str.encode()).decode("utf-8")

    cart = Cart(request)
    total_price = cart.get_total_price_after_discount()
    total_mass = cart.get_total_mass()
    index = request.POST['postindex']
    #properties
    access_token    = "*************"
    protocol    = "https://"
    host        = "otpravka-api.pochta.ru"
    key         = "******************"

    request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json;charset=UTF-8",
        "Authorization": "AccessToken " + access_token,
        "X-User-Authorization": "Basic " + key
    }

    path = "/1.0/tariff"

    destination = {
        "index-from": "603101",
        "index-to": index,
        "mail-category": "WITH_DECLARED_VALUE",
        "mail-type": "POSTAL_PARCEL",
        "mass": total_mass,
        "declared-value": int(total_price)*100,
        "rcp-pays-shipping": "false",
        "fragile": "false"
    }
    url = protocol + host + path
    try:
        response = requests.post(url, headers=request_headers, json=destination)
    except requests.exceptions.RequestException as err:
        print(err)
    r = response.json()
    sum_totall = round_price((r['total-rate'] + r['total-vat']) / 100, 20)
    #calc postpay
    destination['declared-value'] = (sum_totall + int(total_price))*100 
    try:
        response2 = requests.post(url, headers=request_headers, json=destination)
    except requests.exceptions.RequestException as err:
        print(err)
    r2 = response2.json()
    sum_totall2 = round_price((r2['total-rate'] + r2['total-vat']) / 100, 20)
    #calc nalogenny platezh
    if int(total_price) + sum_totall < 1000:
        fee = 80 + (int(total_price) + sum_totall) * 5 / 100
    elif int(total_price) + sum_totall >= 1000 and int(total_price) + sum_totall < 5000:
        fee = 90 + (int(total_price) + sum_totall) * 4 / 100
    elif int(total_price) + sum_totall >= 5000 and int(total_price) + sum_totall < 20000:
        fee = 190 + (int(total_price) + sum_totall) * 2 / 100
    elif int(total_price) + sum_totall >= 20000:
        fee = 290 + (int(total_price) + sum_totall) * 1.5 / 100
    return {
            "post_postpay": sum_totall2,
            "post_postpay_fee": fee,
            "post_prepay": sum_totall
    }
    
#Dellin
def dellin(request):
    cart = Cart(request)
    total_price = cart.get_total_price_after_discount()
    total_mass = cart.get_total_mass() / 1000
    total_size = cart.get_total_size()
    index = request.POST['postindex']
    #properties
    request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json;charset=UTF-8",
    }
    destination = {
        "appkey" : "***********************",
        "derivalPoint" : "5200000100000000000000000",
        "derivalDoor" : "false",
        "arrivalPoint" : index,
        "arrivalDoor" : "true",
        "sizedVolume": total_size,
        "sizedWeight": total_mass,
    }
    url = 'https://api.dellin.ru/v1/public/calculator.json'
    response = requests.post(url, headers=request_headers, json=destination)
    r = response.json()
    ship_price = r['price']
    terminals = r['arrival']['terminals']
    return {
            "cost_home": float(r['price']),
            "cost_terminal": float(r['intercity']['price']) + float(r['notify']['price']) + float(r['insurance']) + float(r['derival']['price']) + float(r['arrival']['terminals'][0]['price']),
            "terminals": [
                {
                    'name': terminal['name'],
                    'address': terminal['address'],
                    'link': f'https://www.dellin.ru/contacts/{terminal["id"]}/'
                }
                for terminal in terminals
            ],
    }

@csrf_exempt
def delivery_cost(request):
    post_dict = russian_post(request)
    try:
        post_dict['dl'] = dellin(request)
    except:
        pass
    return JsonResponse(post_dict)

    
