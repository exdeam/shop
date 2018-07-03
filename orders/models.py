from django.db import models
from shop.models import Product
from cupons.models import Cupon
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

STATUS_CHOICES = (
    ('new', 'Принят'),
    ('confirmed', 'Подтвержден'),
    ('processing','Обрабатывается'),
    ('sended','Отправлен'),
    ('canceled','Отменен')
    )

class Order(models.Model):
    name = models.CharField(verbose_name='Фамилия Имя Отчество', max_length=120, null=True)
    email = models.EmailField(verbose_name='Email', blank=True)
    phone =  models.CharField(verbose_name='Телефон', max_length=30, blank=True)
    address =  models.CharField(verbose_name='Адрес', max_length=250, blank=True)
    postal_code = models.CharField(verbose_name='Почтовый индекс', max_length=20, blank=True)
    city = models.CharField(verbose_name='Город', max_length=100, blank=True)
    created = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Обновлен', auto_now=True)
    ship_price = models.IntegerField(verbose_name="Цена доставки", blank=True, null=True) 
    paid = models.BooleanField(verbose_name='Оплачен', default=False)
    shipping_method = models.CharField(verbose_name='Доставка', max_length=120, blank=True)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    admin_comment = models.TextField(verbose_name="Коментарий администратора", blank=True)
    pageid = models.CharField(max_length=200, db_index=True, verbose_name="Страница заказа")
    cupon = models.ForeignKey(Cupon, related_name='orders', null=True, blank=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0),
                                                          MaxValueValidator(100)])

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return 'Заказ: {}'.format(self.id)

    def get_total_cost(self):
        if self.ship_price is not None:
            ship_price = self.ship_price
        else: ship_price = 0
        total_cost = sum(item.get_cost() for item in self.items.all()) + ship_price
        return total_cost - total_cost * (self.discount / Decimal('100'))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items')
    product = models.ForeignKey(Product, related_name='order_items')
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity
