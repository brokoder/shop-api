from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import PurchaseOrder, LineItem, Supplier
from .serializers import PurchaseOrderSerializer

class PurchaseOrderViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "supplier": {
                "name": "Test Supplier",
                "email": "test@test.com"
            },
            "line_items": [
                {
                    "item_name": "Test Item",
                    "quantity": 1,
                    "price_without_tax": "10.00",
                    "tax_name": "GST 5%",
                    "tax_amount": "0.50"
                }
            ]
        }

    def test_create_valid_purchase_order(self):
        valid_payload = {
            "supplier": {
                "name": "Test Supplier",
                "email": "test@test.com"
            },
            "line_items": [
                {
                    "item_name": "Test Item",
                    "quantity": 1,
                    "price_without_tax": "10.00",
                    "tax_name": "GST 5%",
                    "tax_amount": "0.50"
                }
            ]
        }
        url = reverse('purchase-order')
        response = self.client.post(url, valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseOrder.objects.count(), 1)
        self.assertEqual(LineItem.objects.count(), 1)
        self.assertEqual(Supplier.objects.count(), 1)

    def test_create_invalid_purchase_order(self):
        invalid_payload = {
            # Invalid payload without required fields
            "line_items": [
                {
                    "item_name": "Test Item",
                    "quantity": 1,
                    "price_without_tax": "10.00",
                    "tax_name": "GST 5%",
                    "tax_amount": "0.50"
                }
            ]
        }
        url = reverse('purchase-order')
        response = self.client.post(url, invalid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PurchaseOrder.objects.count(), 0)
        self.assertEqual(LineItem.objects.count(), 0)
        self.assertEqual(Supplier.objects.count(), 0)
    
    def test_get_all_purchase_orders(self):
        self.supplier = Supplier.objects.create(name='Test Supplier', email='test@test.com')
        self.purchase_order_1 = PurchaseOrder.objects.create(supplier=self.supplier, total_quantity=1, total_amount=10.5, total_tax=0.5)
        self.purchase_order_2 = PurchaseOrder.objects.create(supplier=self.supplier, total_quantity=2, total_amount=42.0, total_tax=2)
        self.line_item_1 = LineItem.objects.create(purchase_order=self.purchase_order_1, item_name='Test Item 1', quantity=1, price_without_tax=10.00, tax_name='GST 5%', tax_amount=0.50,line_total=10.50)
        self.line_item_2 = LineItem.objects.create(purchase_order=self.purchase_order_2, item_name='Test Item 2', quantity=2, price_without_tax=20.00, tax_name='GST 10%', tax_amount=1.00,line_total=42.0)

        url = reverse('purchase-order')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        purchase_orders = PurchaseOrder.objects.all()
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        self.assertEqual(response.data, serializer.data)

class PurchaseOrderIDViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.supplier,_ = Supplier.objects.get_or_create(name='Test Supplier', email='test@test.com')
        self.purchase_order = PurchaseOrder.objects.create(supplier=self.supplier, total_quantity=1, total_amount=10.5, total_tax=0.5)
        self.line_item = LineItem.objects.create(purchase_order=self.purchase_order, item_name='Test Item', quantity=1, price_without_tax=10.00, tax_name='GST 5%', tax_amount=0.50,line_total=10.50)

    def test_get_purchase_order(self):
        url = reverse('purchase-order-id', kwargs={'record_id': self.purchase_order.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer_data = PurchaseOrderSerializer(instance=self.purchase_order).data
        self.assertEqual(response.data, serializer_data)

    def test_get_nonexistent_purchase_order(self):
        non_existent_id = 9999
        url = reverse('purchase-order-id', kwargs={'record_id': non_existent_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_valid_purchase_order(self):
        valid_payload = {
            "id": 1,
            "supplier": {
                "id": 1,
                "name": "Updated Supplier",
                "email": "updated@test.com"
            },
            "line_items": [
                {
                    "id": self.line_item.id,
                    "item_name": "Updated Item",
                    "quantity": 2,
                    "price_without_tax": "20.00",
                    "tax_name": "GST 10%",
                    "tax_amount": "2.00"
                },
                {
                    "item_name": "New Item",
                    "quantity": 3,
                    "price_without_tax": "30.00",
                    "tax_name": "GST 15%",
                    "tax_amount": "4.50"
                }
            ]
        }
        url = reverse('purchase-order-id', kwargs={'record_id': self.purchase_order.id})
        response = self.client.put(url, valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED )
        updated_purchase_order = PurchaseOrder.objects.get(id=self.purchase_order.id)
        self.assertEqual(updated_purchase_order.supplier.name, "Updated Supplier")
        self.assertEqual(updated_purchase_order.supplier.email, "updated@test.com")
        self.assertEqual(updated_purchase_order.line_items.count(), 2)
        updated_line_item = LineItem.objects.get(id=self.line_item.id)
        self.assertEqual(updated_line_item.item_name, "Updated Item")
        self.assertEqual(updated_line_item.quantity, 2)
        self.assertEqual(updated_line_item.price_without_tax, 20.00)
        self.assertEqual(updated_line_item.tax_name, "GST 10%")
        self.assertEqual(updated_line_item.tax_amount, 2.00)

    def test_update_invalid_purchase_order(self):
        invalid_payload = {
            # Invalid payload without required fields
            "supplier": {
                "id": self.supplier.id,
                "name": "Updated Supplier",
                "email": "updated@test.com"
            }
            # Missing line_items
        }
        url = reverse('purchase-order-id', kwargs={'record_id': self.purchase_order.id})
        response = self.client.put(url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        updated_purchase_order = PurchaseOrder.objects.get(id=self.purchase_order.id)
        self.assertNotEqual(updated_purchase_order.supplier.name, "Updated Supplier")


    def test_delete_purchase_order_and_line_items(self):
        url = reverse('purchase-order-id', kwargs={'record_id': self.purchase_order.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PurchaseOrder.objects.filter(id=self.purchase_order.id).exists())
        self.assertFalse(LineItem.objects.filter(id=self.line_item.id).exists())

    def test_delete_nonexistent_purchase_order(self):
        non_existent_id = 9999
        url = reverse('purchase-order-id', kwargs={'record_id': non_existent_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
