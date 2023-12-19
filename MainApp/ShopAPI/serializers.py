from rest_framework import serializers
from .models import Supplier, PurchaseOrder, LineItem
from .response_formatter import purchase_order_formatter

class SupplierSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(allow_null=True, required=False)
    class Meta:
        model = Supplier
        fields = ("id","name","email")

class LineItemPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(allow_null=True, required=False)
    class Meta:
        model = LineItem
        fields = ('id','item_name', 'quantity', 'price_without_tax', 'tax_name', 'tax_amount')

class PurchaseOrderMutateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(allow_null=True, required=False)
    supplier = SupplierSerializer()
    line_items = LineItemPostSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = ('id','supplier', 'line_items')

    def create(self, validated_data):
        supplier_data = validated_data['supplier']
        line_items_data = validated_data['line_items']
        if supplier_data.get("id"):
            supplier = Supplier.objects.get(id=supplier_data.get("id"))
            supplier.name = supplier_data["name"]
            supplier.email = supplier_data["email"]
            supplier.save()
        else:
            supplier, _ = Supplier.objects.get_or_create(**supplier_data)
        supplier_data["id"] = supplier.id
        purchase_order = PurchaseOrder.objects.create(
            supplier=supplier,
            total_quantity = 0,
            total_amount = 0,
            total_tax = 0
        )
        _total_amount = 0
        _total_quantity = 0
        _total_tax = 0
        for line_item_data in line_items_data:
            _total_amount += (int(line_item_data['quantity']) * (float(line_item_data['price_without_tax']) + float(line_item_data['tax_amount'])))
            _total_quantity += int(line_item_data['quantity'])
            _total_tax += int(line_item_data['quantity']) * float(line_item_data['tax_amount'])
            line_item_data["line_total"] = line_item_data["quantity"] * (line_item_data["price_without_tax"]+ line_item_data["tax_amount"])
            line_item = LineItem.objects.create(purchase_order=purchase_order, **line_item_data)
            line_item_data["id"] = line_item.id
        purchase_order.total_amount = _total_amount
        purchase_order.total_quantity = _total_quantity
        purchase_order.total_tax = _total_tax
        purchase_order.save()
        response_data = purchase_order_formatter(purchase_order, supplier_data, line_items_data)
        return response_data
    
    def update(self, purchase_order, validated_data):
        supplier_data = validated_data['supplier']
        line_items_data = validated_data['line_items']
        if supplier_data.get('id'):
            purchase_order.supplier.id = supplier_data.get('id')
            purchase_order.supplier.name = supplier_data.get('name')
            purchase_order.supplier.email = supplier_data.get('email')
            purchase_order.supplier.save()
        existing_line_item_ids = set(purchase_order.line_items.values_list('id', flat=True))
        _total_amount = 0
        _total_quantity = 0
        _total_tax = 0
        for line_item_data in line_items_data:
            line_item_id = line_item_data.get('id')
            line_item_data["line_total"] = line_item_data["quantity"] * (line_item_data["price_without_tax"]+ line_item_data["tax_amount"])
            if line_item_id:
                # Update existing line items
                if line_item_id in existing_line_item_ids:
                    _total_amount += (int(line_item_data['quantity']) * (float(line_item_data['price_without_tax']) + float(line_item_data['tax_amount'])))
                    _total_quantity += int(line_item_data['quantity'])
                    _total_tax += int(line_item_data['quantity']) * float(line_item_data['tax_amount'])
                    line_item = LineItem.objects.get(pk=line_item_id, purchase_order=purchase_order)
                    for attr, value in line_item_data.items():
                        setattr(line_item, attr, value)
                    line_item.save()
                    existing_line_item_ids.remove(line_item_id)
                else:
                    # If an ID is given but not found in the current line items, skip
                    continue
            else:
                # Create new line items
                _total_amount += (int(line_item_data['quantity']) * (float(line_item_data['price_without_tax']) + float(line_item_data['tax_amount'])))
                _total_quantity += int(line_item_data['quantity'])
                _total_tax += int(line_item_data['quantity']) * float(line_item_data['tax_amount'])
                line_item = LineItem.objects.create(purchase_order=purchase_order, **line_item_data)
                line_item_data["id"] = line_item.id
        # Delete line items that were not updated or created
        LineItem.objects.filter(id__in=existing_line_item_ids).delete()
        response_data =purchase_order_formatter(purchase_order, validated_data["supplier"], line_items_data)
        purchase_order.total_amount = _total_amount
        purchase_order.total_quantity = _total_quantity
        purchase_order.total_tax = _total_tax
        purchase_order.save()
        return response_data

class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = ('id', 'item_name', 'quantity', 'price_without_tax', 'tax_name', 'tax_amount', 'line_total')

class PurchaseOrderSerializer(serializers.ModelSerializer):
    line_items = LineItemSerializer(many=True, read_only=True)
    supplier = SupplierSerializer(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ('id', 'supplier', 'order_number', 'order_time', 'total_amount', 'total_quantity', 'total_tax', 'line_items')