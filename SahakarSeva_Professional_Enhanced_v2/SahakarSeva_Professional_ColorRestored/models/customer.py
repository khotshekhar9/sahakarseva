from database import db

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    company_name = db.Column(db.String(100), nullable=True)
    billing_address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.Text, nullable=True)

    @property
    def projects(self):
        # Compatibility property returning customer service requests
        return self.service_requests

    payments = db.relationship('Payment', backref='customer', lazy='dynamic')
    support_tickets = db.relationship('SupportTicket', backref='customer', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Customer {self.id} Company:{self.company_name}>'
