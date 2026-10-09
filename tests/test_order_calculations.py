import pytest
from models.food import Food
from models.order import Order
from models.bill import Bill
from models.order_item import OrderItem


def test_order_subtotal_and_tax_without_discount(staff_client):
    """
    Validate standard order calculation:
    2 Dosa (@100 = 200) + 1 Biryani (@240 = 240)
    Subtotal = 440.00
    Discount (0%) = 0.00
    Taxable = 440.00
    GST (5%) = 22.00
    Grand Total = 462.00
    """
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    biryani = Food.query.filter_by(name='Test Chicken Biryani').first()

    payload = {
        'customer_name': 'Ramesh Kumar',
        'table_number': 'Table 1',
        'order_type': 'Dine-In',
        'payment_method': 'Cash',
        'discount_pct': 0,
        'items': [
            {'food_id': dosa.id, 'quantity': 2},
            {'food_id': biryani.id, 'quantity': 1}
        ]
    }

    res = staff_client.post('/api/orders', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True

    order = data['order']
    assert order['subtotal'] == 440.00
    assert order['discount'] == 0.00
    assert order['gst'] == 22.00
    assert order['grand_total'] == 462.00

    # Verify corresponding Bill created with exact matching amounts
    bill = data['bill']
    assert bill['subtotal'] == 440.00
    assert bill['discount'] == 0.00
    assert bill['gst'] == 22.00
    assert bill['grand_total'] == 462.00
    assert bill['order_id'] == order['id']


def test_order_calculation_with_percentage_discount(staff_client):
    """
    Validate discount calculation:
    Subtotal = 440.00
    Discount (10%) = 44.00
    Taxable = 396.00
    GST (5%) = 19.80
    Grand Total = 415.80
    """
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    biryani = Food.query.filter_by(name='Test Chicken Biryani').first()

    payload = {
        'customer_name': 'Priya Sharma',
        'table_number': 'Table 5',
        'order_type': 'Dine-In',
        'payment_method': 'UPI / GPay',
        'discount_pct': 10,
        'items': [
            {'food_id': dosa.id, 'quantity': 2},
            {'food_id': biryani.id, 'quantity': 1}
        ]
    }

    res = staff_client.post('/api/orders', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    order = data['order']

    assert order['subtotal'] == 440.00
    assert order['discount'] == 44.00
    assert order['gst'] == 19.80
    assert order['grand_total'] == 415.80


def test_order_discount_clamping_negative_and_excessive(staff_client):
    """Validate that discount is clamped between 0% and 100%."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()

    # Negative discount (-20%) must be clamped to 0%
    neg_payload = {
        'customer_name': 'Clamp Test Neg',
        'table_number': 'Table 2',
        'discount_pct': -20,
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    }
    res_neg = staff_client.post('/api/orders', json=neg_payload)
    assert res_neg.status_code == 201
    order_neg = res_neg.get_json()['order']
    assert order_neg['discount'] == 0.00
    assert order_neg['grand_total'] == 105.00  # 100 + 5% GST

    # >100% discount (150%) must be clamped to 100%
    excess_payload = {
        'customer_name': 'Clamp Test Excess',
        'table_number': 'Table 2',
        'discount_pct': 150,
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    }
    res_excess = staff_client.post('/api/orders', json=excess_payload)
    assert res_excess.status_code == 201
    order_excess = res_excess.get_json()['order']
    assert order_excess['discount'] == 100.00
    assert order_excess['gst'] == 0.00
    assert order_excess['grand_total'] == 0.00


def test_order_empty_items_validation(staff_client):
    """An order with no items must be rejected with 400 Bad Request."""
    payload = {
        'customer_name': 'Empty Order',
        'table_number': 'Table 3',
        'items': []
    }
    res = staff_client.post('/api/orders', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert 'Order cannot be empty' in data['error']


def test_order_invalid_quantity_validation(staff_client):
    """Zero, negative, or non-integer quantities must be rejected."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()

    # Zero quantity
    res_zero = staff_client.post('/api/orders', json={
        'customer_name': 'Zero Qty',
        'table_number': 'Table 1',
        'items': [{'food_id': dosa.id, 'quantity': 0}]
    })
    assert res_zero.status_code == 400

    # Negative quantity
    res_neg = staff_client.post('/api/orders', json={
        'customer_name': 'Negative Qty',
        'table_number': 'Table 1',
        'items': [{'food_id': dosa.id, 'quantity': -3}]
    })
    assert res_neg.status_code == 400

    # String non-integer
    res_str = staff_client.post('/api/orders', json={
        'customer_name': 'String Qty',
        'table_number': 'Table 1',
        'items': [{'food_id': dosa.id, 'quantity': 'invalid'}]
    })
    assert res_str.status_code == 400


def test_order_unavailable_dish_rejection(staff_client):
    """Dishes marked is_available=False must be rejected."""
    unavailable = Food.query.filter_by(name='Test Seasonal Halwa').first()
    assert unavailable.is_available is False

    res = staff_client.post('/api/orders', json={
        'customer_name': 'Unavailable Test',
        'table_number': 'Table 4',
        'items': [{'food_id': unavailable.id, 'quantity': 1}]
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert 'unavailable' in data['error'].lower()


def test_order_missing_required_fields(staff_client):
    """Missing customer name or table number must fail validation."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()

    # Missing customer name
    res1 = staff_client.post('/api/orders', json={
        'customer_name': '   ',
        'table_number': 'Table 1',
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    })
    assert res1.status_code == 400

    # Missing table number
    res2 = staff_client.post('/api/orders', json={
        'customer_name': 'Valid Name',
        'table_number': '',
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    })
    assert res2.status_code == 400


def test_order_nonexistent_dish(staff_client):
    """Ordering a non-existent dish ID returns 404."""
    res = staff_client.post('/api/orders', json={
        'customer_name': 'Ghost Dish',
        'table_number': 'Table 1',
        'items': [{'food_id': 99999, 'quantity': 1}]
    })
    assert res.status_code == 404
    data = res.get_json()
    assert data['success'] is False


def test_order_calculation_with_service_charge(staff_client):
    """
    Validate service charge calculation:
    Subtotal = 100.00, GST (5%) = 5.00, Service Charge (10%) = 10.00
    Grand Total = 115.00
    """
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    payload = {
        'customer_name': 'Service Charge Test',
        'table_number': 'Table 9',
        'discount_pct': 0,
        'service_charge_pct': 10,
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    }
    res = staff_client.post('/api/orders', json=payload)
    assert res.status_code == 201
    order = res.get_json()['order']
    assert order['subtotal'] == 100.00
    assert order['gst'] == 5.00
    assert order['service_charge'] == 10.00
    assert order['grand_total'] == 115.00


def test_order_creates_payment_record(staff_client):
    """Creating an order generates a linked Payment record with amount and payment_status."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    payload = {
        'customer_name': 'Payment Test Customer',
        'table_number': 'Table 3',
        'payment_method': 'UPI / GPay',
        'items': [{'food_id': dosa.id, 'quantity': 2}]
    }
    res = staff_client.post('/api/orders', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert 'payment' in data
    payment = data['payment']
    assert payment['amount'] == 210.00  # 200 + 5% GST = 210
    assert payment['payment_method'] == 'UPI / GPay'
    assert payment['payment_status'] == 'Paid'
    assert payment['order_id'] == data['order']['id']


def test_order_status_update_flow(staff_client):
    """Staff can update order status (Pending -> Preparing -> Ready -> Completed)."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    order_res = staff_client.post('/api/orders', json={
        'customer_name': 'Status Flow Customer',
        'table_number': 'Table 6',
        'status': 'Pending',
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    })
    order_id = order_res.get_json()['order']['id']
    assert order_res.get_json()['order']['status'] == 'Pending'

    # Update to Preparing
    patch_res = staff_client.patch(f'/api/orders/{order_id}/status', json={'status': 'Preparing'})
    assert patch_res.status_code == 200
    assert patch_res.get_json()['order']['status'] == 'Preparing'

    # Update to Ready
    patch_res2 = staff_client.patch(f'/api/orders/{order_id}/status', json={'status': 'Ready'})
    assert patch_res2.status_code == 200
    assert patch_res2.get_json()['order']['status'] == 'Ready'


def test_order_payment_status_update(staff_client):
    """Updating payment status synchronizes across order, bill, and payment."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    order_res = staff_client.post('/api/orders', json={
        'customer_name': 'Refund Test Customer',
        'table_number': 'Table 8',
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    })
    order_id = order_res.get_json()['order']['id']
    bill_id = order_res.get_json()['bill']['id']

    # Update payment status via order endpoint
    patch_res = staff_client.patch(f'/api/orders/{order_id}/status', json={'payment_status': 'Refunded'})
    assert patch_res.status_code == 200
    assert patch_res.get_json()['order']['payment_status'] == 'Refunded'

    # Verify bill reflects updated payment status
    bill_res = staff_client.get(f'/api/bills/{bill_id}')
    assert bill_res.status_code == 200
    assert bill_res.get_json()['bill']['payment_status'] == 'Refunded'

    # Update via bill payment-status endpoint
    bill_patch = staff_client.patch(f'/api/bills/{bill_id}/payment-status', json={'payment_status': 'Paid'})
    assert bill_patch.status_code == 200
    assert bill_patch.get_json()['bill']['payment_status'] == 'Paid'


def test_order_invalid_status_rejected(staff_client):
    """Submitting invalid status or payment_status returns 400 Bad Request."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    order_res = staff_client.post('/api/orders', json={
        'customer_name': 'Bad Status Test',
        'table_number': 'Table 1',
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    })
    order_id = order_res.get_json()['order']['id']

    # Invalid order status
    bad_status = staff_client.patch(f'/api/orders/{order_id}/status', json={'status': 'InvalidStatusName'})
    assert bad_status.status_code == 400
    assert bad_status.get_json()['success'] is False

    # Invalid payment status
    bad_pay = staff_client.patch(f'/api/orders/{order_id}/status', json={'payment_status': 'UnknownStatus'})
    assert bad_pay.status_code == 400
    assert bad_pay.get_json()['success'] is False


def test_payments_api_listing(staff_client):
    """Staff can list all recorded payments via /api/payments."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    staff_client.post('/api/orders', json={
        'customer_name': 'Listing Payment Customer',
        'table_number': 'Table 12',
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    })
    res = staff_client.get('/api/payments')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['count'] >= 1
    assert any(p['payment_method'] == 'Cash' for p in data['payments'])
