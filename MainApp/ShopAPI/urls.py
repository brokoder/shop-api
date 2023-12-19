from django.urls import path
from .views import PurchaseOrderView, PurchaseOrderIDView

urlpatterns = [
    path("purchase/orders/", PurchaseOrderView.as_view(), name="purchase-order"),
    path(
        "purchase/orders/<int:record_id>/",
        PurchaseOrderIDView.as_view(),
        name="purchase-order",
    ),
]
