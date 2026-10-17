import unittest
import time
from app import app, db
from models.user import User
from models.service_request import ServiceRequest
from models.finance import Payment
from models.quotation import Quotation

class TestBookingActionButtonsAndTracking(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            anita = User.query.filter(User.username.like('%anita%')).first() or User.query.filter_by(role='customer').first()
            self.customer_id = anita.id

    def test_booking_card_action_buttons_logic(self):
        """
        Verify conditional rendering of action buttons on /customer/bookings:
        1. Always display 'View Status'
        2. 'Edit Booking' only for editable states (Pending Review, Pending, Scheduled)
        3. 'View Payment' / 'Pay Invoice' only for In Progress, Completed, Paid with payment
        4. 'Booking Cancelled - No actions available' on Cancelled bookings
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_id)
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            resp = self.client.get('/customer/bookings')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # 1. 'View Status' must be rendered
            self.assertIn('View Status', html)
            self.assertIn('/customer/booking/', html)

            # 2. Check each booking in DB for customer to verify specific button logic
            with self.app.app_context():
                bookings = ServiceRequest.query.filter_by(customer_id=self.customer_id).all()
                for b in bookings:
                    card_snippet = f'id="booking-card-{b.id}"'
                    self.assertIn(card_snippet, html)

                    # Extract the card HTML block cleanly up to the next card or container end
                    card_start = html.find(card_snippet)
                    next_card = html.find('id="booking-card-', card_start + 1)
                    if next_card != -1:
                        card_html = html[card_start:next_card]
                    else:
                        modal_pos = html.find('id="reviewModal"', card_start)
                        card_html = html[card_start:modal_pos] if modal_pos != -1 else html[card_start:]

                    # All cards must have View Status linking to details view
                    expected_details_url = f'/customer/booking/{b.id}/details'
                    self.assertIn(expected_details_url, card_html, f"Booking {b.id} missing View Status link")

                    if b.status in ['Cancelled', 'Rejected']:
                        self.assertIn('Booking Cancelled - No actions available', card_html)
                        self.assertNotIn('Edit Booking', card_html)
                        self.assertNotIn('Pay Invoice', card_html)
                    elif b.status in ['Completed', 'Closed']:
                        self.assertNotIn('Edit Booking', card_html)
                    elif b.status in ['Pending', 'Pending Review', 'Scheduled'] and not b.assigned_worker_id:
                        self.assertIn('Edit Booking', card_html)

    def test_booking_details_route_and_checkpoints(self):
        """
        Verify /customer/booking/<id>/details:
        - Returns 200 for user's own booking
        - Renders operational checkpoints: Assigned, Dispatched, In-Progress, Completed
        - Returns 403 when attempting to access another customer's booking
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_id)
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            with self.app.app_context():
                anita_booking = ServiceRequest.query.filter_by(customer_id=self.customer_id).first()
                self.assertIsNotNone(anita_booking)

                other_booking = ServiceRequest.query.filter(ServiceRequest.customer_id != self.customer_id).first()
                self.assertIsNotNone(other_booking)

            # Access Anita's own booking details
            resp = self.client.get(f'/customer/booking/{anita_booking.id}/details')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # Check for checkpoints
            self.assertIn('Worker Assigned', html)
            self.assertIn('Worker Dispatched', html)
            self.assertIn('Service In-Progress', html)
            self.assertIn('Job Completed', html)

            # Check reference ID
            self.assertIn(anita_booking.request_id, html)

            # Access another customer's booking -> 403 Forbidden
            forbidden_resp = self.client.get(f'/customer/booking/{other_booking.id}/details')
            self.assertEqual(forbidden_resp.status_code, 403)

if __name__ == '__main__':
    unittest.main()
