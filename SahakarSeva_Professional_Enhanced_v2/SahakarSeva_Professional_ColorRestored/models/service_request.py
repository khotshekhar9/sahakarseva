from database import db
from datetime import datetime

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    request_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    # Multi-tenant: which contractor this request is assigned to
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id', ondelete='SET NULL'), nullable=True, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    voice_path = db.Column(db.String(255), nullable=True)
    photos = db.Column(db.Text, nullable=True)  # Comma-separated paths of complaint photos
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)
    status = db.Column(db.String(50), default='Pending', index=True)  # Workflow statuses
    
    # Assignment Fields
    assigned_worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='SET NULL'), nullable=True)
    visit_date = db.Column(db.Date, nullable=True)
    estimated_cost = db.Column(db.Numeric(10, 2), nullable=True)
    priority = db.Column(db.String(20), default='Normal')  # 'Normal', 'Urgent', 'Emergency'
    
    # Instant 1-Click Emergency / On-Demand Dispatch Fields
    is_emergency = db.Column(db.Boolean, default=False, index=True)
    emergency_severity = db.Column(db.String(20), default='Critical')  # 'Standard', 'Critical', 'Life-Threatening'
    fixed_rate = db.Column(db.Numeric(10, 2), nullable=True)  # Pre-fixed cooperative tariff bypassing quotation
    broadcast_status = db.Column(db.String(20), default='None', index=True)  # 'None', 'Broadcasting', 'Claimed', 'Expired', 'Cancelled'
    dispatch_radius_km = db.Column(db.Float, default=5.0)
    claimed_at = db.Column(db.DateTime, nullable=True)
    broadcast_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Verification & Workflow Fields
    otp = db.Column(db.String(10), nullable=True)
    otp_verified = db.Column(db.Boolean, default=False)
    arrived_at = db.Column(db.DateTime, nullable=True)
    preferred_time = db.Column(db.String(50), nullable=True)
    progress = db.Column(db.Integer, default=0)
    completion_videos = db.Column(db.Text, nullable=True)
    materials_used = db.Column(db.Text, nullable=True)
    time_worked = db.Column(db.Numeric(10, 2), default=0.0)
    
    # Completion Fields
    completion_date = db.Column(db.DateTime, nullable=True)
    completion_photos = db.Column(db.Text, nullable=True)  # Comma-separated paths of completion photos
    completion_notes = db.Column(db.Text, nullable=True)
    completion_voice_path = db.Column(db.String(255), nullable=True)
    
    # Feedback Fields
    rating = db.Column(db.Integer, nullable=True)
    review_comment = db.Column(db.Text, nullable=True)
    rework_comments = db.Column(db.Text, nullable=True)
    payment_status = db.Column(db.String(20), default='Pending')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    contractor = db.relationship('Contractor', backref=db.backref('assigned_service_requests', lazy='dynamic'))
    customer = db.relationship('Customer', backref=db.backref('service_requests', cascade="all, delete-orphan"))
    assigned_worker = db.relationship('Worker', backref=db.backref('assigned_service_jobs', lazy='dynamic'))

    @property
    def payment(self):
        """Returns the latest payment record associated with this service request."""
        if hasattr(self, 'payments') and self.payments:
            return self.payments.order_by(db.desc('id')).first()
        return None

    @property
    def payment_id(self):
        """Returns the ID of the latest payment record, or None."""
        p = self.payment
        return p.id if p else None

    @property
    def location_name(self):
        return self.address or f"Service Site #{self.request_id}"

    @property
    def location_lat(self):
        return self.latitude

    @property
    def location_lng(self):
        return self.longitude

    @property
    def name(self):
        return self.title or f"Service #{self.request_id}"

    def __repr__(self):
        return f'<ServiceRequest {self.request_id} Status:{self.status}>'
