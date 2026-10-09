from datetime import datetime
from models import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id', ondelete='SET NULL'), nullable=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash')  # 'Cash', 'Card', 'UPI / GPay'
    payment_status = db.Column(db.String(50), nullable=False, default='Paid')  # 'Paid', 'Pending', 'Refunded', 'Failed'
    transaction_ref = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'bill_id': self.bill_id,
            'amount': round(float(self.amount), 2),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_ref': self.transaction_ref or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

    def __repr__(self):
        return f"<Payment {self.id} Order:{self.order_id} - ₹{self.amount} ({self.payment_status})>"
