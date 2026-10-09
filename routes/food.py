from flask import Blueprint, request, jsonify, session
from models import db
from models.food import Food
from routes.auth import login_required, admin_required

food_bp = Blueprint('food', __name__)

@food_bp.route('/api/foods', methods=['GET'])
def get_foods():
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()
    available_only = request.args.get('available_only', 'false').lower() == 'true'

    query = Food.query

    if available_only:
        query = query.filter(Food.is_available == True)

    if category and category.lower() != 'all items':
        query = query.filter(Food.category.ilike(f"%{category}%"))

    if search:
        query = query.filter(Food.name.ilike(f"%{search}%") | Food.description.ilike(f"%{search}%"))

    foods = query.order_by(Food.category, Food.name).all()
    return jsonify({
        'success': True,
        'count': len(foods),
        'foods': [f.to_dict() for f in foods]
    })

@food_bp.route('/api/foods/<int:food_id>', methods=['GET'])
def get_food(food_id):
    food = db.session.get(Food, food_id)
    if not food:
        return jsonify({'success': False, 'error': 'Food item not found'}), 404
    return jsonify({'success': True, 'food': food.to_dict()})

@food_bp.route('/api/foods', methods=['POST'])
@admin_required
def create_food():
    data = request.get_json() or {}
    
    name = data.get('name', '').strip()
    category = data.get('category', '').strip()
    price = data.get('price')
    food_type = data.get('food_type', 'Veg')
    description = data.get('description', '').strip()
    image = data.get('image', 'idly.jpg').strip()
    rating = data.get('rating', 4.5)
    is_available = data.get('is_available', True)

    if not name or not category or price is None:
        return jsonify({'success': False, 'error': 'Name, category, and price are required.'}), 400

    try:
        price = float(price)
        if price <= 0:
            return jsonify({'success': False, 'error': 'Price must be greater than zero.'}), 400
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid price format.'}), 400

    try:
        rating = float(rating)
    except (ValueError, TypeError):
        rating = 4.5

    new_food = Food(
        name=name,
        category=category,
        description=description,
        price=price,
        food_type=food_type,
        image=image if image else 'idly.jpg',
        rating=rating,
        is_available=bool(is_available)
    )

    db.session.add(new_food)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Food '{new_food.name}' added successfully.",
        'food': new_food.to_dict()
    }), 201

@food_bp.route('/api/foods/<int:food_id>', methods=['PUT'])
@admin_required
def update_food(food_id):
    food = db.session.get(Food, food_id)
    if not food:
        return jsonify({'success': False, 'error': 'Food item not found.'}), 404

    data = request.get_json() or {}

    if 'name' in data and data['name'].strip():
        food.name = data['name'].strip()
    if 'category' in data and data['category'].strip():
        food.category = data['category'].strip()
    if 'description' in data:
        food.description = data['description'].strip()
    if 'food_type' in data:
        food.food_type = data['food_type']
    if 'image' in data and data['image'].strip():
        food.image = data['image'].strip()
    if 'rating' in data:
        try:
            food.rating = float(data['rating'])
        except (ValueError, TypeError):
            pass
    if 'is_available' in data:
        food.is_available = bool(data['is_available'])
    if 'price' in data:
        try:
            p = float(data['price'])
            if p > 0:
                food.price = p
            else:
                return jsonify({'success': False, 'error': 'Price must be positive.'}), 400
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid price format.'}), 400

    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Food '{food.name}' updated successfully.",
        'food': food.to_dict()
    })

@food_bp.route('/api/foods/<int:food_id>', methods=['DELETE'])
@admin_required
def delete_food(food_id):
    food = db.session.get(Food, food_id)
    if not food:
        return jsonify({'success': False, 'error': 'Food item not found.'}), 404

    food_name = food.name
    db.session.delete(food)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Food item '{food_name}' deleted successfully."
    })
