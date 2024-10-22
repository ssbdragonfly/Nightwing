from django import http
from django.db import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Credit, Product


@login_required
def store_view(request):
    products = Product.objects.all()
    return render(
        request,
        "store/store.html",
        {"products": products, "credits": Credit.get_credit(request.user)},
    )


@login_required
def product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(
        request,
        "store/product.html",
        {"product": product, "credits": Credit.get_credit(request.user)},
    )


@login_required
@require_POST
@csrf_exempt
def buy_product(request):
    if product_id := request.POST.get("product_id"):
        product = Product.objects.get(id=product_id)
        credits = Credit.get_credit(request.user)
        if credits.money >= product.price:
            credits.money = models.F("money") - product.price
            credits.save(update_fields=["money"])
            return http.JsonResponse({"success": True})
    raise http.Http404
