from database import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'revenue', 'expense', 'salary'
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    date = db.Column(db.Date, default=datetime.utcnow().date, index=True)
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Paid', 'Overdue'
    
    # Multi-tenant: which contractor this payment belongs to
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id', ondelete='SET NULL'), nullable=True, index=True)
    # Optional Foreign Keys based on type
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='SET NULL'), nullable=True)
    project_id = db.Column(db.Integer, nullable=True)  # Legacy compatibility column
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='SET NULL'), nullable=True)
    
    invoice_number = db.Column(db.String(50), unique=True, nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    receipt_path = db.Column(db.String(255), nullable=True)
    
    # Customer Signature for dynamic contracts/invoices
    signed_by_customer = db.Column(db.Boolean, default=False)
    signature_path = db.Column(db.String(255), nullable=True)
    
    # Billing detailed fields
    quotation_number = db.Column(db.String(50), nullable=True)
    discount = db.Column(db.Numeric(10, 2), default=0.0)
    gst = db.Column(db.Numeric(10, 2), default=0.0)
    labour_cost = db.Column(db.Numeric(10, 2), default=0.0)
    material_cost = db.Column(db.Numeric(10, 2), default=0.0)

    # Cooperative 4-Tier Distribution Fields (90% Worker, 4% Society Admin, 4% Federation, 2% Welfare Cess)
    worker_payout = db.Column(db.Numeric(10, 2), default=0.0)
    society_admin_fee = db.Column(db.Numeric(10, 2), default=0.0)
    federation_fee = db.Column(db.Numeric(10, 2), default=0.0)
    welfare_cess = db.Column(db.Numeric(10, 2), default=0.0)

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('payments', lazy='dynamic'))

    @property
    def project(self):
        return self.service_request

    def __repr__(self):
        return f'<Payment {self.id} Type:{self.type} Amount:{self.amount} Status:{self.status}>'


class WelfareTransaction(db.Model):
    """
    Dedicated audit ledger for the Worker Welfare & Social Security Fund (Suraksha Nidhi).
    Tracks micro-cess credits (2%) and automated insurance auto-debit premiums (PMJJBY/PMSBY).
    """
    __tablename__ = 'welfare_transactions'

    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='CASCADE'), nullable=False, index=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id', ondelete='SET NULL'), nullable=True, index=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id', ondelete='SET NULL'), nullable=True)
    
    # 'CESS_CREDIT', 'PMSBY_PREMIUM', 'PMJJBY_PREMIUM', 'ESIC_BENEFIT', 'WELFARE_GRANT'
    transaction_type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Positive for credit (+₹20.0), Negative for debit (-₹436.0)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    reference_id = db.Column(db.String(100), nullable=True)  # Policy cert no or invoice ref
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    payment = db.relationship('Payment', backref=db.backref('welfare_transactions', lazy='dynamic'))
    service_request = db.relationship('ServiceRequest', backref=db.backref('welfare_transactions', lazy='dynamic'))

    def __repr__(self):
        return f'<WelfareTransaction {self.id} Worker:{self.worker_id} Type:{self.transaction_type} Amount:{self.amount}>'
