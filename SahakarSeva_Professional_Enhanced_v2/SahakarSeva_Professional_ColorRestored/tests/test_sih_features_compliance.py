import unittest
from app import create_app
from database import db
from models.user import User
from models.customer import Customer
from models.worker import Worker
from models.contractor import Contractor
from models.service_request import ServiceRequest
from models.finance import Payment, WelfareTransaction
from models.communication import SupportTicket, Notification, SystemSettings
from services.dispatch_service import DispatchService
from services.welfare_service import WelfareService

class TestSIHFeaturesCompliance(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def login(self, username, password='password123'):
        return self.client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

    def test_01_all_four_roles_accessible(self):
        # 1. Customer
        self.login('anita_deshmukh')
        for r in ['/customer/dashboard', '/customer/book-service', '/customer/bookings', '/customer/payments', '/customer/help', '/customer/profile']:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200)
        self.client.get('/logout')

        # 2. Worker
        self.login('ramesh')
        for r in ['/worker/dashboard', '/worker/service-requests', '/worker/attendance', '/worker/earnings', '/worker/benefits', '/worker/certificates', '/worker/profile']:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200)
        self.client.get('/logout')

        # 3. Admin
        self.login('admin')
        for r in ['/admin/dashboard', '/admin/service-requests', '/admin/workers', '/admin/attendance', '/admin/payments', '/admin/ai-demand', '/admin/settings']:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200)
        self.client.get('/logout')

        # 4. Publisher
        self.login('publisher')
        for r in ['/publisher/dashboard', '/publisher/societies', '/publisher/complaints', '/publisher/money', '/publisher/settings', '/publisher/profile']:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200)
        self.client.get('/logout')

    def test_02_database_integrity_22_tables(self):
        with self.app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = sorted(inspector.get_table_names())
            self.assertEqual(len(tables), 22)

    def test_03_booking_and_otp_generation(self):
        self.login('anita_deshmukh')
        with self.app.app_context():
            contractor = Contractor.query.first()
            res = self.client.post('/customer/book-service/submit', data={
                'category': 'Electrician',
                'title': 'Fuse Replacement',
                'description': 'Fuse tripped in main board',
                'address': 'Chembur Colony, Mumbai',
                'preferred_date': '2026-09-30',
                'contractor_id': contractor.id,
                'customer_name': 'Anita Deshmukh',
                'mobile_number': '9820011223'
            })
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            sr = ServiceRequest.query.filter_by(request_id=data.get('request_id')).first()
            self.assertIsNotNone(sr)
            self.assertIsNotNone(sr.otp)
            self.assertEqual(len(str(sr.otp)), 4)

    def test_04_welfare_split_88_8_4(self):
        split = WelfareService.calculate_cess_split(1000.0, split_mode="88_8_4")
        self.assertEqual(split['worker_payout'], 880.0)
        self.assertEqual(split['society_admin_fee'], 80.0)
        self.assertEqual(split['welfare_cess'], 40.0)

if __name__ == '__main__':
    unittest.main()
