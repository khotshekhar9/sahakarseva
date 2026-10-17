import unittest
import time
from datetime import datetime, date, timedelta
from app import app, db
from models.user import User
from models.worker import Worker
from models.customer import Customer
from models.service_request import ServiceRequest
from models.attendance import Attendance


class TestWorkerAttendance(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            # 1. Setup Worker user
            self.user = User.query.filter_by(email='worker_attendance_test@sahakar.coop').first()
            if not self.user:
                self.user = User(
                    username='testartisan_att',
                    email='worker_attendance_test@sahakar.coop',
                    role='worker'
                )
                self.user.set_password('Worker123!')
                db.session.add(self.user)
                db.session.commit()

            self.worker = Worker.query.get(self.user.id)
            if not self.worker:
                self.worker = Worker(
                    id=self.user.id,
                    contractor_id=1,
                    skills='Plumbing, Electrical maintenance',
                    experience_years=4,
                    availability_status='available',
                    is_verified=True,
                    verification_status='approved'
                )
                db.session.add(self.worker)
                db.session.commit()

            # 2. Setup ServiceRequest site
            cust = Customer.query.first()
            cust_id = cust.id if cust else self.user.id

            self.service_request = ServiceRequest.query.filter_by(title='Deonar Heights CHS Annual Society Plumbing & Electrical Maintenance').first()
            if not self.service_request:
                self.service_request = ServiceRequest(
                    request_id='SR-ATT-TEST-001',
                    customer_id=cust_id,
                    customer_name='Deonar Heights CHS',
                    mobile_number='9820030003',
                    category='Plumbing',
                    title='Deonar Heights CHS Annual Society Plumbing & Electrical Maintenance',
                    address='Deonar Heights CHS, P.L. Lokhande Marg, Deonar Colony, Govandi East, Mumbai - 400088',
                    latitude=19.0553,
                    longitude=72.9150,
                    status='In Progress',
                    assigned_worker_id=self.worker.id,
                    contractor_id=1
                )
                db.session.add(self.service_request)
                db.session.commit()
            else:
                self.service_request.assigned_worker_id = self.worker.id
                db.session.commit()

            self.project = self.service_request
            self.project_id = self.service_request.id

            # Clean up today's attendance for this worker to start fresh
            today = date.today()
            Attendance.query.filter_by(worker_id=self.worker.id, date=today).delete()
            ServiceRequest.query.filter(
                ServiceRequest.request_id.in_(['SR-2026-000035', 'SR-2026-000036'])
            ).delete()
            self.service_request.otp_verified = False
            self.service_request.status = 'Assigned'
            db.session.commit()

            # Ensure some historical logs exist
            hist_date = today - timedelta(days=1)
            old_log = Attendance.query.filter_by(worker_id=self.worker.id, date=hist_date).first()
            if not old_log:
                old_log = Attendance(
                    worker_id=self.worker.id,
                    service_request_id=self.service_request.id,
                    project_id=self.service_request.id,
                    date=hist_date,
                    check_in_time=datetime.combine(hist_date, datetime.min.time()).replace(hour=8, minute=5),
                    check_out_time=datetime.combine(hist_date, datetime.min.time()).replace(hour=17, minute=2),
                    status='Present',
                    verified_by_gps=True
                )
                db.session.add(old_log)
                db.session.commit()

            self.worker_id = self.worker.id
            self.project_id = self.service_request.id

    def _login(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.worker_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_attendance_page_renders_with_ux_requirements(self):
        """Test that /worker/attendance displays all key PM/UX elements when not checked in."""
        self._login()
        resp = self.client.get('/worker/attendance')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # 1. Simplified Headings
        self.assertIn('Attendance', html)
        self.assertIn('Punch in at your assigned site and track your work days.', html)

        # 2. Daily Punch Action (Top Card)
        self.assertIn('Not Checked In', html)
        self.assertIn('Punch In for Today', html)
        self.assertIn('Deonar Heights CHS', html)
        self.assertIn('GPS Geofence Verified', html)

        # 3. Daily Performance Snapshot (3 Minimal Metric Chips)
        self.assertIn('Days Active (This Month)', html)
        self.assertIn('Average Daily Hours', html)
        self.assertIn('Attendance Compliance', html)

        # 4. Attendance History (6 Clean Columns)
        self.assertIn('Attendance History', html)
        self.assertIn('Location / Society Site', html)
        self.assertIn('Punch In', html)
        self.assertIn('Punch Out', html)
        self.assertIn('Total Hours', html)
        self.assertIn('Status', html)
        self.assertIn('Present', html)

    def test_one_tap_check_in_and_check_out_flow(self):
        """Test the complete 1-tap check-in and check-out cycle via AJAX."""
        self._login()

        # Step 1: 1-Tap Punch In for Today
        check_in_payload = {
            'service_request_id': self.project_id,
            'lat': 0.0,
            'lng': 0.0
        }
        in_resp = self.client.post(
            '/worker/attendance/check-in',
            data=check_in_payload,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(in_resp.status_code, 200)
        in_data = in_resp.get_json()
        self.assertEqual(in_data['status'], 'success')
        self.assertIn('Successfully punched in', in_data['message'])
        self.assertIn('Deonar Heights CHS', in_data['site_name'])

        # Verify database record
        today = date.today()
        with self.app.app_context():
            log = Attendance.query.filter_by(worker_id=self.worker_id, date=today).first()
            self.assertIsNotNone(log)
            self.assertIsNotNone(log.check_in_time)
            self.assertIsNone(log.check_out_time)

        # Step 2: Page now reflects On Duty / Checked In state
        page_resp = self.client.get('/worker/attendance')
        self.assertEqual(page_resp.status_code, 200)
        page_html = page_resp.get_data(as_text=True)
        self.assertIn('On Duty / Checked In', page_html)
        self.assertIn('Punch Out', page_html)
        self.assertIn('Active Shift Duration', page_html)

        # Step 3: 1-Tap Punch Out
        out_payload = {
            'lat': 0.0,
            'lng': 0.0
        }
        out_resp = self.client.post(
            '/worker/attendance/check-out',
            data=out_payload,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(out_resp.status_code, 200)
        out_data = out_resp.get_json()
        self.assertEqual(out_data['status'], 'success')
        self.assertIn('Successfully punched out', out_data['message'])
        self.assertIsNotNone(out_data.get('duration'))

        # Step 4: Page now reflects Shift Completed state
        final_page_resp = self.client.get('/worker/attendance')
        self.assertEqual(final_page_resp.status_code, 200)
        final_html = final_page_resp.get_data(as_text=True)
        self.assertIn('Shift Completed', final_html)
        self.assertIn("Today's Shift Completed", final_html)

    def test_double_punch_in_prevented(self):
        """Test that duplicate check-ins on the same day are blocked with friendly warning."""
        self._login()

        # First punch in
        self.client.post(
            '/worker/attendance/check-in',
            data={'service_request_id': self.project_id, 'lat': 0, 'lng': 0},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        # Second punch in should be rejected
        dup_resp = self.client.post(
            '/worker/attendance/check-in',
            data={'service_request_id': self.project_id, 'lat': 0, 'lng': 0},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(dup_resp.status_code, 400)
        dup_data = dup_resp.get_json()
        self.assertEqual(dup_data['status'], 'error')
        self.assertIn('Already punched in today', dup_data['message'])

    def _login_admin(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = '2'  # Primary Society Admin User ID 2
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_admin_attendance_panel_renders_clean_summary_and_table(self):
        """Verify /admin/attendance renders modern, user-friendly panel with 4 cards, filters, and scannable table."""
        self._login_admin()
        resp = self.client.get('/admin/attendance')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Header & Subtitle
        self.assertIn('Worker Attendance', html)
        self.assertIn('Track daily artisan check-ins, job site locations, and completed hours.', html)

        # 4 Summary Metric Cards
        self.assertIn('Checked In Today', html)
        self.assertIn('On Site Now', html)
        self.assertIn('Shifts Completed', html)
        self.assertIn('GPS Verified Rate', html)

        # Controls & Table Headers
        self.assertIn('Search artisan or site...', html)
        self.assertIn('Artisan', html)
        self.assertIn('Date', html)
        self.assertIn('Location / Society Site', html)
        self.assertIn('Punch In', html)
        self.assertIn('Punch Out', html)
        self.assertIn('Total Hours', html)
        self.assertIn('Verification', html)
        self.assertIn('Status', html)

    def test_admin_dashboard_section_attendance_renders_modernized_panel(self):
        """Verify Section 5 on /admin/dashboard contains user-friendly Worker Attendance panel."""
        self._login_admin()
        resp = self.client.get('/admin/dashboard')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Worker Attendance', html)
        self.assertIn('Present Today', html)
        self.assertIn('Absent Today', html)
        self.assertIn('Total Verified Logs', html)
    def test_arrival_otp_verification_auto_marks_attendance_present_with_gis(self):
        """Test that on-site OTP verification within 100m geofence automatically records attendance as Present."""
        self._login()
        sr_id = self.service_request.id
        with self.app.app_context():
            # Reset today's attendance & set known OTP
            today = date.today()
            Attendance.query.filter_by(worker_id=self.worker_id, date=today).delete()
            sr = db.session.get(ServiceRequest, sr_id)
            sr.otp = '882244'
            sr.latitude = 19.0553
            sr.longitude = 72.9150
            sr.otp_verified = False
            sr.status = 'Assigned'
            db.session.commit()

        # Worker is ~33m away (within 100m radius)
        resp = self.client.post(
            f'/worker/service-request/{sr_id}/verify-arrival-otp',
            data={
                'arrival_otp': '882244',
                'worker_lat': 19.0556,
                'worker_lng': 72.9150
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')

        # Attendance must be automatically marked Present and verified by GPS
        with self.app.app_context():
            today = date.today()
            att = Attendance.query.filter_by(worker_id=self.worker_id, date=today).first()
            self.assertIsNotNone(att)
            self.assertEqual(att.status, 'Present')
            self.assertTrue(att.verified_by_gps)
            self.assertIsNotNone(att.check_in_time)

    def test_arrival_otp_verification_fails_if_outside_100m_geofence(self):
        """Test that OTP verification is rejected when worker is outside the 100m GIS perimeter."""
        self._login()
        sr_id = self.service_request.id
        with self.app.app_context():
            today = date.today()
            Attendance.query.filter_by(worker_id=self.worker_id, date=today).delete()
            sr = db.session.get(ServiceRequest, sr_id)
            sr.otp = '882244'
            sr.latitude = 19.0553
            sr.longitude = 72.9150
            db.session.commit()

        # Worker is ~550m away (> 100m radius)
        resp = self.client.post(
            f'/worker/service-request/{sr_id}/verify-arrival-otp',
            data={
                'arrival_otp': '882244',
                'worker_lat': 19.0603,
                'worker_lng': 72.9150
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('GIS Geofence Check Failed', data['message'])
        self.assertIn('20–100m', data['message'])

    def test_attendance_auto_status_absent_past_6pm(self):
        """Verify that past 6 PM without OTP verification, attendance auto-marks as Absent."""
        self._login()
        with self.app.app_context():
            today = date.today()
            Attendance.query.filter_by(worker_id=self.worker_id, date=today).delete()
            sr = db.session.get(ServiceRequest, self.service_request.id)
            sr.otp_verified = False
            sr.status = 'Assigned'
            db.session.commit()

        resp = self.client.get('/worker/attendance')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        now = datetime.now()
        if now.hour >= 18:
            self.assertIn('Absent', html)

    def test_multiple_service_request_otp_verifications_create_distinct_attendance_records(self):
        """Verify that verifying OTP on different service requests creates separate attendance records with customer name, location, and punch in time."""
        self._login()
        with self.app.app_context():
            today = date.today()
            Attendance.query.filter_by(worker_id=self.worker_id, date=today).delete()

            cust = Customer.query.first()
            cust_id = cust.id if cust else self.user.id

            # Create or update 2 distinct service requests for this worker
            sr1 = ServiceRequest.query.filter_by(request_id='SR-2026-000035').first()
            if not sr1:
                sr1 = ServiceRequest(
                    request_id='SR-2026-000035',
                    customer_id=cust_id,
                    customer_name='Ramesh Sharma',
                    mobile_number='9820011111',
                    category='Plumbing',
                    title='Leakage in Master Bathroom',
                    address='Flat 402, Building 3, Gokuldham CHS, Goregaon East, Mumbai',
                    latitude=19.0553,
                    longitude=72.9150,
                    status='Assigned',
                    assigned_worker_id=self.worker_id,
                    contractor_id=1,
                    otp='112233'
                )
                db.session.add(sr1)
            else:
                sr1.customer_id = cust_id
                sr1.customer_name = 'Ramesh Sharma'
                sr1.address = 'Flat 402, Building 3, Gokuldham CHS, Goregaon East, Mumbai'
                sr1.assigned_worker_id = self.worker_id
                sr1.otp = '112233'
                sr1.otp_verified = False

            sr2 = ServiceRequest.query.filter_by(request_id='SR-2026-000036').first()
            if not sr2:
                sr2 = ServiceRequest(
                    request_id='SR-2026-000036',
                    customer_id=cust_id,
                    customer_name='Priya Patel',
                    mobile_number='9820022222',
                    category='Electrical',
                    title='Switchboard Repair in Living Room',
                    address='A-102, Shanti Vihar, Dahisar West, Mumbai',
                    latitude=19.0553,
                    longitude=72.9150,
                    status='Assigned',
                    assigned_worker_id=self.worker_id,
                    contractor_id=1,
                    otp='445566'
                )
                db.session.add(sr2)
            else:
                sr2.customer_id = cust_id
                sr2.customer_name = 'Priya Patel'
                sr2.address = 'A-102, Shanti Vihar, Dahisar West, Mumbai'
                sr2.assigned_worker_id = self.worker_id
                sr2.otp = '445566'
                sr2.otp_verified = False

            db.session.commit()
            sr1_id = sr1.id
            sr2_id = sr2.id

        # 1. Verify OTP for Request 1
        resp1 = self.client.post(
            f'/worker/service-request/{sr1_id}/verify-arrival-otp',
            data={'arrival_otp': '112233', 'worker_lat': 19.0554, 'worker_lng': 72.9150},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp1.status_code, 200)

        # 2. Verify OTP for Request 2
        resp2 = self.client.post(
            f'/worker/service-request/{sr2_id}/verify-arrival-otp',
            data={'arrival_otp': '445566', 'worker_lat': 19.0554, 'worker_lng': 72.9150},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp2.status_code, 200)

        # Verify DB contains 2 distinct attendance records for this worker today
        with self.app.app_context():
            records = Attendance.query.filter_by(worker_id=self.worker_id, date=date.today()).all()
            sr_ids = [r.service_request_id for r in records]
            self.assertIn(sr1_id, sr_ids)
            self.assertIn(sr2_id, sr_ids)
            for r in records:
                self.assertEqual(r.status, 'Present')
                self.assertIsNotNone(r.check_in_time)

        # 3. Verify /worker/attendance page renders both records with Customer Name, Location, Punch In Time, Status
        page_resp = self.client.get('/worker/attendance')
        self.assertEqual(page_resp.status_code, 200)
        html = page_resp.get_data(as_text=True)

        self.assertIn('Ramesh Sharma', html)
        self.assertIn('Flat 402, Building 3, Gokuldham CHS', html)
        self.assertIn('Priya Patel', html)
        self.assertIn('A-102, Shanti Vihar', html)
        self.assertIn('Present', html)
        self.assertIn('Punch In Time', html)
        self.assertIn('Customer Name', html)


if __name__ == '__main__':
    unittest.main()


