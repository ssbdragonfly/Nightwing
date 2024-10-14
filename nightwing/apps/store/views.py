from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Product


@login_required
def store_view(request):
    products = Product.objects.all()
    return render(request, "store/store.html", {"products": products})


@login_required
def product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, "store/product.html", {"product": product})
