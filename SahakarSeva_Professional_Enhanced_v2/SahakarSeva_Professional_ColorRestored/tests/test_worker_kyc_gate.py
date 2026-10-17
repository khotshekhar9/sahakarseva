import unittest
import time
import json
from app import app, db
from models.user import User
from models.worker import Worker
from models.contractor import Contractor
from models.service_request import ServiceRequest
from services.dispatch_service import DispatchService

class TestWorkerKYCGate(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.clean_user_ids = []
        self.clean_request_ids = []

    def tearDown(self):
        with self.app.app_context():
            for req_id in self.clean_request_ids:
                sr = db.session.get(ServiceRequest, req_id)
                if sr:
                    db.session.delete(sr)
            for uid in self.clean_user_ids:
                w = db.session.get(Worker, uid)
                if w:
                    db.session.delete(w)
                u = db.session.get(User, uid)
                if u:
                    db.session.delete(u)
            db.session.commit()

    def _login(self, user_id):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_worker_registration_kyc_defaults(self):
        """Worker registration must initialize is_verified=False, verification_status='pending', availability_status='pending_verification'."""
        ts = int(time.time() * 1000) % 1000000
        username = f"testworker_{ts}"
        email = f"worker_{ts}@test.coop"

        resp = self.client.post('/register', data={
            'role': 'worker',
            'username': username,
            'email': email,
            'password': 'password123',
            'phone': '9820099999',
            'address': 'Nehru Nagar, Kurla East, Mumbai - 400024',
            'skills': 'Carpentry, Furniture Assembly',
            'experience_years': '4',
            'salary_rate': '480'
        }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        content = resp.get_data(as_text=True)
        self.assertIn("Registration received", content)

        with self.app.app_context():
            user = User.query.filter_by(username=username).first()
            self.assertIsNotNone(user)
            self.clean_user_ids.append(user.id)

            worker = db.session.get(Worker, user.id)
            self.assertIsNotNone(worker)
            self.assertFalse(worker.is_verified)
            self.assertEqual(worker.verification_status, 'pending')
            self.assertEqual(worker.availability_status, 'pending_verification')

    def test_dispatch_service_excludes_unverified_workers(self):
        """Unverified workers must not appear in available worker dispatch or receive broadcasts."""
        with self.app.app_context():
            # Worker 15 (sunil_plumber) is seeded as unverified (is_verified=False, verification_status='pending')
            unverified_worker = db.session.get(Worker, 15)
            self.assertIsNotNone(unverified_worker)
            self.assertFalse(unverified_worker.is_verified)
            self.assertEqual(unverified_worker.verification_status, 'pending')

            # Search available nearby workers for Plumbing in Kurla East
            candidates = DispatchService.find_nearby_available_workers(
                category="Plumbing",
                lat=19.0626,
                lng=72.8797,
                radius_km=15.0
            )

            candidate_ids = [c['worker'].id for c in candidates]
            self.assertNotIn(15, candidate_ids, "Unverified worker must NOT be present in candidate pool")

            # Check broadcasts for unverified worker
            broadcasts = DispatchService.get_pending_broadcasts_for_worker(15)
            self.assertEqual(broadcasts, [], "Unverified worker must receive empty broadcasts list")

    def test_unverified_worker_emergency_claim_rejected_with_403(self):
        """Claiming an emergency job while unverified must be rejected with HTTP 403."""
        with self.app.app_context():
            ts = int(time.time() * 1000) % 1000000
            sr = ServiceRequest(
                request_id=f"SR-EMG-{ts:06d}",
                customer_id=11,
                customer_name="Anita Sharma",
                mobile_number="9820030001",
                category="Plumbing",
                title="Burst Kitchen Pipe",
                address="Chheda Nagar, Chembur West, Mumbai - 400089",
                status="Broadcast",
                priority="Emergency",
                is_emergency=True,
                contractor_id=1
            )
            db.session.add(sr)
            db.session.commit()
            self.clean_request_ids.append(sr.id)
            sr_id = sr.id

        # Authenticate as unverified worker 15
        self._login(15)
        resp = self.client.post(f'/worker/emergency-claim/{sr_id}', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(resp.status_code, 403)
        data = resp.get_json()
        self.assertFalse(data['success'])
        self.assertIn("KYC approval required", data['message'])

    def test_unverified_worker_cannot_toggle_availability(self):
        """Unverified workers cannot toggle availability to available; returns HTTP 403."""
        self._login(15)
        resp = self.client.post('/worker/api/toggle-availability', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(resp.status_code, 403)
        data = resp.get_json()
        self.assertEqual(data['status'], 'error')
        self.assertIn("verification", data['message'].lower())

    def test_society_admin_verify_and_reject_worker_lifecycle(self):
        """Society admin can approve and reject workers via AJAX endpoints with proper status updates."""
        # Authenticate as Society Admin (User ID 2, Chembur Society)
        self._login(2)

        # 1. Approve worker 15
        resp = self.client.post('/admin/workers/15/verify', headers={
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn("approved", data['message'].lower())

        with self.app.app_context():
            w = db.session.get(Worker, 15)
            self.assertTrue(w.is_verified)
            self.assertEqual(w.verification_status, 'approved')
            self.assertEqual(w.availability_status, 'available')

        # 2. Reject worker 15
        resp = self.client.post('/admin/workers/15/reject', headers={
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn("rejected", data['message'].lower())

        with self.app.app_context():
            w = db.session.get(Worker, 15)
            self.assertFalse(w.is_verified)
            self.assertEqual(w.verification_status, 'rejected')
            self.assertEqual(w.availability_status, 'inactive')

            # Reset back to pending for other tests
            w.verification_status = 'pending'
            w.availability_status = 'pending_verification'
            db.session.commit()

    def test_worker_dashboard_renders_kyc_status_banner_and_disabled_switch(self):
        """Worker dashboard displays Under Review banner and disabled availability switch when pending."""
        self._login(15)
        resp = self.client.get('/worker/dashboard')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("Under Review:", html)
        self.assertIn("Your society admin is verifying your documents", html)
        self.assertIn("disabled", html)
        self.assertIn("Approval required", html)

if __name__ == '__main__':
    unittest.main()
