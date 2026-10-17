from database import db
from datetime import datetime


class Contractor(db.Model):
    __tablename__ = 'contractors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Company Info
    company_name = db.Column(db.String(200), nullable=False)
    company_logo = db.Column(db.String(255), nullable=True)
    license_number = db.Column(db.String(100), nullable=True)
    business_type = db.Column(db.String(100), default='General')  # 'General', 'Electrical', 'Plumbing', 'Civil', etc.
    description = db.Column(db.Text, nullable=True)
    service_areas = db.Column(db.Text, nullable=True)   # Comma-separated city names e.g. "Mumbai,Pune,Nashik"
    website = db.Column(db.String(255), nullable=True)
    established_year = db.Column(db.Integer, nullable=True)
    cooperative_reg_no = db.Column(db.String(100), nullable=True)  # State Cooperative Registration No.
    federation_name = db.Column(db.String(200), default="State Labour Cooperative Federation")

    # Contact
    contact_phone = db.Column(db.String(20), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    office_address = db.Column(db.Text, nullable=True)
    business_hours = db.Column(db.String(100), default='09:00 - 18:00')

    # Publisher Verification & Onboarding
    license_document = db.Column(db.String(255), nullable=True)
    onboarding_status = db.Column(db.String(50), default='approved')  # 'pending_approval', 'approved', 'rejected'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)


    # Stats (cached for leaderboard)
    total_projects_completed = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Numeric(3, 2), default=0.0)
    total_reviews = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('contractor_profile', uselist=False))

    def get_service_area_list(self):
        """Return service_areas as a Python list."""
        if self.service_areas:
            return [a.strip() for a in self.service_areas.split(',') if a.strip()]
        return []

    def serves_city(self, city):
        """Check if contractor serves a given city (case-insensitive)."""
        if not city:
            return True
        return city.strip().lower() in [a.lower() for a in self.get_service_area_list()]

    @property
    def worker_count(self):
        from models.worker import Worker
        return Worker.query.filter_by(contractor_id=self.id, is_archived=False).count()

    def __repr__(self):
        return f'<Contractor {self.company_name}>'


class ContractorReview(db.Model):
    """Customer review for a contractor after a completed service/project."""
    __tablename__ = 'contractor_reviews'

    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id', ondelete='CASCADE'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='SET NULL'), nullable=True)
    project_id = db.Column(db.Integer, nullable=True)  # Legacy compatibility column

    rating = db.Column(db.Integer, nullable=False)          # 1–5 stars
    title = db.Column(db.String(150), nullable=True)
    review_text = db.Column(db.Text, nullable=True)
    is_approved = db.Column(db.Boolean, default=True)       # Publisher can hide inappropriate reviews
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contractor = db.relationship('Contractor', backref=db.backref('reviews', cascade='all, delete-orphan'))
    customer = db.relationship('Customer', backref=db.backref('given_reviews', lazy='dynamic'))

    def __repr__(self):
        return f'<ContractorReview Contractor:{self.contractor_id} Rating:{self.rating}>'

