from datetime import datetime
from models import db

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    table_number = db.Column(db.String(50), nullable=True)
    total_visits = db.Column(db.Integer, default=1)
    total_spent = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone or '',
            'email': self.email or '',
            'table_number': self.table_number or '',
            'total_visits': self.total_visits,
            'total_spent': round(float(self.total_spent or 0.0), 2),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

    def __repr__(self):
        return f"<Customer {self.name} ({self.phone})>"
