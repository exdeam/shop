from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^create/$', views.OrderCreate, name='OrderCreate'),
    url(r'^testpost/$', views.delivery_cost, name='delivery_cost'),
    url(r'^confirmpay/$', views.ConfirmPay, name='ConfirmPay'),
    url(r'^(?P<pageid>\d+)/$', views.OrderPage, name='OrderPage'),
    url(r'^success/(?P<pageid>\d+)/$', views.OrderPageSucc, name='OrderPageSucc'),
    url(r'^fail/(?P<pageid>\d+)/$', views.OrderPageFail, name='OrderPageFail'),
    url(r'^admin/order/(?P<order_id>\d+)/$', views.AdminOrderDetail, name='AdminOrderDetail'),
    url(r'^admin/order/(?P<order_id>\d+)/pdf/$', views.AdminOrderPDF, name='AdminOrderPDF')
]
