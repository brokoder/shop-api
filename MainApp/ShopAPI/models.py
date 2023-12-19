from django.db import models


class Supplier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now_add=True)
    order_number = models.IntegerField(unique=True)
    total_quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = PurchaseOrder.objects.last()
            if last_order:
                self.order_number = last_order.order_number + 1
            else:
                self.order_number = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} - {self.supplier}"


class LineItem(models.Model):
    id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price_without_tax = models.DecimalField(max_digits=10, decimal_places=2)
    tax_name = models.CharField(max_length=100)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_order = models.ForeignKey(
        PurchaseOrder, related_name="line_items", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.item_name} - Order {self.purchase_order.order_number}"
