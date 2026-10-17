import unittest
import time
from app import app, db, socketio
from models.user import User
from models.worker import Worker
from models.service_request import ServiceRequest
from services.dispatch_service import DispatchService


class TestEmergencyDispatchSocketIO(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.created_request_ids = []
        with self.app.app_context():
            cust = User.query.filter_by(role='customer').first()
            worker = User.query.filter_by(role='worker').first()
            self.customer_id = cust.id if cust else 17
            self.worker_id = worker.id if worker else 7
            self.customer_user_id = self.customer_id
            self.worker_user_id = self.worker_id

    def tearDown(self):
        with self.app.app_context():
            from models.finance import Payment
            from models.communication import Notification
            for req_id in self.created_request_ids:
                Payment.query.filter_by(service_request_id=req_id).delete()
                Notification.query.filter(Notification.message.like(f"%{req_id}%")).delete()
                sr = db.session.get(ServiceRequest, req_id)
                if sr:
                    db.session.delete(sr)
            db.session.commit()

    def _login(self, user_id=None):
        if user_id is None:
            user_id = self.customer_user_id
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0

    def test_socketio_connection_and_room_subscription(self):
        """Verify Socket.IO test client connects cleanly and subscribes to rooms."""
        s_client = socketio.test_client(self.app)
        self.assertTrue(s_client.is_connected())

        # Join trade rooms and personal worker room
        s_client.emit('join_trade_room', {
            'trade_category': 'Electrical',
            'trades': ['Electrical', 'General'],
            'worker_id': 3
        })

        # Track booking room
        s_client.emit('track_booking_room', {
            'booking_id': 9999
        })

        received = s_client.get_received()
        # No crashes or disconnects
        self.assertTrue(s_client.is_connected())
        s_client.disconnect()

    def test_emergency_broadcast_targeted_socketio_emission(self):
        """Verify creating an emergency broadcast emits emergency_job_alert only to targeted trade rooms."""
        client_electrician = socketio.test_client(self.app)
        client_plumber = socketio.test_client(self.app)

        self.assertTrue(client_electrician.is_connected())
        self.assertTrue(client_plumber.is_connected())

        client_electrician.emit('join_trade_room', {
            'trade_category': 'Electrical',
            'worker_id': 3
        })
        client_plumber.emit('join_trade_room', {
            'trade_category': 'Plumbing',
            'worker_id': 4
        })

        # Clear any handshake messages
        client_electrician.get_received()
        client_plumber.get_received()

        with self.app.app_context():
            res = DispatchService.create_and_broadcast_emergency(
                customer_id=self.customer_id,
                category='Electrical',
                severity='Critical',
                title='Main Switchboard Hazard',
                description='Sparking and smoke from main breaker',
                address='14 Sindhi Society, Chembur, Mumbai',
                lat=19.052,
                lng=72.899,
                radius_km=5.0
            )
            self.assertTrue(res['success'])
            self.created_request_ids.append(res['id'])

            # Verify electrician client received emergency_job_alert
            electrician_events = client_electrician.get_received()
            alert_event = next((e for e in electrician_events if e['name'] == 'emergency_job_alert'), None)
            self.assertIsNotNone(alert_event, "Electrician should have received emergency_job_alert")

            payload = alert_event['args'][0]
            self.assertEqual(payload['id'], res['id'])
            self.assertEqual(payload['category'], 'Electrical')
            self.assertEqual(payload['ticket_no'], res['request_id'])
            self.assertIn('address', payload)
            self.assertAlmostEqual(payload['tariff_total'], 650.0, delta=1.0)
            self.assertAlmostEqual(payload['estimated_payout'], float(res['worker_payout']), delta=1.0)
            self.assertEqual(payload['expires_in_seconds'], 900)

            # Verify plumber client did NOT receive emergency_job_alert
            plumber_events = client_plumber.get_received()
            plumber_alert = next((e for e in plumber_events if e['name'] == 'emergency_job_alert'), None)
            self.assertIsNone(plumber_alert, "Plumber should not receive electrical emergency alert")

        client_electrician.disconnect()
        client_plumber.disconnect()

    def test_emergency_claim_socketio_lifecycle(self):
        """Verify claiming an emergency sets status=Travelling and emits updates to booking and trade rooms."""
        with self.app.app_context():
            # Create emergency request
            res = DispatchService.create_and_broadcast_emergency(
                customer_id=self.customer_id,
                category='Electrical',
                severity='Critical',
                title='Water heater spark',
                description='Live electrical spark',
                address='Chembur West, Mumbai',
                lat=19.05,
                lng=72.89
            )
            req_id = res['id']
            self.created_request_ids.append(req_id)

            # Connect customer tracking client
            client_customer = socketio.test_client(self.app)
            client_customer.emit('track_booking_room', {'booking_id': req_id})

            # Connect another worker client subscribed to Electrical trade
            client_other_worker = socketio.test_client(self.app)
            client_other_worker.emit('join_trade_room', {'trade_category': 'Electrical', 'worker_id': 99})

            # Clear join events
            client_customer.get_received()
            client_other_worker.get_received()

            # Worker claims the request
            claim_res = DispatchService.claim_emergency_request(req_id, worker_id=self.worker_id)
            self.assertTrue(claim_res['success'], f"Claim failed: {claim_res}")

            # Verify database state
            sr = db.session.get(ServiceRequest, req_id)
            self.assertEqual(sr.status, 'Travelling')
            self.assertEqual(sr.broadcast_status, 'Claimed')
            self.assertEqual(sr.assigned_worker_id, self.worker_id)

            # Verify customer client received emergency_status_update
            cust_events = client_customer.get_received()
            status_event = next((e for e in cust_events if e['name'] == 'emergency_status_update'), None)
            self.assertIsNotNone(status_event, "Customer should receive emergency_status_update")

            cust_payload = status_event['args'][0]
            self.assertEqual(cust_payload['booking_id'], req_id)
            self.assertEqual(cust_payload['status'], 'Travelling')
            self.assertEqual(cust_payload['status_label'], 'Artisan Dispatched & En Route')
            self.assertEqual(cust_payload['arrival_otp'], sr.otp)
            self.assertTrue(cust_payload['worker_name'])
            self.assertTrue(cust_payload['worker_phone'])
            self.assertIn('worker_tier', cust_payload)

            # Verify other worker client received emergency_broadcast_dismissed
            other_events = client_other_worker.get_received()
            dismiss_event = next((e for e in other_events if e['name'] == 'emergency_broadcast_dismissed'), None)
            self.assertIsNotNone(dismiss_event, "Other worker should receive emergency_broadcast_dismissed")
            self.assertEqual(dismiss_event['args'][0]['id'], req_id)

            client_customer.disconnect()
            client_other_worker.disconnect()

    def test_customer_emergency_request_page_rendering(self):
        """Verify /customer/emergency-request renders the 1-click rate cards and dispatch trigger."""
        self._login(user_id=self.customer_user_id)
        resp = self.client.get('/customer/emergency-request')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Instant Emergency Artisan Dispatch', html)
        self.assertIn('Select Emergency Service Trade', html)
        self.assertIn('Electrical', html)
        self.assertIn('Plumbing', html)
        self.assertIn('Caregiving', html)
        self.assertIn('BROADCAST EMERGENCY SOS NOW', html)
        self.assertIn('Detect Current GPS', html)

    def test_customer_booking_status_route_alias(self):
        """Verify /customer/booking-status/<id> serves the booking tracking page with Socket.IO integration."""
        self._login(user_id=self.customer_user_id)
        with self.app.app_context():
            # Get existing booking for customer
            sr = ServiceRequest.query.filter_by(customer_id=self.customer_id).first()
            if not sr:
                sr = ServiceRequest(
                    request_id="SR-TEST-ALIAS",
                    customer_id=self.customer_id,
                    customer_name="Anita Sharma",
                    category="Electrical",
                    title="Socket check",
                    address="Chembur, Mumbai",
                    status="Travelling"
                )
                db.session.add(sr)
                db.session.commit()
                self.created_request_ids.append(sr.id)
            booking_id = sr.id

        resp = self.client.get(f'/customer/booking-status/{booking_id}')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Live Service Tracking', html)
        self.assertIn('socket.io.min.js', html)
        self.assertIn('track_booking_room', html)
        self.assertIn('emergency_status_update', html)

    def test_worker_service_requests_socketio_integration(self):
        """Verify /worker/service-requests renders Socket.IO client, trade subscription, and emergency feed."""
        self._login(user_id=self.worker_user_id)
        resp = self.client.get('/worker/service-requests')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('socket.io.min.js', html)
        self.assertIn('emergency-broadcast-feed', html)
        self.assertIn('join_trade_room', html)
        self.assertIn('emergency_job_alert', html)
        self.assertIn('emergency_broadcast_dismissed', html)
        self.assertIn('claimEmergencyJob', html)
        self.assertIn('playEmergencyChime', html)


if __name__ == '__main__':
    unittest.main()
