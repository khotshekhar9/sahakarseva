import unittest
from app import create_app
from database import db
from models.user import User
from models.worker import Worker
from models.contractor import Contractor
from models.service_request import ServiceRequest
from models.finance import Payment
from models.communication import Notification

class TestWorkerJobClaiming(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def login(self, username, password='password123'):
        return self.client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

    def test_e2e_worker_job_claim_flow(self):
        print("\n--- Testing E2E Worker Job Self-Claiming Flow ---")
        
        # 1. Customer creates a booking
        self.login('anita_deshmukh')
        with self.app.app_context():
            contractor = Contractor.query.first()
            self.assertIsNotNone(contractor)

            res = self.client.post('/customer/book-service/submit', data={
                'category': 'Electrician',
                'title': 'Kitchen MCB Tripping Issue',
                'description': 'Main kitchen MCB trips when refrigerator starts',
                'address': 'Flat 304, Sindhi Society, Chembur, Mumbai',
                'preferred_date': '2026-10-01',
                'preferred_time': '11:00',
                'priority': 'Normal',
                'contractor_id': contractor.id,
                'customer_name': 'Anita Deshmukh',
                'mobile_number': '9820011223'
            })
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            req_id_str = data.get('request_id')
            print(f" [PASS] 1. Customer created request: {req_id_str}")

            sr = ServiceRequest.query.filter_by(request_id=req_id_str).first()
            self.assertIsNotNone(sr)
            self.assertIsNone(sr.assigned_worker_id)
            job_db_id = sr.id

        self.client.get('/logout')

        # 2. Worker (jdoe - Master Electrician in Society 1) logs in and checks available jobs
        self.login('jdoe')
        worker_page_res = self.client.get('/worker/service-requests')
        self.assertEqual(worker_page_res.status_code, 200)
        page_html = worker_page_res.get_data(as_text=True)
        self.assertIn("Available Jobs for You", page_html)
        self.assertIn(req_id_str, page_html)
        print(f" [PASS] 2. Worker jdoe sees unassigned job {req_id_str} in Open Cooperative Pool")

        # 3. Worker claims the job
        claim_res = self.client.post(f'/worker/service-requests/{job_db_id}/claim', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(claim_res.status_code, 200)
        claim_data = claim_res.get_json()
        self.assertEqual(claim_data.get('status'), 'success')
        print(f" [PASS] 3. Worker jdoe successfully claimed job #{job_db_id}")

        # 4. Verify Database state: assigned to jdoe, status='Assigned', 88/8/4 payment split created
        with self.app.app_context():
            updated_sr = ServiceRequest.query.get(job_db_id)
            jdoe_worker = Worker.query.get(User.query.filter_by(username='jdoe').first().id)
            self.assertEqual(updated_sr.assigned_worker_id, jdoe_worker.id)
            self.assertEqual(updated_sr.status, 'Assigned')
            self.assertIsNotNone(updated_sr.otp)

            # Check statutory payment record created
            pay = Payment.query.filter_by(service_request_id=job_db_id, type='revenue').first()
            self.assertIsNotNone(pay)
            self.assertEqual(pay.worker_id, jdoe_worker.id)
            self.assertAlmostEqual(float(pay.worker_payout), float(pay.amount) * 0.88, places=1)
            self.assertAlmostEqual(float(pay.welfare_cess), float(pay.amount) * 0.04, places=1)
            print(f" [PASS] 4. Job assigned to jdoe: Payout Rs. {pay.worker_payout} (88%), Welfare Rs. {pay.welfare_cess} (4%)")

            # Check Customer Notification
            cust_notif = Notification.query.filter_by(user_id=updated_sr.customer_id).order_by(Notification.id.desc()).first()
            self.assertIsNotNone(cust_notif)
            self.assertIn("Artisan Accepted", cust_notif.title)
            print(f" [PASS] 5. Customer notified: '{cust_notif.message}'")

        self.client.get('/logout')

        # 5. Concurrency protection: Another worker (savitri) attempts to claim the same job
        self.login('savitri')
        double_claim_res = self.client.post(f'/worker/service-requests/{job_db_id}/claim', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(double_claim_res.status_code, 409)
        double_data = double_claim_res.get_json()
        self.assertTrue(double_data.get('already_claimed'))
        print(f" [PASS] 6. Concurrency lock prevented duplicate claim by savitri: '{double_data.get('message')}'")

if __name__ == '__main__':
    unittest.main()
