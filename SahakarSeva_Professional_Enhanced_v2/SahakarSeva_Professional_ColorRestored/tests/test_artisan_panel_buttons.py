import unittest
import time
from datetime import datetime, date
from app import app, db
from models.user import User
from models.worker import Worker
from models.attendance import Attendance
from models.finance import Payment
from models.service_request import ServiceRequest
from models.worker_features import WorkerCertification
from models.customer import Customer

class TestArtisanPanelButtons(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def _login_as_artisan(self):
        with self.app.app_context():
            worker_user = User.query.filter_by(username='jdoe').first()
            if not worker_user:
                worker_user = User.query.filter_by(role='worker').first()
            self.worker_id = worker_user.id
            cust = Customer.query.first()
            self.customer_id = cust.id if cust else 1
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.worker_id)  # John Doe (worker)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_01_all_artisan_pages_render_successfully(self):
        """Verify all 7 artisan panel views load cleanly with status 200."""
        self._login_as_artisan()
        endpoints = [
            '/worker/dashboard',
            '/worker/service-requests',
            '/worker/attendance',
            '/worker/earnings',
            '/worker/benefits',
            '/worker/certificates',
            '/worker/profile'
        ]
        for ep in endpoints:
            with self.subTest(endpoint=ep):
                resp = self.client.get(ep)
                self.assertEqual(resp.status_code, 200, f"Endpoint {ep} failed with {resp.status_code}")

    def test_02_duty_availability_toggle_button(self):
        """Verify duty availability toggle switch endpoint."""
        self._login_as_artisan()
        # Toggle to unavailable
        resp = self.client.post('/worker/api/toggle-availability',
                                json={'status': 'unavailable'},
                                headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['availability_status'], 'unavailable')

        # Toggle back to available
        resp2 = self.client.post('/worker/api/toggle-availability',
                                 json={'status': 'available'},
                                 headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()
        self.assertEqual(data2['status'], 'success')
        self.assertEqual(data2['availability_status'], 'available')

    def test_03_attendance_punch_in_and_out_buttons(self):
        """Verify Punch In and Punch Out buttons work with AJAX."""
        self._login_as_artisan()
        with self.app.app_context():
            # Clean today's attendance for worker
            Attendance.query.filter_by(worker_id=self.worker_id, date=date.today()).delete()
            db.session.commit()

        # Punch In
        resp_in = self.client.post('/worker/attendance/check-in',
                                   data={'project_id': 1, 'lat': 0.0, 'lng': 0.0},
                                   headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(resp_in.status_code, 200)
        data_in = resp_in.get_json()
        self.assertEqual(data_in['status'], 'success')

        # Punch Out
        resp_out = self.client.post('/worker/attendance/check-out',
                                    data={'lat': 0.0, 'lng': 0.0},
                                    headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(resp_out.status_code, 200)
        data_out = resp_out.get_json()
        self.assertEqual(data_out['status'], 'success')

    def test_04_download_payslip_button(self):
        """Verify the Download Payslip button generates valid PDF."""
        self._login_as_artisan()
        with self.app.app_context():
            p = Payment.query.filter_by(worker_id=self.worker_id).first()
            if not p:
                p = Payment(worker_id=self.worker_id, amount=750.0, status='Paid', date=date.today(), description='Test Payout')
                db.session.add(p)
                db.session.commit()
            pid = p.id

        resp = self.client.get(f'/worker/payslip/download/{pid}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get('Content-Type'), 'application/pdf')

    def test_05_profile_save_changes_button(self):
        """Verify Save Changes button on Profile page."""
        self._login_as_artisan()
        resp = self.client.post('/worker/api/profile/update', data={
            'username': 'jdoe',
            'email': 'john.doe@example.com',
            'phone': '+91-9876543210',
            'experience_years': 5,
            'skills': 'Electrical, Motor Rewinding, Safety Wiring',
            'address': 'Flat 201, Kurla West, Mumbai',
            'emergency_contact': 'Mary Doe - 9876500000',
            'bank_details': 'HDFC0001234 - 50100234567890'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')

    def test_06_verify_arrival_otp_ajax_button(self):
        """Verify that Verify & Start button returns clean JSON when AJAX request is made."""
        self._login_as_artisan()
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="TEST-BTN-OTP-01",
                customer_id=self.customer_id,
                customer_name="Test Customer",
                mobile_number="+91-9988776655",
                address="Bandra East, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=1,
                category="Electrical",
                title="Test Circuit Repair",
                status="Travelling",
                otp="456789",
                otp_verified=False,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id

        try:
            # 1. Test invalid OTP returns JSON error
            resp_err = self.client.post(f'/worker/service-request/{sr_id}/verify-arrival-otp',
                                        data={'arrival_otp': '000000'},
                                        headers={'X-Requested-With': 'XMLHttpRequest'})
            self.assertEqual(resp_err.status_code, 400)
            err_data = resp_err.get_json()
            self.assertEqual(err_data['status'], 'error')
            self.assertIn('Invalid OTP', err_data['message'])

            # 2. Test valid OTP returns JSON success
            resp_ok = self.client.post(f'/worker/service-request/{sr_id}/verify-arrival-otp',
                                       data={'arrival_otp': '456789'},
                                       headers={'X-Requested-With': 'XMLHttpRequest'})
            self.assertEqual(resp_ok.status_code, 200)
            ok_data = resp_ok.get_json()
            self.assertEqual(ok_data['status'], 'success')

            with self.app.app_context():
                updated = db.session.get(ServiceRequest, sr_id)
                self.assertTrue(updated.otp_verified)
                self.assertEqual(updated.status, 'In Progress')
        finally:
            with self.app.app_context():
                sr_del = db.session.get(ServiceRequest, sr_id)
                if sr_del:
                    db.session.delete(sr_del)
                    db.session.commit()

    def test_07_mark_job_completed_ajax_button(self):
        """Verify that Mark Job Completed button returns clean JSON when AJAX request is made."""
        self._login_as_artisan()

        # 1. Verify that HTML page renders the button with ID and data attributes
        page_resp = self.client.get('/worker/service-requests')
        self.assertEqual(page_resp.status_code, 200)
        page_html = page_resp.get_data(as_text=True)
        # Check that button element markup exists
        self.assertIn('mark_job_completed_ajax_button', page_html)

        # 2. Test AJAX completion execution via URL path (/service-request/<id>/complete)
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="TEST-BTN-COMP-01",
                customer_id=self.customer_id,
                customer_name="Test Customer",
                mobile_number="+91-9988776655",
                address="Bandra East, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=1,
                category="Electrical",
                title="Test Circuit Repair",
                status="In Progress",
                otp="456789",
                otp_verified=True,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id

        try:
            resp = self.client.post(f'/worker/service-request/{sr_id}/complete',
                                    data={
                                        'job_id': sr_id,
                                        'hours_worked': '2.0',
                                        'progress': '100',
                                        'materials_used': '16A Switch, Copper Wire',
                                        'work_notes': 'Successfully replaced burnt switchboard.'
                                    },
                                    headers={'X-Requested-With': 'XMLHttpRequest'})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data['status'], 'success')
            self.assertIn('marked as completed', data['message'])

            with self.app.app_context():
                updated = db.session.get(ServiceRequest, sr_id)
                self.assertEqual(updated.status, 'Work Completed')
        finally:
            with self.app.app_context():
                sr_del = db.session.get(ServiceRequest, sr_id)
                if sr_del:
                    db.session.delete(sr_del)
                    db.session.commit()

        # 3. Test AJAX completion execution via general POST (/service-request/complete)
        with self.app.app_context():
            sr2 = ServiceRequest(
                request_id="TEST-BTN-COMP-02",
                customer_id=self.customer_id,
                customer_name="Test Customer 2",
                mobile_number="+91-9988776655",
                address="Andheri East, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=1,
                category="Plumbing",
                title="Test Pipe Repair",
                status="In Progress",
                otp_verified=True,
                created_at=datetime.utcnow()
            )
            db.session.add(sr2)
            db.session.commit()
            sr2_id = sr2.id

        try:
            resp2 = self.client.post('/worker/service-request/complete',
                                     data={
                                         'job_id': sr2_id,
                                         'work_notes': 'Pipe joints sealed tightly.'
                                     },
                                     headers={'X-Requested-With': 'XMLHttpRequest'})
            self.assertEqual(resp2.status_code, 200)
            data2 = resp2.get_json()
            self.assertEqual(data2['status'], 'success')

            with self.app.app_context():
                updated2 = db.session.get(ServiceRequest, sr2_id)
                self.assertEqual(updated2.status, 'Work Completed')
        finally:
            with self.app.app_context():
                sr2_del = db.session.get(ServiceRequest, sr2_id)
                if sr2_del:
                    db.session.delete(sr2_del)
                    db.session.commit()

    def mark_job_completed_ajax_button(self):
        """Direct method execution alias for mark_job_completed_ajax_button."""
        return self.test_07_mark_job_completed_ajax_button()

    def test_mark_job_completed_ajax_button(self):
        """Test runner alias for test_07_mark_job_completed_ajax_button."""
        return self.test_07_mark_job_completed_ajax_button()

    def test_08_save_draft_progress_button(self):
        """Verify Save Draft progress button endpoint."""
        self._login_as_artisan()
        with self.app.app_context():
            sr = ServiceRequest(
                request_id="TEST-BTN-DRAFT-01",
                customer_id=self.customer_id,
                customer_name="Test Customer",
                mobile_number="+91-9988776655",
                address="Bandra East, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=1,
                category="Electrical",
                title="Test Circuit Repair",
                status="In Progress",
                otp_verified=True,
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id

        try:
            resp = self.client.post(f'/worker/api/service-job/{sr_id}/update-progress',
                                    data={
                                        'hours_worked': '1.0',
                                        'progress': '50',
                                        'materials_used': 'Wire',
                                        'work_notes': 'Initial diagnostic complete.'
                                    },
                                    headers={'X-Requested-With': 'XMLHttpRequest'})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data['status'], 'success')
        finally:
            with self.app.app_context():
                sr_del = db.session.get(ServiceRequest, sr_id)
                if sr_del:
                    db.session.delete(sr_del)
                    db.session.commit()

    def test_09_certificates_upload_button(self):
        """Verify Upload New Certificate modal form submit button."""
        self._login_as_artisan()
        unique_title = f"ITI Electrical Badge {int(time.time())}"
        resp = self.client.post('/worker/certificates/upload', data={
            'cert_title': unique_title,
            'issuing_body': 'State Board of Vocational Education',
            'cert_number': 'SBVE-2026-9901',
            'issue_date': '2024-01-15'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn(unique_title, html)

    def test_10_worker_jobs_filter_categories_and_badges(self):
        """Verify that My Jobs page correctly tags active and completed jobs, and renders filter pill badges."""
        self._login_as_artisan()

        # Create one assigned active job and one completed job for worker
        with self.app.app_context():
            active_sr = ServiceRequest(
                request_id="TEST-ACTIVE-FILTER-01",
                customer_id=self.customer_id,
                customer_name="Test Customer Active",
                mobile_number="+91-9988771122",
                address="Andheri East, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=1,
                category="Electrical",
                title="Switchboard repair",
                status="Travelling",
                otp="123456",
                otp_verified=False,
                created_at=datetime.utcnow()
            )
            completed_sr = ServiceRequest(
                request_id="TEST-COMPLETED-FILTER-01",
                customer_id=self.customer_id,
                customer_name="Test Customer Completed",
                mobile_number="+91-9988771123",
                address="Dadar, Mumbai",
                assigned_worker_id=self.worker_id,
                contractor_id=1,
                category="Electrical",
                title="Fan regulator replacement",
                status="Completed",
                otp="654321",
                otp_verified=True,
                created_at=datetime.utcnow()
            )
            db.session.add(active_sr)
            db.session.add(completed_sr)
            db.session.commit()
            active_id = active_sr.id
            completed_id = completed_sr.id

        try:
            resp = self.client.get('/worker/service-requests')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # 1. Filter pill badges exist
            self.assertIn('id="filter-active-btn"', html)
            self.assertIn('id="filter-completed-btn"', html)
            self.assertIn('Active / En Route', html)

            # 2. Active job (status Travelling) MUST be categorized as data-category="active"
            self.assertIn(f'id="job-{active_id}"', html)
            self.assertIn('data-category="active"', html)

            # 3. Completed job MUST be categorized as data-category="completed"
            self.assertIn(f'id="job-{completed_id}"', html)
            self.assertIn('data-category="completed"', html)

            # 4. Ensure no job cards have the broken "pending" category
            self.assertNotIn('data-category="pending"', html)
        finally:
            with self.app.app_context():
                a_del = db.session.get(ServiceRequest, active_id)
                c_del = db.session.get(ServiceRequest, completed_id)
                if a_del:
                    db.session.delete(a_del)
                if c_del:
                    db.session.delete(c_del)
                db.session.commit()

if __name__ == '__main__':
    unittest.main()
