def purchase_order_formatter(purchase_order, supplier_data, line_items_data):
    response_data = {
        "data": {
            "type": "purchase-orders",
            "id": purchase_order.id,
            "attributes": {
                "total_amount": purchase_order.total_amount,
                "total_quantity": purchase_order.total_quantity,
                "total_tax": purchase_order.total_tax,
                "order_number": purchase_order.order_number,
                "order_time": purchase_order.order_time.isoformat(),
            },
            "relationships": {
                "supplier": {
                    "data": {
                        "type": "suppliers",
                        "id": supplier_data["id"],
                    },
                    "attributes": {
                        "name": supplier_data["name"],
                        "email": supplier_data["email"],
                    },
                },
                "line_items": [
                    {
                        "data": {
                            "type": "line_items",
                            "id": line_item_data["id"],
                        },
                        "attributes": {
                            "item_name": line_item_data["item_name"],
                            "quantity": line_item_data["quantity"],
                            "price_without_tax": line_item_data["price_without_tax"],
                            "tax_name": line_item_data["tax_name"],
                            "tax_amount": line_item_data["tax_amount"],
                            "line_total": line_item_data["line_total"],
                        },
                    }
                    for line_item_data in line_items_data
                ],
            },
        }
    }
    return response_data
