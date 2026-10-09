from datetime import datetime
from models import db

class DemandPrediction(db.Model):
    __tablename__ = 'demand_predictions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prediction_date = db.Column(db.String(20), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('foods.id', ondelete='SET NULL'), nullable=True)
    dish_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    predicted_units = db.Column(db.Integer, nullable=False, default=0)
    safety_buffer = db.Column(db.Integer, nullable=False, default=0)
    recommended_prep = db.Column(db.Integer, nullable=False, default=0)
    risk_level = db.Column(db.String(20), default='Moderate')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'prediction_date': self.prediction_date,
            'dish_id': self.dish_id,
            'dish_name': self.dish_name,
            'category': self.category,
            'predicted_units': self.predicted_units,
            'safety_buffer': self.safety_buffer,
            'recommended_prep': self.recommended_prep,
            'risk_level': self.risk_level,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

    def __repr__(self):
        return f"<DemandPrediction {self.dish_name} on {self.prediction_date}: {self.recommended_prep} units>"
