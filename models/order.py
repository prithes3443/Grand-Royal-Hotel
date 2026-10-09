from datetime import datetime
from models import db

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    table_number = db.Column(db.String(50), nullable=False)
    order_type = db.Column(db.String(50), nullable=False, default='Dine-In')  # 'Dine-In' or 'Parcel / Takeaway'
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    gst = db.Column(db.Float, nullable=False, default=0.0)
    service_charge = db.Column(db.Float, nullable=False, default=0.0)
    grand_total = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash')  # 'Cash', 'Card', 'UPI / GPay'
    payment_status = db.Column(db.String(50), nullable=False, default='Paid')  # 'Paid', 'Pending', 'Refunded'
    status = db.Column(db.String(50), default='Completed')  # 'Pending', 'Preparing', 'Ready', 'Completed', 'Cancelled'
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.String(100), nullable=True)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    bills = db.relationship('Bill', backref='order', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'table_number': self.table_number,
            'order_type': self.order_type,
            'subtotal': round(float(self.subtotal), 2),
            'discount': round(float(self.discount), 2),
            'gst': round(float(self.gst), 2),
            'service_charge': round(float(self.service_charge or 0.0), 2),
            'grand_total': round(float(self.grand_total), 2),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status or 'Paid',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'created_by': self.created_by or '',
            'items': [item.to_dict() for item in self.items]
        }

    def __repr__(self):
        return f"<Order {self.order_number} - ₹{self.grand_total}>"
