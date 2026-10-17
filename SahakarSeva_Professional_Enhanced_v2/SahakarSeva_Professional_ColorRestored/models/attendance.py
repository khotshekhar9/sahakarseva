from database import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='CASCADE'), nullable=False)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=True)
    project_id = db.Column(db.Integer, nullable=True)  # Legacy compatibility column
    date = db.Column(db.Date, nullable=False, index=True)
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Absent')  # 'Present', 'Absent', 'Late'
    
    # Verification and GPS
    check_in_lat = db.Column(db.Numeric(10, 8), nullable=True)
    check_in_lng = db.Column(db.Numeric(11, 8), nullable=True)
    check_out_lat = db.Column(db.Numeric(10, 8), nullable=True)
    check_out_lng = db.Column(db.Numeric(11, 8), nullable=True)
    
    verified_by_gps = db.Column(db.Boolean, default=False)
    verified_by_qr = db.Column(db.Boolean, default=False)

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('attendance_records', cascade="all, delete-orphan"))

    @property
    def project(self):
        return self.service_request

    @project.setter
    def project(self, val):
        self.service_request = val

    @property
    def site_name(self):
        if hasattr(self, '_site_name') and self._site_name:
            return self._site_name
        target = self.service_request
        if target and getattr(target, 'location_name', None):
            return target.location_name.split(',')[0].strip()
        if target and getattr(target, 'name', None):
            return target.name.split(' — ')[0].strip()
        return "Deonar Heights CHS"

    @site_name.setter
    def site_name(self, value):
        self._site_name = value

    @property
    def site_full(self):
        if hasattr(self, '_site_full') and self._site_full:
            return self._site_full
        target = self.service_request
        if target and getattr(target, 'name', None):
            return target.name
        return f"{self.site_name} — Annual Society Maintenance"

    @site_full.setter
    def site_full(self, value):
        self._site_full = value

    def __repr__(self):
        return f'<Attendance W:{self.worker_id} Date:{self.date} Status:{self.status}>'

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item, default=None):
        return getattr(self, item, default)
