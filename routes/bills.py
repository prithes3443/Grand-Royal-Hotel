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

    bills = query.order_by(Bill.id.desc()).all()

    return jsonify({
        'success': True,
        'count': len(bills),
        'bills': [b.to_dict() for b in bills]
    })

@bills_bp.route('/api/bills/<int:bill_id>', methods=['GET'])
@login_required
def get_bill(bill_id):
    bill = Bill.query.get(bill_id)
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
    bill = Bill.query.get(bill_id)
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

@bills_bp.route('/bill/<int:bill_id>', methods=['GET'])
@login_required
def view_bill_page(bill_id):
    bill = Bill.query.get(bill_id)
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
