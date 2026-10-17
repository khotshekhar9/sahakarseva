import unittest
import time
from datetime import datetime
from app import app, db
from models.user import User
from models.worker import Worker
from models.service_request import ServiceRequest

class TestOtpStateSync(unittest.TestCase):
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
            Payment.query.filter(Payment.description.like('%EMG-TEST-SYNC%')).delete()
            test_srs = ServiceRequest.query.filter(ServiceRequest.request_id.like('EMG-TEST-SYNC%')).all()
            for sr in test_srs:
                Payment.query.filter_by(service_request_id=sr.id).delete()
                db.session.delete(sr)
            db.session.commit()

    def _login(self, user_id=None):
        if user_id is None:
            user_id = self.worker_user_id
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_worker_verify_arrival_otp_transitions_to_in_progress(self):
        """Verify that worker entering OTP transitions status to 'In Progress' and sets arrived_at."""
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="EMG-TEST-SYNC01",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Chembur West, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=self.contractor_id,
                category="Electrical",
                title="Emergency Sparking",
                status="Travelling",
                priority="Emergency",
                is_emergency=True,
                otp="123456",
                otp_verified=False,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.created_sr_ids.append(sr_id)

        self._login(self.worker_user_id)  # Worker
        resp = self.client.post(f'/worker/service-request/{sr_id}/verify-arrival-otp',
                                data={'arrival_otp': '123456'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            updated = db.session.get(ServiceRequest, sr_id)
            self.assertTrue(updated.otp_verified)
            self.assertEqual(updated.status, 'In Progress')
            self.assertIsNotNone(updated.arrived_at)

    def test_customer_verify_otp_transitions_to_in_progress(self):
        """Verify that customer OTP verification transitions status to 'In Progress' and sets arrived_at."""
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="EMG-TEST-SYNC02",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Chembur West, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=self.contractor_id,
                category="Electrical",
                title="Emergency Sparking",
                status="Travelling",
                priority="Emergency",
                is_emergency=True,
                otp="654321",
                otp_verified=False,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.created_sr_ids.append(sr_id)

        self._login(self.customer_user_id)  # Customer
        resp = self.client.post(f'/customer/booking/{sr_id}/verify-otp',
                                data={'otp': '654321'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            updated = db.session.get(ServiceRequest, sr_id)
            self.assertTrue(updated.otp_verified)
            self.assertEqual(updated.status, 'In Progress')
            self.assertIsNotNone(updated.arrived_at)

    def test_worker_portal_card_renders_work_execution_form_when_otp_verified(self):
        """
        Verify that in /worker/service-requests, when otp_verified is True
        (even if legacy status was Travelling), Case 2 (Active Work Execution Form) renders:
        - Shows 'Service In Progress' header
        - Shows 'OTP Verified' badge
        - Shows inputs: hours_worked, materials_used, work_notes, and 'Mark Job Completed' button.
        """
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="EMG-TEST-SYNC03",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Chembur West, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=self.contractor_id,
                category="Electrical",
                title="Emergency Sparking",
                status="Travelling",  # Legacy desynced status
                priority="Emergency",
                is_emergency=True,
                otp="999888",
                otp_verified=True,    # OTP is verified!
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.created_sr_ids.append(sr_id)

        self._login(self.worker_user_id)  # Worker
        resp = self.client.get('/worker/service-requests')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('job-progress-panel', html)
        self.assertIn('Work In Progress', html)
        self.assertIn('OTP Verified', html)
        self.assertIn('hours_worked', html)
        self.assertIn('materials_used', html)
        self.assertIn('work_notes', html)
        self.assertIn('Mark Job Completed', html)

    def test_worker_portal_card_renders_arrival_card_when_unverified(self):
        """
        Verify that in /worker/service-requests, when otp_verified is False
        and status is Travelling/Assigned, Case 3 (Arrival Card) renders:
        - Shows 'Confirm Site Arrival'
        - Shows high-contrast arrival-card styling
        - Shows 6-digit OTP input and 'Verify & Start' button.
        """
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="EMG-TEST-SYNC04",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Chembur West, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=self.contractor_id,
                category="Electrical",
                title="Emergency Sparking",
                status="Travelling",
                priority="Emergency",
                is_emergency=True,
                otp="112233",
                otp_verified=False,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.created_sr_ids.append(sr_id)

        self._login(self.worker_user_id)  # Worker
        resp = self.client.get('/worker/service-requests')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('arrival-card', html)
        self.assertIn('Confirm Site Arrival', html)
        self.assertIn('arrival_otp', html)
        self.assertIn('Verify & Start', html)

    def test_worker_complete_job_submits_execution_form(self):
        """
        Verify that submitting the completion form updates time_worked,
        materials_used, completion_notes, and marks job completed.
        """
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="EMG-TEST-SYNC05",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Chembur West, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=self.contractor_id,
                category="Electrical",
                title="Emergency Sparking",
                status="In Progress",
                priority="Emergency",
                is_emergency=True,
                otp="334455",
                otp_verified=True,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.created_sr_ids.append(sr_id)

        self._login(self.worker_user_id)  # Worker
        resp = self.client.post(f'/worker/service-request/{sr_id}/complete',
                                data={
                                    'request_id': 'EMG-TEST-SYNC05',
                                    'hours_worked': '2.5',
                                    'materials_used': '32A MCB switch, copper wire',
                                    'work_notes': 'Replaced damaged breaker and secured terminals.',
                                    'progress': '100'
                                },
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            updated = db.session.get(ServiceRequest, sr_id)
            self.assertIn(updated.status, ['Work Completed', 'Completed'])
            self.assertEqual(float(updated.time_worked), 2.5)
            self.assertEqual(updated.materials_used, '32A MCB switch, copper wire')
            self.assertIn('Replaced damaged breaker', updated.completion_notes)

if __name__ == '__main__':
    unittest.main()
