import time
import unittest
from app import app, db
from models.user import User
from models.customer import Customer
from models.contractor import Contractor
from models.communication import SupportTicket, Notification, ActivityLog
from models.finance import Payment, WelfareTransaction


class TestPublisherMoneyAndDisputes(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            # 1. Setup Publisher user
            self.pub_user = User.query.filter_by(email='test_pub_super@sahakar.coop').first()
            if not self.pub_user:
                self.pub_user = User(
                    username='testpubsuper',
                    email='test_pub_super@sahakar.coop',
                    role='publisher'
                )
                self.pub_user.set_password('PubSecret123!')
                db.session.add(self.pub_user)
                db.session.commit()

            # 2. Setup Contractor Society
            self.contractor = Contractor.query.filter_by(company_name='Test Apex Linked Society PACS').first()
            if not self.contractor:
                con_owner = User.query.filter_by(email='test_con_owner@sahakar.coop').first()
                if not con_owner:
                    con_owner = User(
                        username='testconowner',
                        email='test_con_owner@sahakar.coop',
                        role='admin'
                    )
                    con_owner.set_password('ConSecret123!')
                    db.session.add(con_owner)
                    db.session.commit()

                self.contractor = Contractor(
                    user_id=con_owner.id,
                    company_name='Test Apex Linked Society PACS',
                    contact_phone='9820112233',
                    business_type='Multi-Trade',
                    service_areas='Chembur Central',
                    is_verified=True,
                    is_active=True,
                    onboarding_status='approved'
                )
                db.session.add(self.contractor)
                db.session.commit()

            # 3. Setup Customer user
            self.cust_user = User.query.filter_by(email='test_complaint_citizen@sahakar.coop').first()
            if not self.cust_user:
                self.cust_user = User(
                    username='testcitizen1',
                    email='test_complaint_citizen@sahakar.coop',
                    role='customer'
                )
                self.cust_user.set_password('Citizen123!')
                db.session.add(self.cust_user)
                db.session.commit()

            self.cust_user.name = 'Rani Deshmukh'
            self.cust_user.phone = '9820011223'
            db.session.commit()

            self.customer = Customer.query.get(self.cust_user.id)
            if not self.customer:
                self.customer = Customer(
                    id=self.cust_user.id,
                    billing_address='Flat 402, Sai Heights, Chembur'
                )
                db.session.add(self.customer)
                db.session.commit()

            self.pub_user_id = self.pub_user.id
            self.cust_user_id = self.cust_user.id
            self.contractor_id = self.contractor.id
            self.customer_id = self.customer.id

    def login_as_publisher(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.pub_user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def login_as_customer(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.cust_user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_publisher_money_page_renders_simplified_revenue_and_no_bloat(self):
        """Test that /publisher/money renders the simplified Money & Welfare page with 4 top cards and society revenue table."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/money')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Header & Navigation Structure
        self.assertIn('Money & Welfare', html)
        self.assertIn('Overview of platform revenue, society earnings, and worker welfare funds.', html)
        self.assertIn('Platform & Society Revenue', html)
        self.assertIn('Worker Welfare Fund (Suraksha Nidhi)', html)

        # 4 Simple Top Cards
        self.assertIn('Total Bookings Value', html)
        self.assertIn('Artisan Direct Wages (88%)', html)
        self.assertIn('Primary Societies Share (8%)', html)
        self.assertIn('Total Settled Jobs', html)

        # Simple Society Revenue Table
        self.assertIn('Society Revenue', html)
        self.assertIn('Society Name', html)
        self.assertIn('Completed Jobs', html)
        self.assertIn('Total Value (₹)', html)
        self.assertIn('Artisan Payout (88%)', html)
        self.assertIn('Society Cut (8%)', html)
        self.assertIn('Status', html)

        # Bloated comparison charts and dense text blocks must be removed
        self.assertNotIn('Cooperative Dividend vs Commercial Aggregators', html)
        self.assertNotIn('Cooperative subscription payments and revenue', html)
        self.assertNotIn('No subscription payments found', html)

    def test_publisher_money_page_welfare_tab_renders_metrics_and_clean_log(self):
        """Test that /publisher/money?tab=welfare displays 3 clear metrics cards and clean welfare log table without dense protocol text."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/money?tab=welfare')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # 3 Clear Metrics Cards
        self.assertIn('Welfare Pool Balance (4%)', html)
        self.assertIn('Active Insurance Policies', html)
        self.assertIn('Claims Paid Out', html)

        # Simple Welfare Log Table
        self.assertIn('Welfare Log', html)
        self.assertIn('Worker Name', html)
        self.assertIn('Trade', html)
        self.assertIn('Contribution / Debit (₹)', html)
        self.assertIn('Reason / Scheme', html)
        self.assertIn('Date', html)

        # Dense protocol text block must be removed
        self.assertNotIn('Automated Micro-Cess Protocol', html)
        self.assertNotIn('Automated Micro-Cess & Social Security Protocol', html)

    def test_publisher_complaints_page_renders_simplified_desk(self):
        """Test that /publisher/complaints renders the simplified Customer Complaints desk."""
        self.login_as_publisher()
        resp = self.client.get('/publisher/complaints')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Simplified Header
        self.assertIn('Customer Complaints', html)
        self.assertIn('Review and resolve escalated customer grievances against local societies.', html)

        # 3 Minimal Top Cards
        self.assertIn('Total Complaints', html)
        self.assertIn('Pending Review', html)
        self.assertIn('Resolved', html)

        # Deleted protocol text card
        self.assertNotIn('Apex Federation Statutory Conciliation Protocol', html)

        # Streamlined Complaints Table
        self.assertIn('Complaint ID & Date', html)
        self.assertIn('Customer', html)
        self.assertIn('Society Involved', html)
        self.assertIn('Issue / Problem', html)
        self.assertIn('Status', html)
        self.assertIn('Action', html)
        self.assertIn('Resolve Complaint', html)

    def test_customer_escalates_to_apex_and_appears_on_concierge_desk(self):
        """Test customer escalation flow end-to-end to Apex conciliation desk."""
        self.login_as_customer()

        # Submit ticket with escalation_level='apex'
        payload = {
            'title': 'Emergency Plumbing Leak Unresolved with Extra Surcharge',
            'description': 'Pipe repair was charged extra in cash and valve leaked again. Requesting Apex Council statutory refund and conciliation.',
            'priority': 'Emergency',
            'escalation_level': 'apex'
        }

        # Clean up any stale records from prior test runs
        with self.app.app_context():
            SupportTicket.query.filter_by(title=payload['title']).delete()
            db.session.commit()

        resp = self.client.post('/customer/support/ticket', data=payload, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Verify database record state
        with self.app.app_context():
            st = SupportTicket.query.filter_by(title=payload['title']).first()
            self.assertIsNotNone(st)
            self.assertEqual(st.target_tier, 'apex')
            self.assertEqual(st.escalation_level, 'apex')
            self.assertTrue(st.is_apex_dispute)

        # Check that Apex Concierge desk renders this complaint
        self.login_as_publisher()
        p_resp = self.client.get('/publisher/complaints')
        self.assertEqual(p_resp.status_code, 200)
        p_html = p_resp.get_data(as_text=True)
        self.assertIn('Emergency Plumbing Leak Unresolved with Extra Surcharge', p_html)
        self.assertIn(self.cust_user.username, p_html)

    def test_publisher_arbitrates_dispute_resolution(self):
        """Test Apex Super Admin arbitrates a dispute and issues resolution."""
        # Create an escalated grievance in DB
        with self.app.app_context():
            st = SupportTicket(
                customer_id=self.customer_id,
                title='Electrical Panel Sparking Dispute',
                description='Customer disputes additional billing for circuit inspection.',
                priority='High',
                status='Escalated',
                target_tier='apex',
                escalation_level='apex',
                is_apex_dispute=True,
                contractor_id=self.contractor_id
            )
            db.session.add(st)
            db.session.commit()
            test_st_id = st.id

        self.login_as_publisher()

        # 1. Arbitrate: Resolve in Citizen Favor
        arb_payload = {
            'action': 'resolve_customer',
            'publisher_notes': 'Full restitution approved under SahakarSeva statutory guarantee.'
        }
        arb_resp = self.client.post(f'/publisher/disputes/{test_st_id}/arbitrate', data=arb_payload, follow_redirects=True)
        self.assertEqual(arb_resp.status_code, 200)

        with self.app.app_context():
            updated_st = SupportTicket.query.get(test_st_id)
            self.assertEqual(updated_st.status, 'Resolved')
            self.assertIn('Resolved in Customer Favor', updated_st.arbitration_action)

            # Verify notification was sent
            notif = Notification.query.filter(Notification.message.like('%Electrical Panel Sparking Dispute%')).first()
            if not notif:
                notif = Notification.query.filter(Notification.title.like('%Apex Conciliation%')).first()
            self.assertIsNotNone(notif)

            # Verify activity was logged
            log = ActivityLog.query.filter(ActivityLog.action.like('%Apex Conciliation%')).first()
            self.assertIsNotNone(log)


if __name__ == '__main__':
    unittest.main()
