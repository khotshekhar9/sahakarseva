import unittest
import time
import os
import re
from app import app, db
from models.user import User
from models.service_request import ServiceRequest

class TestCustomerLayoutAndSpacing(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.clean_request_ids = []
        with self.app.app_context():
            anita = User.query.filter(User.username.like('%anita%')).first() or User.query.filter_by(role='customer').first()
            self.customer_id = anita.id

    def tearDown(self):
        with self.app.app_context():
            from models.service_request import ServiceRequest
            from models.quotation import Quotation
            from models.finance import Payment
            for req_id in self.clean_request_ids:
                Quotation.query.filter_by(service_request_id=req_id).delete()
                Payment.query.filter_by(service_request_id=req_id).delete()
                sr = ServiceRequest.query.get(req_id)
                if sr:
                    db.session.delete(sr)
            # Also clean up any TEST-* requests
            test_srs = ServiceRequest.query.filter(ServiceRequest.request_id.like("TEST-%")).all()
            for tsr in test_srs:
                Quotation.query.filter_by(service_request_id=tsr.id).delete()
                Payment.query.filter_by(service_request_id=tsr.id).delete()
                db.session.delete(tsr)
            db.session.commit()

    def test_customer_bookings_duplicate_header_removed(self):
        """
        Verify on /customer/bookings:
        1. Top layout bar renders 'My Bookings' via #header-page-title
        2. Breadcrumb renders 'My Bookings'
        3. Redundant duplicate <h1>My Bookings</h1> is removed from the content body
        4. Subtitle description and 'Book Service' button are retained
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_id)  # Anita Sharma
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            resp = self.client.get('/customer/bookings')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # 1. Header bar contains active section title
            self.assertIn('id="header-page-title"', html)
            self.assertIn('My Bookings', html)

            # 2. Breadcrumb has current page title
            self.assertIn('<span class="bc-current">My Bookings</span>', html)

            # 3. Ensure NO duplicate <h1> tag inside the section head or page content
            self.assertNotIn('<h1>My Bookings</h1>', html)
            self.assertNotIn('<h1 class="h3 fw-bold mb-1">My Bookings</h1>', html)
            # Confirm no other <h1> exists on bookings page (or only 1 if used for screen readers)
            h1_matches = re.findall(r'<h1[^>]*>.*?</h1>', html, re.DOTALL | re.IGNORECASE)
            self.assertEqual(len(h1_matches), 0, f"Expected no duplicate h1 tags on bookings page, found: {h1_matches}")

            # 4. Description and Book Service button remain present
            self.assertIn('Track live technician checkpoints, view quotes, and manage your service requests.', html)
            self.assertIn('Book Service', html)

    def test_customer_dashboard_greeting_heading_structure(self):
        """
        Verify on /customer/dashboard:
        1. Greeting heading renders with class 'greeting-heading'
        2. Greeting contains username and greeting emoji
        3. Top bar and breadcrumb render properly
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_id)  # Anita Sharma
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            resp = self.client.get('/customer/dashboard')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # Greeting heading with class greeting-heading
            self.assertIn('class="greeting-heading"', html)
            self.assertIn('Hi Anita', html)

            # Header bar and breadcrumb
            self.assertIn('Home', html)
            self.assertIn('Dashboard', html)

    def test_css_layout_clearance_and_fab_docking_rules(self):
        """
        Verify CSS files contain required rules for:
        1. Negative margin removal and top clearance (padding-top: 1.5rem)
        2. Hero & greeting heading line-height and anti-clipping
        3. Bottom scroll clearance (padding-bottom: 5.5rem / 5rem)
        4. Floating assistant docked offsets (bottom: 1.5rem, right: 1.5rem, z-index: 1040)
        """
        css_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'css', 'final_polish.css')
        self.assertTrue(os.path.exists(css_path), "final_polish.css must exist")

        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # 1. Top clearance and margin-top: 0
        self.assertIn('.main-content', css_content)
        self.assertIn('margin-top: 0 !important', css_content)
        self.assertIn('padding-top: 1.5rem !important', css_content)

        # 2. Bottom scroll clearance >= 5rem
        self.assertIn('padding-bottom: 5.5rem !important', css_content)
        self.assertIn('padding-bottom: 5rem !important', css_content)

        # 3. Greeting heading anti-clipping
        self.assertIn('.greeting-heading', css_content)
        self.assertIn('line-height: 1.35 !important', css_content)
        self.assertIn('overflow: visible !important', css_content)

        # 4. Service assistant docking
        self.assertIn('.service-assistant-fab', css_content)
        self.assertIn('bottom: 1.5rem !important', css_content)
        self.assertIn('right: 1.5rem !important', css_content)
        self.assertIn('z-index: 1040 !important', css_content)

        # 5. Service assistant panel docking
        self.assertIn('.service-assistant-panel', css_content)
        self.assertIn('bottom: 5.5rem !important', css_content)
        self.assertIn('z-index: 1045 !important', css_content)

    def test_customer_navigation_distinct_active(self):
        """
        Verify:
        1. On /customer/dashboard, 'Home' is active, and 'Help' has href='/customer/help' and is NOT active
        2. 'Home' and 'Help' NEVER glow/activate at the same time
        3. On /customer/help, 'Help' is active and 'Home' is NOT active
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_id)  # Anita Sharma
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            # 1. Check /customer/dashboard
            resp = self.client.get('/customer/dashboard')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # Home should be active
            self.assertIn('sidebar-item active">\n                        <a href="/customer/dashboard" title="Home">', html)
            # Help should NOT be active and should point to /customer/help
            self.assertIn('<a href="/customer/help" title="Help">', html)
            self.assertNotIn('sidebar-item active">\n                        <a href="/customer/help"', html)
            self.assertNotIn('<a href="/customer/dashboard" title="Help">', html)

            # 2. Check /customer/help
            resp_help = self.client.get('/customer/help')
            self.assertEqual(resp_help.status_code, 200)
            help_html = resp_help.get_data(as_text=True)

            # Help should be active on /customer/help
            self.assertIn('sidebar-item active">\n                        <a href="/customer/help" title="Help">', help_html)
            # Home should NOT be active on /customer/help
            self.assertNotIn('sidebar-item active">\n                        <a href="/customer/dashboard" title="Home">', help_html)

            # Help page contents
            self.assertIn('Help & Support', help_html)
            self.assertIn('Quick Common Answers', help_html)
            self.assertIn('Resolution Center', help_html)
            self.assertIn('Raise a Ticket', help_html)
            self.assertIn('My Support Tickets', help_html)

            # Assert duplicate top cards and action buttons are removed
            self.assertNotIn('Open Assistant', help_html)
            self.assertNotIn('Trigger Emergency SOS', help_html)
            self.assertNotIn('COOPERATIVE HELP CENTER', help_html)

            # Assert 4 streamlined FAQ questions exist
            self.assertIn('How does booking work?', help_html)
            self.assertIn('Emergency response time?', help_html)
            self.assertIn('How does fair wage pricing work?', help_html)
            self.assertIn('How to verify the visiting technician?', help_html)

            # Test AJAX ticket creation
            ticket_payload = {
                "title": "Question regarding electrician invoice",
                "description": "Please explain the welfare cess line item on the invoice.",
                "priority": "Normal"
            }
            ticket_resp = self.client.post(
                '/customer/support/ticket',
                json=ticket_payload,
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            self.assertEqual(ticket_resp.status_code, 200)
            t_data = ticket_resp.get_json()
            self.assertEqual(t_data.get('status'), 'success')
            self.assertIsNotNone(t_data.get('ticket', {}).get('id'))

    def test_emergency_modal_and_dispatch(self):
        """
        Verify:
        1. /customer/dashboard contains 'openEmergencyModal()' on the button
        2. #emergencyModal exists in DOM with category options and tariff cards
        3. JavaScript functions 'openEmergencyModal' and 'submitEmergencySOS' exist
        4. Submitting emergency dispatch creates an emergency ticket
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_id)  # Anita Sharma
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            resp = self.client.get('/customer/dashboard')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # 1. Button has onclick="openEmergencyModal()"
            self.assertIn('onclick="openEmergencyModal()"', html)
            # 2. Modal exists in DOM
            self.assertIn('id="emergencyModal"', html)
            self.assertIn('Rapid Emergency SOS Dispatch', html)
            self.assertIn('₹650', html)  # Electrical tariff
            # 3. JavaScript helper functions exist
            self.assertIn('function openEmergencyModal()', html)
            self.assertIn('function submitEmergencySOS(event)', html)

            # 4. Test POST to /customer/emergency-dispatch
            dispatch_payload = {
                "category": "Electrical",
                "title": "Sparking switchboard in kitchen",
                "description": "Smoke coming from main switch, power isolated",
                "address": "Sindhi Society, Chembur Central, Mumbai - 400071",
                "latitude": 19.0560,
                "longitude": 72.8997,
                "radius_km": 5.0
            }
            post_resp = self.client.post(
                '/customer/emergency-dispatch',
                json=dispatch_payload,
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            self.assertEqual(post_resp.status_code, 200)
            data = post_resp.get_json()
            self.assertEqual(data.get('status'), 'success')
            self.assertIn('DISPATCH BROADCAST', data.get('message', ''))
            req_id = data.get('data', {}).get('request_id')
            db_id = data.get('data', {}).get('id')
            self.assertIsNotNone(req_id)
            self.assertIsNotNone(db_id)
            self.clean_request_ids.append(db_id)

            # Confirm record in database is marked as emergency
            with self.app.app_context():
                emg_req = ServiceRequest.query.filter_by(request_id=req_id).first()
                self.assertIsNotNone(emg_req)
                self.assertTrue(emg_req.is_emergency)
                self.assertEqual(emg_req.category, 'Electrical')

    def test_booking_cancellation_lifecycle_guards(self):
        """
        Verify strict lifecycle guards for POST /customer/booking/<id>/cancel:
        1. Allowed for unassigned standard booking in 'Pending' / 'Pending Review'
        2. Blocked if worker is already assigned (protect artisan commitment)
        3. Blocked if quotation is already approved (lock materials & labor)
        4. Blocked if booking is already cancelled or completed
        """
        from models.quotation import Quotation
        import datetime

        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_id)  # Anita Sharma
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            # Case 1: Unassigned Pending booking -> Cancellation Allowed
            with self.app.app_context():
                test_req1 = ServiceRequest(
                    request_id=f"TEST-CANCEL-{int(time.time())}",
                    customer_id=self.customer_id,
                    customer_name="Anita Sharma",
                    mobile_number="9822000000",
                    category="Plumbing",
                    title="Leaking bathroom tap",
                    address="Plot 12, Kamgar Nagar, Kurla East, Mumbai - 400024",
                    status="Pending",
                    assigned_worker_id=None
                )
                db.session.add(test_req1)
                db.session.commit()
                req1_id = test_req1.id
                self.clean_request_ids.append(req1_id)

            cancel_resp = self.client.post(
                f'/customer/booking/{req1_id}/cancel',
                json={"reason": "Fixed it myself"},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            self.assertEqual(cancel_resp.status_code, 200)
            data1 = cancel_resp.get_json()
            self.assertEqual(data1.get('status'), 'success')

            # Confirm state in database
            with self.app.app_context():
                refreshed1 = ServiceRequest.query.get(req1_id)
                self.assertEqual(refreshed1.status, 'Cancelled')

            # Case 2: Attempting to cancel already cancelled booking -> Blocked
            cancel_again_resp = self.client.post(
                f'/customer/booking/{req1_id}/cancel',
                json={"reason": "Cancelled again"},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            self.assertEqual(cancel_again_resp.status_code, 400)

            # Case 3: Booking with assigned worker -> Blocked
            from models.worker import Worker
            with self.app.app_context():
                w = Worker.query.first()
                w_id = w.id if w else 1
                test_req2 = ServiceRequest(
                    request_id=f"TEST-ASSIGNED-{int(time.time())}",
                    customer_id=self.customer_id,
                    customer_name="Anita Sharma",
                    mobile_number="9822000000",
                    category="Electrical",
                    title="Switchboard repair",
                    address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                    status="Scheduled",
                    assigned_worker_id=w_id
                )
                db.session.add(test_req2)
                db.session.commit()
                req2_id = test_req2.id
                self.clean_request_ids.append(req2_id)

            cancel_resp2 = self.client.post(
                f'/customer/booking/{req2_id}/cancel',
                json={"reason": "Want to cancel"},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            self.assertEqual(cancel_resp2.status_code, 400)
            data2 = cancel_resp2.get_json()
            self.assertIn('assigned', data2.get('message', '').lower())

            # Case 4: Booking with approved quotation -> Blocked
            with self.app.app_context():
                test_req3 = ServiceRequest(
                    request_id=f"TEST-QUOTE-{int(time.time())}",
                    customer_id=self.customer_id,
                    customer_name="Anita Sharma",
                    mobile_number="9822000000",
                    category="Carpentry",
                    title="Door hinge replacement",
                    address="Bunglow 14, Sindhi Society, Chembur Central, Mumbai - 400071",
                    status="Pending",
                    assigned_worker_id=None
                )
                db.session.add(test_req3)
                db.session.flush()
                req3_id = test_req3.id
                self.clean_request_ids.append(req3_id)

                quote = Quotation(
                    quotation_number=f"Q-TEST-{test_req3.id}",
                    service_request_id=test_req3.id,
                    grand_total=1200.0,
                    validity_date=datetime.date.today(),
                    status="Approved"
                )
                db.session.add(quote)
                db.session.commit()

            cancel_resp3 = self.client.post(
                f'/customer/booking/{req3_id}/cancel',
                json={"reason": "Cancelling after quote approval"},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            self.assertEqual(cancel_resp3.status_code, 400)
            data3 = cancel_resp3.get_json()
            self.assertIn('approved', data3.get('message', '').lower())

    def test_emergency_banner_controls_and_cancel(self):
        """
        Verify:
        1. Emergency alert banner renders Track Live Status and Cancel Broadcast button
        2. Customer can cancel broadcasting emergency request
        3. Modal and cancel JS handler exist
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_id)
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            # Create broadcasting emergency request
            with self.app.app_context():
                emg_req = ServiceRequest(
                    request_id=f"TEST-EMG-BCAST-{int(time.time())}",
                    customer_id=self.customer_id,
                    customer_name="Anita Sharma",
                    mobile_number="9822000000",
                    category="Plumbing",
                    title="Burst kitchen pipe flooding",
                    address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                    status="Broadcasting",
                    broadcast_status="Broadcasting",
                    is_emergency=True,
                    assigned_worker_id=None
                )
                db.session.add(emg_req)
                db.session.commit()
                emg_id = emg_req.id
                emg_req_id = emg_req.request_id
                self.clean_request_ids.append(emg_id)

            # Check dashboard render
            resp = self.client.get('/customer/dashboard')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn('Track Live Status', html)
            self.assertIn('Cancel Broadcast', html)
            self.assertIn('id="cancelBookingModal"', html)
            self.assertIn('function openCancelBookingModal', html)

            # Check bookings page render
            resp_b = self.client.get('/customer/bookings')
            self.assertEqual(resp_b.status_code, 200)
            b_html = resp_b.get_data(as_text=True)
            self.assertIn('Cancel Request', b_html)

            # Cancel the emergency broadcast
            cancel_resp = self.client.post(
                f'/customer/booking/{emg_id}/cancel',
                json={"reason": "Neighbor turned off the main valve"},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            self.assertEqual(cancel_resp.status_code, 200)
            c_data = cancel_resp.get_json()
            self.assertEqual(c_data.get('status'), 'success')

            # Verify in DB
            with self.app.app_context():
                check_emg = ServiceRequest.query.get(emg_id)
                self.assertEqual(check_emg.status, 'Cancelled')
                self.assertEqual(check_emg.broadcast_status, 'Cancelled')

if __name__ == '__main__':
    unittest.main()

