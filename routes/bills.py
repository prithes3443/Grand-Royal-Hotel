from flask import Blueprint, request, jsonify, render_template, abort
from models import db
from models.bill import Bill
from models.order import Order
from routes.auth import login_required, admin_required

bills_bp = Blueprint('bills', __name__)

@bills_bp.route('/api/bills', methods=['GET'])
@login_required
def get_bills():
    search = request.args.get('search', '').strip()
    date_filter = request.args.get('date', '').strip()
    payment_status_filter = request.args.get('payment_status', '').strip()

    query = Bill.query

    if search:
        query = query.filter(
            Bill.bill_number.ilike(f"%{search}%") |
            Bill.customer_name.ilike(f"%{search}%") |
            Bill.table_number.ilike(f"%{search}%")
        )

    if date_filter:
        # Match YYYY-MM-DD prefix
        query = query.filter(db.cast(Bill.created_at, db.String).ilike(f"{date_filter}%"))

    if payment_status_filter:
        query = query.filter(Bill.payment_status == payment_status_filter)

    bills = query.order_by(Bill.id.desc()).all()

    return jsonify({
        'success': True,
        'count': len(bills),
        'bills': [b.to_dict() for b in bills]
    })

@bills_bp.route('/api/bills/<int:bill_id>', methods=['GET'])
@login_required
def get_bill(bill_id):
    bill = db.session.get(Bill, bill_id)
    if not bill:
        return jsonify({'success': False, 'error': 'Bill not found.'}), 404
    return jsonify({'success': True, 'bill': bill.to_dict()})

@bills_bp.route('/api/bills/by-number/<string:bill_number>', methods=['GET'])
@login_required
def get_bill_by_number(bill_number):
    bill = Bill.query.filter_by(bill_number=bill_number).first()
    if not bill:
        return jsonify({'success': False, 'error': f'Bill {bill_number} not found.'}), 404
    return jsonify({'success': True, 'bill': bill.to_dict()})

@bills_bp.route('/api/bills/<int:bill_id>', methods=['DELETE'])
@admin_required
def delete_bill(bill_id):
    bill = db.session.get(Bill, bill_id)
    if not bill:
        return jsonify({'success': False, 'error': 'Bill not found.'}), 404

    bill_num = bill.bill_number
    # Also delete associated order if desired, or cascade
    order = bill.order
    db.session.delete(bill)
    if order:
        db.session.delete(order)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Bill '{bill_num}' deleted successfully."
    })

@bills_bp.route('/api/bills/<int:bill_id>/payment-status', methods=['PATCH', 'PUT'])
@login_required
def update_bill_payment_status(bill_id):
    bill = db.session.get(Bill, bill_id)
    if not bill:
        return jsonify({'success': False, 'error': 'Bill not found.'}), 404

    data = request.get_json() or {}
    valid_payment_statuses = ('Paid', 'Pending', 'Refunded')
    new_status = data.get('payment_status', '').strip()

    if new_status not in valid_payment_statuses:
        return jsonify({'success': False, 'error': f'Invalid payment status. Allowed: {valid_payment_statuses}'}), 400

    bill.payment_status = new_status
    if bill.order:
        bill.order.payment_status = new_status
        for p in bill.order.payments:
            p.payment_status = new_status

    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Bill {bill.bill_number} payment status updated to {new_status}.",
        'bill': bill.to_dict()
    })

@bills_bp.route('/bill/<int:bill_id>', methods=['GET'])
@login_required
def view_bill_page(bill_id):
    bill = db.session.get(Bill, bill_id)
    if not bill:
        abort(404, description="Bill not found")
    return render_template('bill.html', bill=bill.to_dict())

@bills_bp.route('/bill/number/<string:bill_number>', methods=['GET'])
@login_required
def view_bill_by_number_page(bill_number):
    bill = Bill.query.filter_by(bill_number=bill_number).first()
    if not bill:
        abort(404, description=f"Bill {bill_number} not found")
    return render_template('bill.html', bill=bill.to_dict())
