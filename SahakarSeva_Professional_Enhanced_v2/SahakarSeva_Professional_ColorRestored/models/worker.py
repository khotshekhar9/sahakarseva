from datetime import datetime
from database import db

class Worker(db.Model):
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    # Multi-tenant: which contractor employs this worker
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id', ondelete='SET NULL'), nullable=True, index=True)
    skills = db.Column(db.String(255), nullable=True)  # Comma-separated or descriptive text
    experience_years = db.Column(db.Integer, default=0)
    salary_rate = db.Column(db.Numeric(10, 2), default=0.0)
    performance_rating = db.Column(db.Numeric(3, 2), default=5.0)  # Rating out of 5
    availability_status = db.Column(db.String(20), default='available')  # 'available', 'busy', 'leave', 'pending_verification', 'inactive'
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'approved', 'rejected'
    id_proof_file = db.Column(db.String(255), nullable=True)  # Path to uploaded identity/trade document
    emergency_contact = db.Column(db.Text, nullable=True)
    bank_details = db.Column(db.Text, nullable=True)
    documents_paths = db.Column(db.Text, nullable=True)

    # Statutory Cooperative Artisan Skill Tiering
    tier = db.Column(db.String(30), default='Apprentice', nullable=False) # 'Apprentice', 'Skilled Craftsman', 'Master Artisan'
    tier_updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # GPS Live Tracking coordinates
    gps_lat = db.Column(db.Numeric(10, 8), nullable=True)
    gps_lng = db.Column(db.Numeric(11, 8), nullable=True)
    gps_last_updated = db.Column(db.DateTime, nullable=True)

    # Worker Welfare & Insurance Integration (PMJJBY/PMSBY/ESIC/Welfare Fund)
    insurance_provider = db.Column(db.String(120), nullable=True)
    insurance_policy_no = db.Column(db.String(100), nullable=True)
    insurance_valid_until = db.Column(db.Date, nullable=True)
    insurance_coverage_amount = db.Column(db.Numeric(12, 2), default=200000.00)
    coop_welfare_fund_enrolled = db.Column(db.Boolean, default=True)
    welfare_fund_id = db.Column(db.String(100), nullable=True)

    # Automated Welfare & Social Security Engine Fields
    welfare_balance = db.Column(db.Float, default=0.0)
    pmjjby_id = db.Column(db.String(50), nullable=True)  # Policy Certificate ID
    pmjjby_status = db.Column(db.String(20), default="Pending")  # 'Active', 'Accumulating', 'Lapsed'
    pmjjby_renewal_date = db.Column(db.Date, nullable=True)
    pmsby_id = db.Column(db.String(50), nullable=True)
    pmsby_status = db.Column(db.String(20), default="Pending")  # 'Active', 'Due'
    pmsby_renewal_date = db.Column(db.Date, nullable=True)
    esic_ip_number = db.Column(db.String(20), nullable=True)  # 10-digit Insurance Person number

    # Relationships
    attendance_records = db.relationship('Attendance', backref='worker', cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='worker', lazy='dynamic')
    welfare_transactions = db.relationship('WelfareTransaction', backref='worker_profile', cascade="all, delete-orphan", lazy='dynamic', order_by="desc(WelfareTransaction.created_at)")

    @property
    def assigned_projects(self):
        return self.assigned_service_jobs

    @classmethod
    def evaluate_tier(cls, experience_years, verified_certs):
        """
        Statutory Cooperative Tiering Rule Engine:
        - Master Artisan: > 5 years experience AND at least 1 verified Govt/NSDC/ITI certificate.
        - Skilled Craftsman: 2-5 years experience AND at least 1 verified trade certificate.
        - Apprentice: < 2 years experience OR 0 verified certifications.
        """
        exp = float(experience_years or 0)
        verified_count = len(verified_certs) if isinstance(verified_certs, list) else int(verified_certs or 0)
        has_govt_nsdc = any(
            any(kw in (getattr(c, 'cert_title', '') + ' ' + getattr(c, 'issuing_body', '')).upper() 
                for kw in ['NSDC', 'GOVT', 'ITI', 'GOVERNMENT', 'NABET']) 
            for c in (verified_certs if isinstance(verified_certs, list) else [])
        )

        if exp > 5 and has_govt_nsdc:
            return 'Master Artisan'
        elif exp >= 2 and verified_count >= 1:
            return 'Skilled Craftsman'
        else:
            return 'Apprentice'

    def refresh_tier(self):
        from models.worker_features import WorkerCertification
        verified_certs = WorkerCertification.query.filter_by(worker_id=self.id, status='Verified').all()
        new_tier = self.evaluate_tier(self.experience_years, verified_certs)
        if self.tier != new_tier:
            self.tier = new_tier
            self.tier_updated_at = datetime.utcnow()
        return self.tier

    def get_next_tier_info(self):
        """Returns concise 1-line progress indicator showing criteria to reach next statutory tier."""
        from models.worker_features import WorkerCertification
        verified_certs = WorkerCertification.query.filter_by(worker_id=self.id, status='Verified').all()
        exp = float(self.experience_years or 0)
        verified_count = len(verified_certs)
        has_govt_nsdc = any(
            any(kw in (getattr(c, 'cert_title', '') + ' ' + getattr(c, 'issuing_body', '')).upper() 
                for kw in ['NSDC', 'GOVT', 'ITI', 'GOVERNMENT', 'NABET']) 
            for c in verified_certs
        )

        if self.tier == 'Master Artisan':
            return {
                'current_tier': 'Master Artisan',
                'next_tier': None,
                'progress_pct': 100,
                'requirement_text': 'Highest statutory skill tier achieved.',
                'badge_class': 'bg-purple-subtle text-purple border-purple-subtle',
                'icon': 'fas fa-crown text-warning'
            }
        elif self.tier == 'Skilled Craftsman':
            if exp <= 5 and not has_govt_nsdc:
                needed_exp = max(1, 6 - int(exp))
                req = f"Add {needed_exp} yr experience & 1 verified Govt/NSDC certificate for Master Artisan."
            elif not has_govt_nsdc:
                req = "Add 1 verified Govt/NSDC/ITI certificate to unlock Master Artisan."
            else:
                needed_exp = max(1, 6 - int(exp))
                req = f"Reach >5 yrs experience ({needed_exp} yr needed) to unlock Master Artisan."
            return {
                'current_tier': 'Skilled Craftsman',
                'next_tier': 'Master Artisan',
                'progress_pct': 66,
                'requirement_text': req,
                'badge_class': 'bg-primary-subtle text-primary border-primary-subtle',
                'icon': 'fas fa-tools'
            }
        else: # Apprentice
            if verified_count == 0 and exp < 2:
                req = "Reach 2+ yrs experience and add 1 verified trade certificate for Skilled Craftsman."
            elif verified_count == 0:
                req = "Add 1 verified trade certificate to unlock Skilled Craftsman."
            else:
                needed_exp = max(1, 2 - int(exp))
                req = f"Reach 2 yrs experience ({needed_exp} yr needed) to unlock Skilled Craftsman."
            return {
                'current_tier': 'Apprentice',
                'next_tier': 'Skilled Craftsman',
                'progress_pct': 33,
                'requirement_text': req,
                'badge_class': 'bg-secondary-subtle text-secondary border-secondary-subtle',
                'icon': 'fas fa-user-graduate'
            }

    @property
    def latitude(self):
        return self.gps_lat

    @latitude.setter
    def latitude(self, val):
        self.gps_lat = val

    @property
    def longitude(self):
        return self.gps_lng

    @longitude.setter
    def longitude(self, val):
        self.gps_lng = val

    @property
    def trades(self):
        """Returns all matching emergency trade categories for this worker."""
        skills = (self.skills or "").lower()
        trade_list = []
        trade_map = {
            "Electrical": ["electrician", "wiring", "electrical", "appliance repair"],
            "Plumbing": ["plumbing", "pipefitting", "sanitary", "waterproofing"],
            "Caregiving": ["caregiver", "elderly", "bedside", "palliative", "nurse"],
            "Locksmith": ["carpentry", "locksmith", "furniture repair"],
            "Sanitization": ["cleaning", "sanitization", "deep cleaning", "housekeeping", "domestic"],
            "Drivers": ["driver", "chauffeur", "transport", "vehicle"],
            "Painting": ["painting", "painter", "wall finishing"],
            "Gardening": ["gardening", "landscape", "garden"],
            "General": ["maintenance", "general", "technician"]
        }
        for trade, kws in trade_map.items():
            if any(kw in skills for kw in kws):
                trade_list.append(trade)
        return trade_list if trade_list else ["General"]

    @property
    def trade_category(self):
        """Returns the primary emergency trade category for this worker."""
        t = self.trades
        return t[0] if t else "Electrical"

    def __repr__(self):
        return f'<Worker {self.id} Tier:{self.tier} Status:{self.availability_status} WelfareBal:₹{self.welfare_balance}>'
