from datetime import datetime, date
from flask import Blueprint, jsonify
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
