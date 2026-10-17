import unittest
import time
import uuid
from datetime import datetime, date
from app import app, db
from models.user import User
from models.worker import Worker
from models.worker_features import WorkerCertification
from models.service_request import ServiceRequest

class TestWorkerSkillTiering(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.created_user_ids = []
        self.created_cert_ids = []
        self.created_sr_ids = []
        self._cleanup_test_records()

    def tearDown(self):
        self._cleanup_test_records()

    def _cleanup_test_records(self):
        with self.app.app_context():
            from models.communication import Notification
            from models.finance import Payment
            for sr_id in self.created_sr_ids:
                Payment.query.filter_by(service_request_id=sr_id).delete()
                sr = db.session.get(ServiceRequest, sr_id)
                if sr:
                    db.session.delete(sr)
            for cert_id in self.created_cert_ids:
                c = db.session.get(WorkerCertification, cert_id)
                if c:
                    db.session.delete(c)
            Payment.query.filter(Payment.description.like('%SR-TIER-TEST%')).delete()
            test_srs = ServiceRequest.query.filter(ServiceRequest.request_id.like('SR-TIER-TEST%')).all()
            for sr in test_srs:
                Payment.query.filter_by(service_request_id=sr.id).delete()
                db.session.delete(sr)
            db.session.commit()

            # Find any leftover test users
            test_users = User.query.filter(
                (User.username.like('test_artisan_%')) | (User.email.like('tier_%'))
            ).all()
            for u in test_users:
                Notification.query.filter_by(user_id=u.id).delete()
                WorkerCertification.query.filter_by(worker_id=u.id).delete()
                db.session.delete(u)
            db.session.commit()

    def _login(self, user_id):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_deterministic_tier_rule_engine_evaluation(self):
        """
        Verify evaluate_tier statutory cooperative rule engine:
        - Master Artisan: > 5 yrs experience AND at least 1 verified Govt/NSDC/ITI cert.
        - Skilled Craftsman: 2-5 yrs experience AND at least 1 verified cert (or >5 yrs with non-govt cert).
        - Apprentice: < 2 yrs experience OR 0 verified certs.
        """
        # Mock cert objects
        class MockCert:
            def __init__(self, title, body):
                self.cert_title = title
                self.issuing_body = body

        nsdc_cert = MockCert("NSDC Level 4 Master Wireman", "National Skill Development Corporation")
        iti_cert = MockCert("ITI Electrician Grade A", "State Council for Vocational Training")
        trade_cert = MockCert("Advanced Pipe Jointing", "Plumbing Trade Guild")

        # Case 1: 6 yrs experience, 0 verified certs -> Apprentice
        self.assertEqual(Worker.evaluate_tier(6, []), 'Apprentice')
        self.assertEqual(Worker.evaluate_tier(6, 0), 'Apprentice')

        # Case 2: 1.5 yrs experience, 1 NSDC cert -> Apprentice (< 2 yrs)
        self.assertEqual(Worker.evaluate_tier(1.5, [nsdc_cert]), 'Apprentice')

        # Case 3: 3 yrs experience, 1 trade cert -> Skilled Craftsman
        self.assertEqual(Worker.evaluate_tier(3, [trade_cert]), 'Skilled Craftsman')

        # Case 4: 6 yrs experience, 1 trade cert (non-Govt/NSDC) -> Skilled Craftsman
        self.assertEqual(Worker.evaluate_tier(6, [trade_cert]), 'Skilled Craftsman')

        # Case 5: 6 yrs experience, 1 NSDC cert -> Master Artisan (> 5 yrs & Govt/NSDC)
        self.assertEqual(Worker.evaluate_tier(6, [nsdc_cert]), 'Master Artisan')

        # Case 6: 7 yrs experience, 1 ITI cert -> Master Artisan
        self.assertEqual(Worker.evaluate_tier(7, [iti_cert]), 'Master Artisan')

    def test_default_tier_initialization(self):
        """
        Worker with 6 years experience and 0 verified certs initializes with default tier Apprentice.
        """
        tag = uuid.uuid4().hex[:6]
        with self.app.app_context():
            test_user = User(
                username=f"test_artisan_{tag}",
                email=f"tier_{tag}@example.com",
                role="worker"
            )
            test_user.set_password("Secret123!")
            db.session.add(test_user)
            db.session.flush()
            self.created_user_ids.append(test_user.id)

            worker = Worker(
                id=test_user.id,
                experience_years=6,
                contractor_id=1,
                availability_status='available',
                is_verified=True
            )
            db.session.add(worker)
            db.session.commit()

            # Confirm default tier is Apprentice
            self.assertEqual(worker.tier, 'Apprentice')

            # refresh_tier with 0 certs maintains Apprentice
            refreshed = worker.refresh_tier()
            self.assertEqual(refreshed, 'Apprentice')

    def test_admin_approves_nsdc_cert_promotes_to_master_artisan(self):
        """
        Admin approves an NSDC certificate for a worker with 6 years experience:
        worker.tier transitions atomically to Master Artisan.
        """
        tag = uuid.uuid4().hex[:6]
        with self.app.app_context():
            test_user = User(
                username=f"test_artisan_{tag}",
                email=f"tier_{tag}@example.com",
                role="worker"
            )
            test_user.set_password("Secret123!")
            db.session.add(test_user)
            db.session.flush()
            self.created_user_ids.append(test_user.id)

            worker = Worker(
                id=test_user.id,
                experience_years=6,
                contractor_id=1,
                tier='Apprentice',
                availability_status='available',
                is_verified=True
            )
            db.session.add(worker)
            db.session.flush()

            cert = WorkerCertification(
                worker_id=worker.id,
                cert_title="NSDC Level 4 Master Wireman",
                issuing_body="National Skill Development Corporation (Skill India)",
                cert_number=f"NSDC-TEST-{tag}",
                status="Pending"
            )
            db.session.add(cert)
            db.session.commit()
            self.created_cert_ids.append(cert.id)

            cert_id = cert.id
            worker_id = worker.id

        # Log in as Admin (User ID 2 is contractor admin)
        self._login(2)

        # Admin approves certificate
        res = self.client.post(
            f"/admin/certification/verify/{cert_id}",
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            w = db.session.get(Worker, worker_id)
            c = db.session.get(WorkerCertification, cert_id)
            self.assertEqual(c.status, 'Verified')
            self.assertEqual(w.tier, 'Master Artisan')

    def test_admin_approves_general_trade_cert_promotes_to_skilled_craftsman(self):
        """
        Admin approves a general trade certificate for a worker with 3 years experience:
        worker.tier transitions to Skilled Craftsman.
        """
        tag = uuid.uuid4().hex[:6]
        with self.app.app_context():
            test_user = User(
                username=f"test_artisan_{tag}",
                email=f"tier_{tag}@example.com",
                role="worker"
            )
            test_user.set_password("Secret123!")
            db.session.add(test_user)
            db.session.flush()
            self.created_user_ids.append(test_user.id)

            worker = Worker(
                id=test_user.id,
                experience_years=3,
                contractor_id=1,
                tier='Apprentice',
                availability_status='available',
                is_verified=True
            )
            db.session.add(worker)
            db.session.flush()

            cert = WorkerCertification(
                worker_id=worker.id,
                cert_title="Certified Plumbing Technician",
                issuing_body="Builders Guild Association",
                cert_number=f"BGA-PLB-{tag}",
                status="Pending"
            )
            db.session.add(cert)
            db.session.commit()
            self.created_cert_ids.append(cert.id)

            cert_id = cert.id
            worker_id = worker.id

        # Log in as Admin
        self._login(2)

        # Approve certificate via alias route
        res = self.client.post(
            f"/admin/certification/approve/{cert_id}",
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            w = db.session.get(Worker, worker_id)
            c = db.session.get(WorkerCertification, cert_id)
            self.assertEqual(c.status, 'Verified')
            self.assertEqual(w.tier, 'Skilled Craftsman')

    def test_customer_tracking_view_reflects_upgraded_badge(self):
        """
        Verify that customer booking tracking view reflects the artisan's tier badge
        (e.g., Master Artisan with bg-purple-subtle) immediately upon refresh.
        """
        with self.app.app_context():
            # Worker 3 (John Doe) is Master Artisan in seed data
            sr = ServiceRequest(
                request_id="SR-TIER-TEST-01",
                customer_id=11,  # Anita Sharma
                customer_name="Anita Sharma",
                mobile_number="+91-9820011223",
                address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                assigned_worker_id=3,  # John Doe
                contractor_id=1,
                category="Electrician",
                title="Master Artisan Badging Verification",
                description="Short circuit check",
                status="Assigned",
                estimated_cost=450.0,
                visit_date=date.today(),
                preferred_time="11:00 AM",
                created_at=datetime.utcnow()
            )
            db.session.add(sr)
            db.session.commit()
            self.created_sr_ids.append(sr.id)
            sr_id = sr.id

        # Log in as customer
        self._login(11)

        res = self.client.get(f"/customer/booking/{sr_id}/details")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # Check for Master Artisan badge and styling
        self.assertIn("Master Artisan", html)
        self.assertIn("bg-purple-subtle", html)
        self.assertIn("text-purple", html)
        self.assertIn("fa-crown", html)

    def test_worker_profile_and_benefits_badge_and_progress_indicator(self):
        """
        Verify worker profile and benefits templates render tier badge and 1-line progress indicator.
        """
        # Ensure Worker 3 (John Doe) has Master Artisan tier for this verification
        with self.app.app_context():
            w = db.session.get(Worker, 3)
            if w:
                w.tier = 'Master Artisan'
                db.session.commit()

        # Log in as Worker 3 (John Doe, Master Artisan)
        self._login(3)

        # Test profile page
        res_profile = self.client.get("/worker/profile")
        self.assertEqual(res_profile.status_code, 200)
        html_prof = res_profile.get_data(as_text=True)
        self.assertIn("Master Artisan", html_prof)
        self.assertIn("bg-purple-subtle", html_prof)
        self.assertIn("Next Tier:", html_prof)

        # Test benefits page
        res_benefits = self.client.get("/worker/benefits")
        self.assertEqual(res_benefits.status_code, 200)
        html_ben = res_benefits.get_data(as_text=True)
        self.assertIn("Master Artisan", html_ben)
        self.assertIn("bg-purple-subtle", html_ben)
        self.assertIn("Next Tier:", html_ben)

if __name__ == '__main__':
    unittest.main()
