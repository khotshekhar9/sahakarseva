from database import db
from datetime import datetime

class ContractorDocument(db.Model):
    """Centralized Document Vault for Contractor Contracts, Permits, Worker Certifications, and Insurance."""
    __tablename__ = 'contractor_documents'

    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id', ondelete='CASCADE'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='SET NULL'), nullable=True)
    project_id = db.Column(db.Integer, nullable=True)  # Legacy compatibility column
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='SET NULL'), nullable=True)

    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), default='Contract')  # 'Contract', 'Site Permit', 'Insurance Policy', 'Worker License', 'Safety Cert'
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.String(50), nullable=True)        # e.g. "1.2 MB"
    notes = db.Column(db.Text, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    contractor = db.relationship('Contractor', backref=db.backref('documents', cascade='all, delete-orphan'))
    worker = db.relationship('Worker', backref='certifications')
    service_request = db.relationship('ServiceRequest', backref='permits_and_contracts')

    @property
    def project(self):
        return self.service_request

    def __repr__(self):
        return f'<ContractorDocument {self.title} ({self.category})>'
