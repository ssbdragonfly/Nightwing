from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.store_view, name="store"),
    path("<int:product_id>/", views.product_view, name="detail"),
    path("buy/", views.buy_product, name="buy"),
]
