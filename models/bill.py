from datetime import datetime
from models import db

class Bill(db.Model):
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    table_number = db.Column(db.String(50), nullable=False)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    gst = db.Column(db.Float, nullable=False, default=0.0)
    grand_total = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        items_list = []
        if self.order and self.order.items:
            items_list = [item.to_dict() for item in self.order.items]
            
        return {
            'id': self.id,
            'bill_number': self.bill_number,
            'order_id': self.order_id,
            'order_number': self.order.order_number if self.order else '',
            'order_type': self.order.order_type if self.order else 'Dine-In',
            'customer_name': self.customer_name,
            'table_number': self.table_number,
            'subtotal': round(float(self.subtotal), 2),
            'discount': round(float(self.discount), 2),
            'gst': round(float(self.gst), 2),
            'grand_total': round(float(self.grand_total), 2),
            'payment_method': self.payment_method,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'items': items_list,
            'order_items': items_list
        }

    def __repr__(self):
        return f"<Bill {self.bill_number} - ₹{self.grand_total}>"
