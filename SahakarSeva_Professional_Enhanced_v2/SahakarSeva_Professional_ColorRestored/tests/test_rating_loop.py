import unittest
import time
import json
import re
from app import app, db
from models.user import User
from models.customer import Customer
from models.worker import Worker
from models.contractor import Contractor, ContractorReview
from models.service_request import ServiceRequest

class TestUnifiedRatingAndFeedbackLoop(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.clean_request_ids = []
        self.clean_review_ids = []
        with self.app.app_context():
            anita = User.query.filter(User.username.like('%anita%')).first() or User.query.filter_by(role='customer').first()
            self.customer_id = anita.id
            other_c = User.query.filter(User.role == 'customer', User.id != self.customer_id).first()
            self.other_customer_id = other_c.id if other_c else self.customer_id + 1
            w = Worker.query.first()
            self.worker_id = w.id
            w2 = Worker.query.filter(Worker.id != self.worker_id).first() or w
            self.worker_id2 = w2.id

    def tearDown(self):
        with self.app.app_context():
            for rev_id in self.clean_review_ids:
                rev = db.session.get(ContractorReview, rev_id)
                if rev:
                    db.session.delete(rev)

            from models.finance import Payment
            for req_id in self.clean_request_ids:
                ContractorReview.query.filter_by(service_request_id=req_id).delete()
                Payment.query.filter_by(service_request_id=req_id).delete()
                sr = db.session.get(ServiceRequest, req_id)
                if sr:
                    db.session.delete(sr)
            db.session.commit()

    def _login_customer(self, customer_id=None):
        cid = customer_id if customer_id is not None else self.customer_id
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(cid)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_ajax_review_submission_atomic_updates(self):
        """Verify submitting a review atomically populates ServiceRequest, Worker, and Contractor."""
        with self.app.app_context():
            ts = int(time.time() * 1000) % 1000000
            worker = db.session.get(Worker, self.worker_id)
            self.assertIsNotNone(worker)

            # Create completed service request
            sr = ServiceRequest(
                request_id=f"SR-RATE-{ts:06d}",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="9822012345",
                category="Electrical",
                title="Ceiling Fan Repair",
                address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                status="Completed",
                contractor_id=1,
                assigned_worker_id=self.worker_id
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.clean_request_ids.append(sr_id)

        self._login_customer()

        # Submit 4-star review via JSON
        res = self.client.post(
            '/customer/review/submit',
            data=json.dumps({
                'service_request_id': sr_id,
                'rating': 4,
                'review_text': 'Punctual, polite, and very skilled electrician.'
            }),
            content_type='application/json',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('Thank you! Review submitted.', data.get('message'))
        self.assertEqual(data.get('rating'), 4)

        # Verify atomic database updates
        with self.app.app_context():
            updated_sr = db.session.get(ServiceRequest, sr_id)
            self.assertEqual(updated_sr.rating, 4)
            self.assertEqual(updated_sr.review_comment, 'Punctual, polite, and very skilled electrician.')

            # Verify ContractorReview created & contractor average recalculated
            rev = ContractorReview.query.filter_by(service_request_id=sr_id).first()
            self.assertIsNotNone(rev)
            self.clean_review_ids.append(rev.id)
            self.assertEqual(rev.rating, 4)

            contractor = db.session.get(Contractor, 1)
            self.assertGreater(contractor.average_rating, 0.0)

            # Verify Worker.performance_rating was recalculated
            updated_worker = db.session.get(Worker, self.worker_id)
            self.assertIsNotNone(updated_worker.performance_rating)

    def test_review_status_guard_rejects_in_progress(self):
        """Verify reviews cannot be submitted for non-completed/non-paid jobs."""
        with self.app.app_context():
            ts = int(time.time() * 1000) % 1000000
            sr = ServiceRequest(
                request_id=f"SR-PROG-{ts:06d}",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="9822012345",
                category="Plumbing",
                title="Pipe Repair",
                address="Plot 12, Kamgar Nagar, Kurla East, Mumbai - 400024",
                status="In Progress",
                contractor_id=1,
                assigned_worker_id=self.worker_id
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.clean_request_ids.append(sr_id)

        self._login_customer()

        res = self.client.post(
            '/customer/review/submit',
            data=json.dumps({
                'service_request_id': sr_id,
                'rating': 5,
                'review_text': 'Good job so far'
            }),
            content_type='application/json',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'error')
        self.assertIn('completed or paid', data.get('message').lower())

        with self.app.app_context():
            check_sr = db.session.get(ServiceRequest, sr_id)
            self.assertIsNone(check_sr.rating)

    def test_review_authorization_guard(self):
        """Verify customer cannot submit a review for another customer's booking."""
        with self.app.app_context():
            ts = int(time.time() * 1000) % 1000000
            # Belongs to other customer
            sr = ServiceRequest(
                request_id=f"SR-OTHER-{ts:06d}",
                customer_id=self.other_customer_id,
                customer_name="Rahul Verma",
                mobile_number="9822099999",
                category="Carpentry",
                title="Chair Repair",
                address="Bunglow 14, Sindhi Society, Chembur Central, Mumbai - 400071",
                status="Completed",
                contractor_id=1,
                assigned_worker_id=self.worker_id
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.clean_request_ids.append(sr_id)

        # Logged in as Anita
        self._login_customer()

        res = self.client.post(
            '/customer/review/submit',
            data=json.dumps({
                'service_request_id': sr_id,
                'rating': 5,
                'review_text': 'Unauthorized attempt'
            }),
            content_type='application/json',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(res.status_code, 403)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'error')

    def test_form_post_redirect_and_flash(self):
        """Verify standard form POST redirects with flash message."""
        with self.app.app_context():
            ts = int(time.time() * 1000) % 1000000
            sr = ServiceRequest(
                request_id=f"SR-FORM-{ts:06d}",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="9822012345",
                category="Cleaning",
                title="Deep House Cleaning",
                address="Clubhouse Office, Deonar Heights CHS, P.L. Lokhande Marg, Govandi East, Mumbai - 400088",
                status="Paid",
                contractor_id=1,
                assigned_worker_id=self.worker_id
            )
            db.session.add(sr)
            db.session.commit()
            sr_id = sr.id
            self.clean_request_ids.append(sr_id)

        self._login_customer()

        res = self.client.post(
            '/customer/review/submit',
            data={
                'service_request_id': sr_id,
                'rating': '5',
                'review_text': 'Spotless and fast service!'
            },
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Thank you! Review submitted.', res.data)

        with self.app.app_context():
            updated_sr = db.session.get(ServiceRequest, sr_id)
            self.assertEqual(updated_sr.rating, 5)

    def test_multi_job_worker_rating_aggregation(self):
        """Verify Worker.performance_rating computes exact cumulative average across completed/paid requests."""
        with self.app.app_context():
            ts = int(time.time() * 1000) % 1000000

            # Create 2 completed jobs with ratings 4 and 2
            sr1 = ServiceRequest(
                request_id=f"SR-AGG1-{ts:06d}",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="9822012345",
                category="Plumbing",
                title="Sink Leak",
                address="Plot 12, Kamgar Nagar, Kurla East, Mumbai - 400024",
                status="Completed",
                contractor_id=1,
                assigned_worker_id=self.worker_id2,
                rating=4
            )
            sr2 = ServiceRequest(
                request_id=f"SR-AGG2-{ts:06d}",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="9822012345",
                category="Plumbing",
                title="Tap Replacement",
                address="Plot 12, Kamgar Nagar, Kurla East, Mumbai - 400024",
                status="Completed",
                contractor_id=1,
                assigned_worker_id=self.worker_id2,
                rating=None  # will be submitted via review route
            )
            db.session.add_all([sr1, sr2])
            db.session.commit()
            self.clean_request_ids.extend([sr1.id, sr2.id])
            sr2_id = sr2.id

        self._login_customer()

        # Submit rating of 2 on the second job
        res = self.client.post(
            '/customer/review/submit',
            data=json.dumps({
                'service_request_id': sr2_id,
                'rating': 2,
                'review_text': 'A bit delayed.'
            }),
            content_type='application/json',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            worker = db.session.get(Worker, self.worker_id2)
            # Cumulative average of 4 and 2 = 3.00
            self.assertEqual(float(worker.performance_rating), 3.0)

    def test_ui_modal_rendering_and_word_count(self):
        """Verify modal is rendered in HTML with under 25 words of copy."""
        with self.app.app_context():
            ts = int(time.time() * 1000) % 1000000
            sr = ServiceRequest(
                request_id=f"SR-UI-{ts:06d}",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="9822012345",
                category="Electrical",
                title="Lighting Fix",
                address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                status="Completed",
                contractor_id=1,
                assigned_worker_id=self.worker_id,
                rating=None
            )
            db.session.add(sr)
            db.session.commit()
            self.clean_request_ids.append(sr.id)

        self._login_customer()

        res = self.client.get('/customer/bookings')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # Check Rate Service button exists for unrated completed booking
        self.assertIn(f'data-booking-id="{sr.id}"', html)
        self.assertIn('Rate Service', html)

        # Check review modal exists
        self.assertIn('id="reviewModal"', html)

        # Check modal title & subheadline
        self.assertIn('Rate Your Service', html)
        self.assertIn('How was your experience with', html)
        self.assertIn('id="reviewModalWorkerName"', html)

        # Check star group and 5 star items
        self.assertIn('id="starRatingGroup"', html)
        star_matches = re.findall(r'class="[^"]*star-item[^"]*"', html)
        self.assertGreaterEqual(len(star_matches), 5)

        # Extract modal body content to check word count
        modal_match = re.search(r'<div class="modal fade" id="reviewModal".*?</div>\s*</div>\s*</div>\s*</div>', html, re.DOTALL)
        self.assertIsNotNone(modal_match)
        modal_html = modal_match.group(0)

        # Strip HTML tags
        text_only = re.sub(r'<[^>]+>', ' ', modal_html)
        words = [w for w in text_only.split() if w]
        # Verify under 25 words
        self.assertLess(len(words), 25, f"Modal contains {len(words)} words, expected < 25: {words}")

if __name__ == '__main__':
    unittest.main()
