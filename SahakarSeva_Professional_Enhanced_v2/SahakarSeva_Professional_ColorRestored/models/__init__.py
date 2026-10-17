from database import db
from models.user import User
from models.contractor import Contractor, ContractorReview
from models.worker import Worker
from models.customer import Customer
from models.document import ContractorDocument
from models.worker_features import WorkerCertification, WorkerTaskChecklist
from models.service_request import ServiceRequest
from models.quotation import Quotation
from models.attendance import Attendance
from models.finance import Payment, WelfareTransaction
from models.communication import (
    Notification, SupportTicket, ActivityLog, LoginHistory,
    SystemAnnouncement, SystemSettings, SystemSetting, PlatformSetting
)
from models.ai_data import AIEstimate, AIDelayPrediction, AIMaterialForecast

# Aliases for Canonical API and Backward Compatibility
AttendanceLog = Attendance

__all__ = [
    'db',
    'User',
    'Contractor',
    'ContractorReview',
    'Worker',
    'Customer',
    'ContractorDocument',
    'WorkerCertification',
    'WorkerTaskChecklist',
    'ServiceRequest',
    'Quotation',
    'Attendance',
    'AttendanceLog',
    'Payment',
    'WelfareTransaction',
    'Notification',
    'SupportTicket',
    'ActivityLog',
    'LoginHistory',
    'SystemAnnouncement',
    'SystemSettings',
    'SystemSetting',
    'PlatformSetting',
    'AIEstimate',
    'AIDelayPrediction',
    'AIMaterialForecast',
]
