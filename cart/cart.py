from decimal import Decimal
from django.conf import settings
from shop.models import Product
from cupons.models import Cupon


class Cart(object):
    def __init__(self, request):
        # Инициализация корзины пользователя
        self.session = request.session
        self.cupon_id = self.session.get('cupon_id')
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Сохраняем корзину пользователя в сессию
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    # Добавление товара в корзину пользователя или обновление количеста товара
    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    # Сохранение данных в сессию
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        # Указываем, что сессия изменена
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # Итерация по товарам
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    # Количество товаров
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def get_total_mass(self):
        # product_ids = self.cart.keys()
        # return sum((product.mass for product in Product.objects.filter(id__in=product_ids)) * item['quantity'] for item in self.cart.values()) 
        qtys = {
            int(product_id): item['quantity']
            for product_id, item in self.cart.items()
        }
        masses = {
            product.id: product.mass
            for product in Product.objects.filter(id__in=qtys.keys())
        }
        return sum(
            qty * masses.get(product_id, 0)
            for product_id, qty in qtys.items()
        )
    def get_total_size(self):
        qtys = {
            int(product_id): item['quantity']
            for product_id, item in self.cart.items()
        }
        sizeall = {
            product.id: product.size
            for product in Product.objects.filter(id__in=qtys.keys())
        }
        return sum(
            qty * sizeall.get(product_id, 0)
            for product_id, qty in qtys.items()
        )


    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    @property
    def cupon(self):
        if self.cupon_id:
            return Cupon.objects.get(id=self.cupon_id)
        return None

    def get_discount(self):
        if self.cupon:
            return (self.cupon.discount / Decimal('100')) * self.get_total_price()
        return Decimal('0')

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()

         
