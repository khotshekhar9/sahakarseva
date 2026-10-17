import unittest
import time
import json
from datetime import datetime, date
from app import app, db
from models.user import User
from models.worker import Worker
from models.service_request import ServiceRequest

class TestLiveTrackingAndWorkerDiagnostics(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.created_sr_ids = []
        with self.app.app_context():
            from models.customer import Customer
            from models.contractor import Contractor
            cust = Customer.query.first()
            worker = Worker.query.first()
            contractor = Contractor.query.first()
            self.customer_id = cust.id if cust else 17
            self.worker_id = worker.id if worker else 7
            self.contractor_id = contractor.id if contractor else 1
            self.customer_user_id = self.customer_id
            self.worker_user_id = self.worker_id
        self._cleanup_test_records()

    def tearDown(self):
        self._cleanup_test_records()

    def _cleanup_test_records(self):
        with self.app.app_context():
            from models.finance import Payment
            for sr_id in self.created_sr_ids:
                Payment.query.filter_by(service_request_id=sr_id).delete()
                sr = db.session.get(ServiceRequest, sr_id)
                if sr:
                    db.session.delete(sr)
            Payment.query.filter(Payment.description.like('%EMG-2026-TEST%')).delete()
            Payment.query.filter(Payment.description.like('%SR-TEST-PROGRESS%')).delete()
            test_srs = ServiceRequest.query.filter(
                (ServiceRequest.request_id.like('EMG-2026-TEST%')) |
                (ServiceRequest.request_id.like('SR-TEST-PROGRESS%')) |
                (ServiceRequest.request_id.like('REQ-2026-TEST%'))
            ).all()
            for sr in test_srs:
                Payment.query.filter_by(service_request_id=sr.id).delete()
                db.session.delete(sr)
            db.session.commit()

    def _login(self, user_id=None):
        if user_id is None:
            user_id = self.customer_user_id
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_progressive_milestone_stepper_otp_verified(self):
        """
        Verify that for an OTP-verified booking (like #EMG-2026-000009),
        Step 1 & Step 2 show as 'Completed' and Step 3 shows as 'Active Now'
        with the arrival verified description.
        """
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="EMG-2026-TEST01",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                assigned_worker_id=self.worker_id,
                contractor_id=self.contractor_id,
                category="Electrician",
                title="Sparking switchboard test",
                description="Short circuit sparks in hall board",
                status="Assigned",
                priority="Emergency",
                is_emergency=True,
                otp="482910",
                otp_verified=True,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.created_sr_ids.append(sr_id)

        self._login(self.customer_user_id)
        resp = self.client.get(f'/customer/booking/{sr_id}/details')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Worker Assigned must be Completed
        self.assertIn('Worker Assigned', html)
        # Worker Dispatched must be Completed (not Pending)
        self.assertIn('Worker Dispatched', html)
        self.assertNotIn('Artisan will be dispatched on scheduled visit date', html)
        # Service In-Progress must be Active Now with verified arrival
        self.assertIn('Service In-Progress', html)
        self.assertIn('Artisan actively servicing site (Arrival verified)', html)
        self.assertNotIn('Awaiting start verification (OTP:', html)
        # Verify completed line connector styling
        self.assertIn('border-success', html)

    def test_milestone_stepper_unverified_shows_otp_gate(self):
        """
        Verify that for an assigned booking where OTP is NOT verified,
        Step 3 correctly displays 'Awaiting start verification (OTP: ...)'
        """
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="REQ-2026-TEST02",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                assigned_worker_id=self.worker_id,
                contractor_id=self.contractor_id,
                category="Electrician",
                title="Ceiling fan installation",
                status="Assigned",
                priority="Normal",
                otp="554433",
                otp_verified=False,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.created_sr_ids.append(sr_id)

        self._login(self.customer_user_id)
        resp = self.client.get(f'/customer/booking/{sr_id}/details')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Awaiting start verification (OTP: 554433)', html)

    def test_milestone_stepper_completed_job(self):
        """
        Verify that completed/closed bookings show all 4 milestones as completed.
        """
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="REQ-2026-TEST03",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                assigned_worker_id=self.worker_id,
                contractor_id=self.contractor_id,
                category="Electrician",
                title="Completed wiring job",
                status="Completed",
                priority="Normal",
                otp="998877",
                otp_verified=True,
                completion_date=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.created_sr_ids.append(sr_id)

        self._login(self.customer_user_id)
        resp = self.client.get(f'/customer/booking/{sr_id}/details')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Quality verified under SahakarSeva Trust Guarantee', html)
        self.assertIn('Service completed &amp; verified on site', html)

    def test_worker_api_update_location(self):
        """
        Verify /worker/api/update-location:
        - Updates worker coordinates when valid lat/lng are provided
        - Gracefully handles empty payload without raising 400 Bad Request
        """
        self._login(self.worker_user_id)  # Worker

        # 1. Valid coordinates
        resp = self.client.post('/worker/api/update-location',
                                json={'latitude': 19.0626, 'longitude': 72.8797})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')

        with self.app.app_context():
            w = db.session.get(Worker, self.worker_id)
            self.assertAlmostEqual(float(w.latitude), 19.0626, places=4)
            self.assertAlmostEqual(float(w.longitude), 72.8797, places=4)

        # 2. Empty payload / no body must not crash with 400
        resp_empty = self.client.post('/worker/api/update-location',
                                      headers={'Content-Type': 'application/json'})
        self.assertEqual(resp_empty.status_code, 200)

    def test_worker_toggle_availability_empty_body(self):
        """
        Verify /worker/api/toggle-availability safely toggles availability
        even when an empty JSON body or no payload is sent.
        """
        self._login(self.worker_user_id)

        # Toggle with empty body
        resp = self.client.post('/worker/api/toggle-availability',
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')

        # Toggle with explicit status
        resp2 = self.client.post('/worker/api/toggle-availability',
                                 json={'status': 'available'})
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()
        self.assertEqual(data2['availability_status'], 'available')

    def test_worker_dashboard_purges_stray_400_flash(self):
        """
        Verify that navigating to /worker/dashboard purges any stray
        400 Bad Request error from session flashes so no alert banner displays.
        """
        self._login(self.worker_user_id)

        # Inject stray 400 Bad Request flash into session
        with self.client.session_transaction() as sess:
            sess['_flashes'] = [
                ('danger', '400 Bad Request: The browser (or proxy) sent a request that this server could not understand.'),
                ('info', 'Welcome back to your shift!')
            ]

        resp = self.client.get('/worker/dashboard')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # The 400 message must NOT be rendered in flash-data or user alerts
        self.assertNotIn('data-msg="400', html)
        self.assertNotIn('400 Bad Request:', html)

        # The legitimate flash message remains
        self.assertIn('Welcome back to your shift!', html)

if __name__ == '__main__':
    unittest.main()
