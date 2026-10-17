from database import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    type = db.Column(db.String(20), default='Info')  # 'Alert', 'Info', 'Success', 'Warning'
    priority = db.Column(db.String(20), default='Normal', nullable=False)

    user = db.relationship('User', backref='notifications')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return f'<Notification {self.id} User:{self.user_id} Read:{self.is_read}>'


class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Open')  # 'Open', 'In Progress', 'Resolved', 'Escalated', 'Notice Issued'
    priority = db.Column(db.String(20), default='Medium')  # 'Low', 'Medium', 'High', 'Emergency'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Apex Escalation & Conciliation Fields
    target_tier = db.Column(db.String(20), default='society')  # 'society', 'apex'
    escalation_level = db.Column(db.String(20), default='society')
    is_apex_dispute = db.Column(db.Boolean, default=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id', ondelete='SET NULL'), nullable=True)
    contractor_name = db.Column(db.String(150), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    arbitration_action = db.Column(db.String(100), nullable=True)

    # Relationships
    contractor = db.relationship('Contractor', backref='support_tickets')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return f'<SupportTicket {self.id} Title:{self.title} Status:{self.status} Tier:{self.target_tier}>'


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    entity_type = db.Column(db.String(50), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    user = db.relationship('User', backref='activity_logs')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @staticmethod
    def log_activity(user_id, action, details, old_val=None, new_val=None, ip=None, entity_type=None, entity_id=None):
        try:
            log = ActivityLog(
                user_id=user_id,
                action=action,
                details=details,
                old_value=str(old_val) if old_val is not None else None,
                new_value=str(new_val) if new_val is not None else None,
                ip_address=ip or "127.0.0.1",
                entity_type=entity_type,
                entity_id=entity_id
            )
            db.session.add(log)
        except Exception as e:
            print(f"[ActivityLog] Log failed: {e}")


class LoginHistory(db.Model):
    __tablename__ = 'login_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Success')  # 'Success', 'Failed'
    
    user = db.relationship('User', backref='login_histories')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class SystemAnnouncement(db.Model):
    __tablename__ = 'system_announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_role = db.Column(db.String(50), default='all')  # 'all', 'admin', 'worker', 'customer'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    created_by = db.relationship('User', foreign_keys=[created_by_id])

    def __repr__(self):
        return f'<SystemAnnouncement {self.title}>'


class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, nullable=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def get_val(cls, key, default=''):
        s = cls.query.filter_by(key=key).first()
        return s.value if s else default

    @classmethod
    def set_val(cls, key, value, description=''):
        s = cls.query.filter_by(key=key).first()
        if not s:
            s = cls(key=key, value=str(value))
            db.session.add(s)
        else:
            s.value = str(value)
        return s

    def __repr__(self):
        return f'<SystemSettings {self.key}={self.value}>'


# Aliases for backward compatibility
SystemSetting = SystemSettings
PlatformSetting = SystemSettings
