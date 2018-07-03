from django.contrib import admin
from .models import Category, Product
from django import forms

# Модель категории
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name', )}


# Модель товара
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'sku', 'mass', 'size', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'sku', 'mass', 'size', 'stock', 'available']
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)