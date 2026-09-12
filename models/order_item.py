from models import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else 'Unknown Dish',
            'food_type': self.food.food_type if self.food else 'Veg',
            'quantity': self.quantity,
            'price': float(self.price),
            'total': float(self.total)
        }

    def __repr__(self):
        return f"<OrderItem Food:{self.food_id} Qty:{self.quantity} Total:₹{self.total}>"
