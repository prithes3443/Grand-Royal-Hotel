from datetime import datetime
from models import db

class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    food_type = db.Column(db.String(20), nullable=False, default='Veg')  # 'Veg' or 'Non-Veg'
    image = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Float, default=4.5)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='food', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description or '',
            'price': float(self.price),
            'food_type': self.food_type,
            'image': self.image or 'idly.jpg',
            'rating': float(self.rating) if self.rating else 4.5,
            'is_available': bool(self.is_available),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

    def __repr__(self):
        return f"<Food {self.name} - ₹{self.price}>"
