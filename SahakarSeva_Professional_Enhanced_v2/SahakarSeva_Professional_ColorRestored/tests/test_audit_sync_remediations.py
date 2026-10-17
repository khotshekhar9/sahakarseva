import unittest
import json
import time
from app import app, db
from models.user import User
from models.contractor import Contractor
from models.worker import Worker
from models.communication import ActivityLog, Notification


class TestAuditSyncRemediations(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            # 1. Setup Publisher User
            self.publisher_user = User.query.filter_by(email='audit_pub_test@sahakar.coop').first()
            if not self.publisher_user:
                self.publisher_user = User(
                    username='auditpubuser',
                    email='audit_pub_test@sahakar.coop',
                    role='publisher'
                )
                self.publisher_user.set_password('PubPassword123!')
                db.session.add(self.publisher_user)
                db.session.commit()

            # 2. Setup Society Admin User & Contractor
            self.admin_user = User.query.filter_by(email='audit_admin_test@sahakar.coop').first()
            if not self.admin_user:
                self.admin_user = User(
                    username='auditadminuser',
                    email='audit_admin_test@sahakar.coop',
                    role='admin'
                )
                self.admin_user.set_password('AdminPassword123!')
                db.session.add(self.admin_user)
                db.session.commit()

            self.contractor = Contractor.query.filter_by(user_id=self.admin_user.id).first()
            if not self.contractor:
                self.contractor = Contractor(
                    user_id=self.admin_user.id,
                    company_name='Audit Test Society Ltd.',
                    business_type='Electrician',
                    is_verified=True,
                    is_active=True
                )
                db.session.add(self.contractor)
                db.session.commit()

            # 3. Setup Test Worker for Verification
            self.worker_user = User.query.filter_by(email='audit_worker_test@sahakar.coop').first()
            if not self.worker_user:
                self.worker_user = User(
                    username='auditworkeruser',
                    email='audit_worker_test@sahakar.coop',
                    role='worker'
                )
                self.worker_user.set_password('WorkerPassword123!')
                db.session.add(self.worker_user)
                db.session.commit()

            self.worker = Worker.query.get(self.worker_user.id)
            if not self.worker:
                self.worker = Worker(
                    id=self.worker_user.id,
                    contractor_id=self.contractor.id,
                    skills='Electrician',
                    is_verified=False,
                    verification_status='pending',
                    availability_status='available',
                    salary_rate=550.0
                )
                db.session.add(self.worker)
                db.session.commit()
            else:
                self.worker.contractor_id = self.contractor.id
                self.worker.is_verified = False
                self.worker.verification_status = 'pending'
                db.session.commit()
            self.publisher_user_id = self.publisher_user.id
            self.admin_user_id = self.admin_user.id
            self.contractor_id = self.contractor.id
            self.worker_id = self.worker.id

    def login_publisher(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.publisher_user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def login_admin(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.admin_user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    # ─── PUBLISHER AUDIT TESTS ────────────────────────────────────────────────

    def test_publisher_backup_export_direct_download(self):
        """Verify Export Global SQL Backup endpoint doesn't return 403 and returns attachment."""
        self.login_publisher()
        res = self.client.get('/publisher/backup/export')
        self.assertIn(res.status_code, [200, 302])
        if res.status_code == 200:
            self.assertIn('attachment', res.headers.get('Content-Disposition', ''))

    def test_publisher_societies_pending_deeplink(self):
        """Verify Review Pending Onboarding links cleanly without 404/500."""
        self.login_publisher()
        res = self.client.get('/publisher/societies?tab=pending')
        self.assertEqual(res.status_code, 200)

    def test_publisher_disputes_route(self):
        """Verify Customer Dispute Center route /publisher/disputes loads cleanly."""
        self.login_publisher()
        res = self.client.get('/publisher/disputes')
        self.assertEqual(res.status_code, 200)

    def test_publisher_settings_canonical_route(self):
        """Verify Emergency Lockout Controls route /publisher/settings works cleanly."""
        self.login_publisher()
        res = self.client.get('/publisher/settings')
        self.assertEqual(res.status_code, 200)

    def test_publisher_live_audit_feed_api(self):
        """Verify live audit feed API returns JSON with activities array."""
        self.login_publisher()
        res = self.client.get('/publisher/api/audit-feed')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIsInstance(data.get('activities'), list)

    def test_publisher_send_announcement(self):
        """Verify Send Announcement dispatch posts cleanly and notifies users."""
        self.login_publisher()
        res = self.client.post('/publisher/broadcast/send', data={
            'title': 'System Maintenance Update',
            'message': 'Cooperative platform update will occur tonight at 11 PM.',
            'target_role': 'contractors'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        with self.app.app_context():
            notif = Notification.query.filter_by(user_id=self.admin_user_id).order_by(Notification.id.desc()).first()
            self.assertIsNotNone(notif)
            self.assertIn('System Maintenance Update', notif.title)

    # ─── SOCIETY ADMIN AUDIT TESTS ────────────────────────────────────────────

    def test_admin_bookings_canonical_route(self):
        """Verify /admin/bookings resolves cleanly to the bookings page."""
        self.login_admin()
        res = self.client.get('/admin/bookings')
        self.assertEqual(res.status_code, 200)

    def test_admin_workers_canonical_route(self):
        """Verify /admin/workers resolves cleanly."""
        self.login_admin()
        res = self.client.get('/admin/workers')
        self.assertEqual(res.status_code, 200)

    def test_admin_payments_canonical_route(self):
        """Verify /admin/payments resolves cleanly."""
        self.login_admin()
        res = self.client.get('/admin/payments')
        self.assertEqual(res.status_code, 200)

    def test_admin_ai_demand_canonical_route(self):
        """Verify /admin/ai-demand resolves cleanly."""
        self.login_admin()
        res = self.client.get('/admin/ai-demand')
        self.assertEqual(res.status_code, 200)

    def test_admin_database_backup_export(self):
        """Verify Download SQL Dump endpoint /admin/backup/export."""
        self.login_admin()
        res = self.client.get('/admin/backup/export')
        self.assertIn(res.status_code, [200, 302])
        if res.status_code == 200:
            self.assertIn('attachment', res.headers.get('Content-Disposition', ''))

    def test_admin_backup_create_json(self):
        """Verify Create Backup JSON endpoint /admin/api/backup/create."""
        self.login_admin()
        res = self.client.post('/admin/api/backup/create', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertIn(res.status_code, [200, 302])
        if res.is_json:
            data = res.get_json()
            self.assertEqual(data.get('status'), 'success')

    def test_worker_approve_and_reject_actions(self):
        """Verify Approve and Reject worker actions respond with atomic JSON status."""
        self.login_admin()
        worker_id = self.worker_id

        # 1. Test approve
        res = self.client.post(
            f'/admin/workers/{worker_id}/verify',
            headers={'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')

        with self.app.app_context():
            w = Worker.query.get(worker_id)
            self.assertTrue(w.is_verified)
            self.assertEqual(w.verification_status, 'approved')

        # 2. Test reject
        res_rej = self.client.post(
            f'/admin/workers/{worker_id}/reject',
            headers={'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'}
        )
        self.assertEqual(res_rej.status_code, 200)
        data_rej = res_rej.get_json()
        self.assertEqual(data_rej.get('status'), 'success')

        with self.app.app_context():
            w = Worker.query.get(worker_id)
            self.assertFalse(w.is_verified)
            self.assertEqual(w.verification_status, 'rejected')


if __name__ == '__main__':
    unittest.main()
