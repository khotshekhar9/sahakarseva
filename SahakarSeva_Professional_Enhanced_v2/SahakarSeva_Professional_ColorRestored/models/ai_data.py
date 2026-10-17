from database import db
from datetime import datetime

class AIEstimate(db.Model):
    __tablename__ = 'ai_estimates'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)
    
    service_type = db.Column(db.String(50), nullable=False)
    house_size = db.Column(db.Numeric(10, 2), nullable=False)
    num_rooms = db.Column(db.Integer, default=1)
    problem_type = db.Column(db.String(100), nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    
    est_material_cost = db.Column(db.Numeric(10, 2), default=0.0)
    est_labour_cost = db.Column(db.Numeric(10, 2), default=0.0)
    est_total_cost = db.Column(db.Numeric(10, 2), default=0.0)
    est_completion_time = db.Column(db.String(50), nullable=False) # e.g. "4 hours"
    confidence_score = db.Column(db.Numeric(5, 2), default=100.0) # Percentage (e.g. 92.5)

    service_request = db.relationship('ServiceRequest', backref=db.backref('ai_estimate', uselist=False, cascade="all, delete-orphan"))


class AIDelayPrediction(db.Model):
    __tablename__ = 'ai_delay_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=True)
    project_id = db.Column(db.Integer, nullable=True)
    
    risk_level = db.Column(db.String(20), nullable=False) # 'Low', 'Medium', 'High'
    delay_percentage = db.Column(db.Numeric(5, 2), default=0.0)
    expected_delay_days = db.Column(db.Integer, default=0)
    reason = db.Column(db.Text, nullable=True)
    suggested_actions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    service_request = db.relationship('ServiceRequest', backref=db.backref('ai_delay_predictions', cascade="all, delete-orphan"))

    @property
    def project(self):
        return self.service_request


class AIMaterialForecast(db.Model):
    """Predicts trade demand and seasonal raw material supply requirements for cooperative services."""
    __tablename__ = 'ai_material_forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    trade_category = db.Column(db.String(100), nullable=False, default='Electrical')
    material_name = db.Column(db.String(150), nullable=False, default='General Supplies')
    
    days_remaining = db.Column(db.Integer, default=0)
    recommended_purchase_qty = db.Column(db.Numeric(10, 2), default=0.0)
    supplier_recommendation = db.Column(db.String(100), nullable=True)
    alert_level = db.Column(db.String(20), default='Low') # 'Low', 'Medium', 'Critical'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AIMaterialForecast {self.trade_category}: {self.material_name} ({self.alert_level})>'
