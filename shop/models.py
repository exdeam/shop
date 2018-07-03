from django.db import models
from django.core.urlresolvers import reverse
from tinymce.models import HTMLField

# Модель категории
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name='Имя')
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    image = models.ImageField(upload_to='category/%Y/%m/%d/', blank=True, verbose_name="Изображение Категории")

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:ProductListByCategory', args=[self.slug])


# Модель продукта
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', verbose_name="Категория")
    name = models.CharField(max_length=200, db_index=True, verbose_name="Название")
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, verbose_name="Изображение товара")
    opisanie = HTMLField(default=True, verbose_name="Описание")
    tech = HTMLField(default=True, verbose_name="Технические характеристики")
    complects = HTMLField(default=True, verbose_name="Комплектация")
    docs = HTMLField(default=True, verbose_name="Документация")
    photo = HTMLField(default=True, verbose_name="Фотогалерея")
    video = HTMLField(default=True, verbose_name="Видеообзоры")
    price = models.IntegerField(verbose_name="Цена")
    sku = models.CharField(default=True, max_length=200, verbose_name="Артикул")
    size = models.FloatField(default=0.003, verbose_name="Размер")
    mass = models.IntegerField(default=100, verbose_name="Вес")
    stock = models.PositiveIntegerField(verbose_name="На складе")
    available = models.BooleanField(default=True, verbose_name="Доступен")
    dopproduct = models.BooleanField(default=False, verbose_name="Допоборудование")
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        ordering = ['slug']
        index_together = [
            ['id', 'slug']
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:ProductDetail', args=[self.id, self.slug])
