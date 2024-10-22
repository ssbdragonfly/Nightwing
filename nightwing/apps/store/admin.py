from django.contrib import admin

from .models import Credit, Product

admin.site.register(Product)
admin.site.register(Credit)
