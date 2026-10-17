from database import db
from datetime import datetime

class Quotation(db.Model):
    __tablename__ = 'quotations'
    
    id = db.Column(db.Integer, primary_key=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    quotation_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)
    
    # Cost Breakdown
    material_list = db.Column(db.Text, nullable=True) # Stored as JSON string
    labour_cost = db.Column(db.Numeric(10, 2), default=0.00)
    equipment_charges = db.Column(db.Numeric(10, 2), default=0.00)
    gst = db.Column(db.Numeric(10, 2), default=0.00)
    discount = db.Column(db.Numeric(10, 2), default=0.00)
    grand_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Metadata
    terms_conditions = db.Column(db.Text, nullable=True)
    validity_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending', index=True) # 'Pending', 'Approved', 'Rejected', 'Changes Requested'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('quotations', cascade="all, delete-orphan"))

    @property
    def total_amount(self):
        return self.grand_total

    def __repr__(self):
        return f'<Quotation {self.quotation_number} Status:{self.status}>'
