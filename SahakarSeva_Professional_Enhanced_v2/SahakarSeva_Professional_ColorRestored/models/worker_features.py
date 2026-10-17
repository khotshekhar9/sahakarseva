from database import db
from datetime import datetime, date

class WorkerTaskChecklist(db.Model):
    """Task Checklists assigned to service requests for workers to complete."""
    __tablename__ = 'worker_task_checklists'

    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id', ondelete='CASCADE'), nullable=False)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=True)
    project_id = db.Column(db.Integer, nullable=True)  # Legacy compatibility column
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='SET NULL'), nullable=True)
    
    task_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('task_checklists', cascade='all, delete-orphan'))
    worker = db.relationship('Worker', backref='task_checklists')

    @property
    def project(self):
        return self.service_request

    def __repr__(self):
        return f'<WorkerTaskChecklist {self.task_name} Done:{self.is_completed}>'


class WorkerCertification(db.Model):
    """Trade Licenses and Skill Safety Certifications uploaded by Workers."""
    __tablename__ = 'worker_certifications'

    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='CASCADE'), nullable=False)
    
    cert_title = db.Column(db.String(200), nullable=False)  # e.g., 'Electrician Master License', 'NSDC Level 4'
    issuing_body = db.Column(db.String(150), nullable=True)
    cert_number = db.Column(db.String(100), nullable=True)
    document_file = db.Column(db.String(255), nullable=True)
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # 'Pending', 'Verified', 'Rejected'
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    worker = db.relationship('Worker', backref=db.backref('trade_certifications', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<WorkerCertification {self.cert_title} Worker:{self.worker_id} Status:{self.status}>'
