import unittest
from datetime import datetime
from app import app, db
from models.user import User
from models.contractor import Contractor
from models.communication import ActivityLog


class TestPublisherSocietiesConsolidation(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            # Create a test publisher super admin
            self.pub_user = User.query.filter_by(email='test_pub_admin@sahakar.coop').first()
            if not self.pub_user:
                self.pub_user = User(
                    username='testpubadmin',
                    email='test_pub_admin@sahakar.coop',
                    role='publisher'
                )
                self.pub_user.set_password('PubSecret123!')
                db.session.add(self.pub_user)
                db.session.commit()

            # Create an active verified society
            self.verified_society = Contractor.query.filter_by(company_name='Test Verified Society PACS').first()
            if not self.verified_society:
                owner = User.query.filter_by(email='verified_society_admin@sahakar.coop').first()
                if not owner:
                    owner = User(
                        username='verifiedsocadmin',
                        email='verified_society_admin@sahakar.coop',
                        role='admin'
                    )
                    owner.set_password('SocAdmin123!')
                    db.session.add(owner)
                    db.session.commit()

                self.verified_society = Contractor(
                    user_id=owner.id,
                    company_name='Test Verified Society PACS',
                    business_type='Multi-Trade',
                    service_areas='Chembur, Kurla',
                    is_verified=True,
                    is_active=True,
                    onboarding_status='approved'
                )
                db.session.add(self.verified_society)
                db.session.commit()

            # Create a pending unverified society
            self.pending_society = Contractor.query.filter_by(company_name='Test Pending Society Union').first()
            if not self.pending_society:
                p_owner = User.query.filter_by(email='pending_society_admin@sahakar.coop').first()
                if not p_owner:
                    p_owner = User(
                        username='pendingsocadmin',
                        email='pending_society_admin@sahakar.coop',
                        role='admin'
                    )
                    p_owner.set_password('PendAdmin123!')
                    db.session.add(p_owner)
                    db.session.commit()

                self.pending_society = Contractor(
                    user_id=p_owner.id,
                    company_name='Test Pending Society Union',
                    business_type='Electrical',
                    service_areas='Thane West',
                    is_verified=False,
                    is_active=True,
                    onboarding_status='pending_approval'
                )
                db.session.add(self.pending_society)
                db.session.commit()

            self.pub_user_id = self.pub_user.id
            self.pending_society_id = self.pending_society.id

    def login_as_publisher(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.pub_user_id)
            sess['_fresh'] = True

    def test_publisher_sidebar_has_exactly_six_canonical_links(self):
        """Test that the Apex Federation sidebar has strictly 6 canonical links and no Worker Approvals."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/dashboard')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # 6 canonical links must be present
        self.assertIn('title="Command Center"', html)
        self.assertIn('title="Primary Societies"', html)
        self.assertIn('title="Customer Disputes & Conciliation"', html)
        self.assertIn('title="State Ledger & Welfare Pool"', html)
        self.assertIn('title="Platform Settings & Security"', html)
        self.assertIn('title="Federation Profile"', html)

        # Mislabeled Worker Approvals must NOT be in the sidebar
        self.assertNotIn('title="Worker Approvals & KYC"', html)

    def test_context_processor_injects_pending_societies_count_badge(self):
        """Test that pending_societies_count is injected and renders as a badge."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/dashboard')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Should render badge with at least 1 pending society
        with self.app.app_context():
            pending_count = Contractor.query.filter_by(is_verified=False).count()
        self.assertGreaterEqual(pending_count, 1)
        self.assertIn('Primary Societies', html)

    def test_publisher_dashboard_preserves_live_audit_activity_feed(self):
        """Test that the real-time Live Audit Activity Feed remains anchored on /publisher/dashboard."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/dashboard')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Live Audit Activity Feed', html)
        self.assertIn('id="liveAuditFeedList"', html)

    def test_societies_page_renders_dual_tabs(self):
        """Test that /publisher/societies renders both Active and Pending tabs."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/societies')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Active Registered Societies', html)
        self.assertIn('Pending Onboarding Queue', html)
        self.assertIn('Test Verified Society PACS', html)
        self.assertIn('Test Pending Society Union', html)

    def test_societies_deep_link_activates_pending_tab(self):
        """Test that /publisher/societies?tab=pending activates Tab 2."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/societies?tab=pending')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('id="tab-pending" role="tabpanel"', html)
        self.assertIn('show active', html)

    def test_approvals_redirects_to_societies_pending_tab(self):
        """Test that legacy /publisher/approvals redirects to /publisher/societies?tab=pending."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/approvals')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('tab=pending', resp.headers['Location'])

    def test_atomic_approve_contractor_logs_activity_and_verifies(self):
        """Test that approving a society updates verification status, logs to ActivityLog, and decrements pending."""
        self.login_as_publisher()
        soc_id = self.pending_society_id

        resp = self.client.post(f'/publisher/onboarding/approve/{soc_id}')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/publisher/societies', resp.headers['Location'])

        with self.app.app_context():
            updated = Contractor.query.get(soc_id)
            self.assertTrue(updated.is_verified)
            self.assertEqual(updated.onboarding_status, 'approved')

            # Verify ActivityLog
            log = ActivityLog.query.filter_by(action='Cooperative Society Approved').order_by(ActivityLog.timestamp.desc()).first()
            self.assertIsNotNone(log)
            self.assertIn(updated.company_name, log.details)

    def test_atomic_reject_contractor_logs_activity_and_decrements_pending(self):
        """Test that rejecting a society updates status to rejected and decrements pending_societies_count."""
        # Setup a fresh pending society for rejection test
        with self.app.app_context():
            rej_user = User.query.filter_by(email='to_be_rejected_soc@sahakar.coop').first()
            if not rej_user:
                rej_user = User(username='toberejecteduser', email='to_be_rejected_soc@sahakar.coop', role='admin')
                rej_user.set_password('Pass123!')
                db.session.add(rej_user)
                db.session.commit()

            test_soc = Contractor.query.filter_by(company_name='Society To Reject PACS').first()
            if not test_soc:
                test_soc = Contractor(
                    user_id=rej_user.id,
                    company_name='Society To Reject PACS',
                    business_type='Plumbing',
                    service_areas='Dadar',
                    is_verified=False,
                    is_active=True,
                    onboarding_status='pending_approval'
                )
                db.session.add(test_soc)
            else:
                test_soc.is_verified = False
                test_soc.onboarding_status = 'pending_approval'
                test_soc.rejection_reason = None
            db.session.commit()
            soc_id = test_soc.id

            initial_pending = Contractor.query.filter(
                Contractor.is_verified == False,
                Contractor.onboarding_status != 'rejected'
            ).count()

        self.login_as_publisher()
        resp = self.client.post(
            f'/publisher/onboarding/reject/{soc_id}',
            data={'rejection_reason': 'Society registration documents verification failed.'},
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            updated = Contractor.query.get(soc_id)
            self.assertFalse(updated.is_verified)
            self.assertEqual(updated.onboarding_status, 'rejected')
            self.assertEqual(updated.rejection_reason, 'Society registration documents verification failed.')

            new_pending = Contractor.query.filter(
                Contractor.is_verified == False,
                Contractor.onboarding_status != 'rejected'
            ).count()
            self.assertEqual(new_pending, initial_pending - 1)

            # Verify ActivityLog
            log = ActivityLog.query.filter_by(action='Cooperative Society Rejected').order_by(ActivityLog.timestamp.desc()).first()
            self.assertIsNotNone(log)
            self.assertIn(updated.company_name, log.details)

        # HTML verification
        html = resp.get_data(as_text=True)
        self.assertIn('Rejected Applications', html)
        self.assertIn('Society To Reject PACS', html)


if __name__ == '__main__':
    unittest.main()
