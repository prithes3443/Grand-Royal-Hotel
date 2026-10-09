from datetime import datetime, date
from collections import defaultdict
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from models import db
from models.order import Order
from models.order_item import OrderItem
from models.bill import Bill
from models.food import Food
from routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')

    # Total Orders Recorded
    total_orders = Order.query.count()

    # Total Revenue across all time
    total_revenue_res = db.session.query(func.sum(Order.grand_total)).scalar()
    total_revenue = round(float(total_revenue_res or 0.0), 2)

    # Today's Orders & Today's Revenue
    # Match created_at date prefix
    today_orders_query = Order.query.filter(db.cast(Order.created_at, db.String).ilike(f"{today_str}%"))
    today_orders = today_orders_query.count()
    
    today_rev_res = db.session.query(func.sum(Order.grand_total))\
        .filter(db.cast(Order.created_at, db.String).ilike(f"{today_str}%")).scalar()
    today_revenue = round(float(today_rev_res or 0.0), 2)

    # Recent Invoices (latest 8 bills)
    recent_bills = Bill.query.order_by(Bill.id.desc()).limit(8).all()
    recent_invoices = [b.to_dict() for b in recent_bills]

    # Top Selling Dishes (Sum quantity by food_id)
    top_selling_raw = db.session.query(
        Food.id,
        Food.name,
        Food.category,
        Food.price,
        Food.food_type,
        Food.image,
        Food.rating,
        func.sum(OrderItem.quantity).label('total_ordered')
    ).join(OrderItem, Food.id == OrderItem.food_id)\
     .group_by(Food.id)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .limit(6).all()

    top_dishes = []
    for rank, item in enumerate(top_selling_raw, 1):
        top_dishes.append({
            'rank': rank,
            'food_id': item.id,
            'name': item.name,
            'category': item.category,
            'price': float(item.price),
            'food_type': item.food_type,
            'image': item.image or 'idly.jpg',
            'rating': float(item.rating) if item.rating else 4.5,
            'total_ordered': int(item.total_ordered or 0)
        })

    # If no orders yet, populate top dishes with top rated foods
    if not top_dishes:
        top_rated = Food.query.filter_by(is_available=True).order_by(Food.rating.desc()).limit(6).all()
        for rank, f in enumerate(top_rated, 1):
            top_dishes.append({
                'rank': rank,
                'food_id': f.id,
                'name': f.name,
                'category': f.category,
                'price': float(f.price),
                'food_type': f.food_type,
                'image': f.image or 'idly.jpg',
                'rating': float(f.rating) if f.rating else 4.5,
                'total_ordered': 0
            })

    return jsonify({
        'success': True,
        'metrics': {
            'today_orders': today_orders,
            'today_revenue': today_revenue,
            'total_orders': total_orders,
            'total_revenue': total_revenue
        },
        'recent_invoices': recent_invoices,
        'top_dishes': top_dishes
    })

@dashboard_bp.route('/api/reports', methods=['GET'])
@login_required
def get_reports_data():
    from datetime import timedelta
    range_filter = request.args.get('range', 'all').lower()
    today = date.today()

    query = Order.query
    if range_filter == 'today':
        query = query.filter(db.cast(Order.created_at, db.String).ilike(f"{today.strftime('%Y-%m-%d')}%"))
    elif range_filter == 'week':
        week_ago = today - timedelta(days=7)
        query = query.filter(Order.created_at >= week_ago)
    elif range_filter == 'month':
        month_ago = today - timedelta(days=30)
        query = query.filter(Order.created_at >= month_ago)

    orders = query.order_by(Order.id.desc()).all()
    total_orders = len(orders)
    total_revenue = round(sum(o.grand_total for o in orders), 2)
    total_discount = round(sum(o.discount for o in orders), 2)
    total_gst = round(sum(o.gst for o in orders), 2)
    total_service_charge = round(sum(getattr(o, 'service_charge', 0.0) or 0.0 for o in orders), 2)
    avg_order_value = round((total_revenue / total_orders), 2) if total_orders > 0 else 0.0

    # Payment Breakdown
    payment_map = defaultdict(lambda: {'count': 0, 'total': 0.0})
    for o in orders:
        method = o.payment_method or 'Cash'
        payment_map[method]['count'] += 1
        payment_map[method]['total'] += float(o.grand_total)

    payment_breakdown = [
        {'method': k, 'count': v['count'], 'total': round(v['total'], 2)}
        for k, v in payment_map.items()
    ]

    # Food Item Sales Breakdown
    order_ids = [o.id for o in orders]
    food_sales = []
    if order_ids:
        raw_food_sales = db.session.query(
            Food.name,
            Food.category,
            func.sum(OrderItem.quantity).label('qty_sold'),
            func.sum(OrderItem.total).label('revenue')
        ).join(OrderItem, Food.id == OrderItem.food_id)\
         .filter(OrderItem.order_id.in_(order_ids))\
         .group_by(Food.id)\
         .order_by(func.sum(OrderItem.total).desc()).all()

        for item in raw_food_sales:
            food_sales.append({
                'name': item.name,
                'category': item.category,
                'quantity': int(item.qty_sold or 0),
                'revenue': round(float(item.revenue or 0.0), 2)
            })

    return jsonify({
        'success': True,
        'range': range_filter,
        'summary': {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_discount': total_discount,
            'total_gst': total_gst,
            'total_service_charge': total_service_charge,
            'avg_order_value': avg_order_value
        },
        'payment_breakdown': payment_breakdown,
        'food_sales': food_sales,
        'recent_orders': [o.to_dict() for o in orders[:20]]
    })

@dashboard_bp.route('/api/reports/export-csv', methods=['GET'])
@login_required
def export_reports_csv():
    import io
    import csv
    from flask import Response

    orders = Order.query.order_by(Order.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Order ID', 'Order Number', 'Date', 'Customer Name', 'Table Number',
        'Order Type', 'Subtotal', 'Discount', 'GST (5%)', 'Service Charge',
        'Grand Total', 'Payment Method', 'Status', 'Cashier'
    ])

    for o in orders:
        writer.writerow([
            o.id,
            o.order_number,
            o.created_at.strftime('%Y-%m-%d %H:%M:%S') if o.created_at else '',
            o.customer_name,
            o.table_number,
            o.order_type,
            f"{o.subtotal:.2f}",
            f"{o.discount:.2f}",
            f"{o.gst:.2f}",
            f"{getattr(o, 'service_charge', 0.0) or 0.0:.2f}",
            f"{o.grand_total:.2f}",
            o.payment_method,
            o.status,
            o.created_by or 'staff'
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=grand_royal_hotel_sales_report.csv"}
    )
