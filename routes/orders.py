from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models import db
from models.order import Order
from models.order_item import OrderItem
from models.bill import Bill
from models.payment import Payment
from models.food import Food
from routes.auth import login_required

orders_bp = Blueprint('orders', __name__)

def generate_order_number():
    last_order = Order.query.order_by(Order.id.desc()).first()
    next_num = 1001 if not last_order else last_order.id + 1001
    return f"ORD-{next_num}"

def generate_bill_number():
    last_bill = Bill.query.order_by(Bill.id.desc()).first()
    next_num = 1001 if not last_bill else last_bill.id + 1001
    return f"BILL-{next_num}"

@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json() or {}

    customer_name = data.get('customer_name', '').strip()
    table_number = data.get('table_number', '').strip()
    order_type = data.get('order_type', 'Dine-In').strip()
    items_data = data.get('items', [])
    discount_pct = float(data.get('discount_pct', 0.0) or 0.0)
    payment_method = data.get('payment_method', 'Cash').strip()

    # Validation
    if not customer_name:
        return jsonify({'success': False, 'error': 'Customer name is required.'}), 400
    if not table_number:
        return jsonify({'success': False, 'error': 'Table or Token number is required.'}), 400
    if not items_data or len(items_data) == 0:
        return jsonify({'success': False, 'error': 'Order cannot be empty. Please add items.'}), 400

    # Validate each item against database and recalculate server-side totals
    subtotal = 0.0
    validated_items = []

    for item in items_data:
        food_id = item.get('food_id')
        qty = item.get('quantity', 1)

        try:
            qty = int(qty)
            if qty <= 0:
                return jsonify({'success': False, 'error': f'Invalid quantity {qty} for item.'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Item quantity must be a positive integer.'}), 400

        food = db.session.get(Food, food_id)
        if not food:
            return jsonify({'success': False, 'error': f'Food item ID {food_id} not found.'}), 404
        if not food.is_available:
            return jsonify({'success': False, 'error': f"'{food.name}' is currently marked unavailable."}), 400

        item_price = float(food.price)
        item_total = round(item_price * qty, 2)
        subtotal += item_total

        validated_items.append({
            'food': food,
            'quantity': qty,
            'price': item_price,
            'total': item_total
        })

    subtotal = round(subtotal, 2)

    # Server-side tax & discount calculation
    if discount_pct < 0:
        discount_pct = 0.0
    if discount_pct > 100:
        discount_pct = 100.0

    service_charge_pct = float(data.get('service_charge_pct', 0.0) or 0.0)
    if service_charge_pct < 0:
        service_charge_pct = 0.0
    if service_charge_pct > 20:
        service_charge_pct = 20.0

    discount_amount = round((subtotal * discount_pct) / 100.0, 2)
    taxable_amount = max(0.0, subtotal - discount_amount)
    gst_amount = round((taxable_amount * 5.0) / 100.0, 2)
    service_charge_amount = round((taxable_amount * service_charge_pct) / 100.0, 2)
    grand_total = round(taxable_amount + gst_amount + service_charge_amount, 2)

    try:
        # Create Order record
        order_number = generate_order_number()
        new_order = Order(
            order_number=order_number,
            customer_name=customer_name,
            table_number=table_number,
            order_type=order_type,
            subtotal=subtotal,
            discount=discount_amount,
            gst=gst_amount,
            service_charge=service_charge_amount,
            grand_total=grand_total,
            payment_method=payment_method,
            payment_status=data.get('payment_status', 'Paid').strip(),
            status=data.get('status', 'Completed').strip(),
            created_by=session.get('username', 'staff')
        )
        db.session.add(new_order)
        db.session.flush()  # assign new_order.id

        # Create OrderItem records
        for v_item in validated_items:
            order_item = OrderItem(
                order_id=new_order.id,
                food_id=v_item['food'].id,
                quantity=v_item['quantity'],
                price=v_item['price'],
                total=v_item['total']
            )
            db.session.add(order_item)

        # Generate corresponding BILL automatically
        bill_number = generate_bill_number()
        new_bill = Bill(
            bill_number=bill_number,
            order_id=new_order.id,
            customer_name=customer_name,
            table_number=table_number,
            subtotal=subtotal,
            discount=discount_amount,
            gst=gst_amount,
            service_charge=service_charge_amount,
            grand_total=grand_total,
            payment_method=payment_method,
            payment_status=new_order.payment_status
        )
        db.session.add(new_bill)
        db.session.flush()

        # Create Payment record
        payment_record = Payment(
            order_id=new_order.id,
            bill_id=new_bill.id,
            amount=grand_total,
            payment_method=payment_method,
            payment_status=new_order.payment_status,
            transaction_ref=data.get('transaction_ref') or f"TXN-{bill_number}"
        )
        db.session.add(payment_record)

        # Track/update customer record
        try:
            from models.customer import Customer
            customer = Customer.query.filter_by(name=customer_name).first()
            if not customer:
                customer = Customer(
                    name=customer_name,
                    table_number=table_number,
                    total_visits=1,
                    total_spent=grand_total
                )
                db.session.add(customer)
            else:
                customer.total_visits = (customer.total_visits or 0) + 1
                customer.total_spent = round(float(customer.total_spent or 0.0) + grand_total, 2)
                customer.table_number = table_number
        except Exception:
            pass

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Order and Bill {bill_number} created successfully!',
            'order': new_order.to_dict(),
            'bill': new_bill.to_dict(),
            'payment': payment_record.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to save order: {str(e)}'}), 500

@orders_bp.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    status_filter = request.args.get('status', '').strip()
    payment_status_filter = request.args.get('payment_status', '').strip()

    query = Order.query
    if status_filter:
        query = query.filter(Order.status == status_filter)
    if payment_status_filter:
        query = query.filter(Order.payment_status == payment_status_filter)

    orders = query.order_by(Order.id.desc()).all()
    return jsonify({
        'success': True,
        'count': len(orders),
        'orders': [o.to_dict() for o in orders]
    })

@orders_bp.route('/api/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found.'}), 404
    return jsonify({'success': True, 'order': order.to_dict()})

@orders_bp.route('/api/orders/<int:order_id>/status', methods=['PATCH', 'PUT'])
@login_required
def update_order_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found.'}), 404

    data = request.get_json() or {}
    valid_statuses = ('Pending', 'Preparing', 'Ready', 'Completed', 'Cancelled')
    valid_payment_statuses = ('Paid', 'Pending', 'Refunded')

    if 'status' in data:
        st = data['status'].strip()
        if st in valid_statuses:
            order.status = st
        else:
            return jsonify({'success': False, 'error': f'Invalid order status: {st}. Allowed: {valid_statuses}'}), 400

    if 'payment_status' in data:
        pst = data['payment_status'].strip()
        if pst in valid_payment_statuses:
            order.payment_status = pst
            for b in order.bills:
                b.payment_status = pst
            for p in order.payments:
                p.payment_status = pst
        else:
            return jsonify({'success': False, 'error': f'Invalid payment status: {pst}. Allowed: {valid_payment_statuses}'}), 400

    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Order {order.order_number} status updated successfully.",
        'order': order.to_dict()
    })

@orders_bp.route('/api/payments', methods=['GET'])
@login_required
def get_payments():
    payments = Payment.query.order_by(Payment.id.desc()).all()
    return jsonify({
        'success': True,
        'count': len(payments),
        'payments': [p.to_dict() for p in payments]
    })
