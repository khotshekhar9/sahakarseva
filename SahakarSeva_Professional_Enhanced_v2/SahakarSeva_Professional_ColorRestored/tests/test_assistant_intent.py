import unittest
import json
import sys
from app import app, db
from models.user import User
from models.service_request import ServiceRequest
from services.ai_service import (
    AIService,
    INTENT_BOOK_SERVICE,
    INTENT_CHECK_STATUS,
    INTENT_COMPLAINT_OR_HELP,
    INTENT_GENERAL_FAQ,
    INTENT_CANCEL_FLOW,
    INTENT_PAYMENT,
    INTENT_EMERGENCY
)

class TestAssistantConversationalState(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            ServiceRequest.query.filter(
                ServiceRequest.customer_id == 11,
                ServiceRequest.request_id != 'EMG-2026-000009',
                ServiceRequest.status == 'Travelling'
            ).update({'status': 'Completed'})
            emg = ServiceRequest.query.filter_by(request_id='EMG-2026-000009').first()
            if emg:
                emg.status = 'Travelling'
            db.session.commit()

    def test_intent_classification(self):
        """Verify intent classifier assigns correct intent to various customer phrases."""
        test_cases = [
            ('What is my latest booking status?', INTENT_CHECK_STATUS),
            ('wanna know the status of my booked service', INTENT_CHECK_STATUS),
            ('booking made on 12 sept', INTENT_CHECK_STATUS),
            ('where is my worker', INTENT_CHECK_STATUS),
            ('track service', INTENT_CHECK_STATUS),
            ('I need a plumber', INTENT_BOOK_SERVICE),
            ('book an electrician', INTENT_BOOK_SERVICE),
            ('I want to book a service', INTENT_BOOK_SERVICE),
            ('cancel this booking', INTENT_CANCEL_FLOW),
            ('stop', INTENT_CANCEL_FLOW),
            ('where can i pay my bill', INTENT_PAYMENT),
            ('gas leak immediate emergency', INTENT_EMERGENCY),
            ('worker broke my tap, file complaint', INTENT_COMPLAINT_OR_HELP),
            ('how much do you charge for deep cleaning?', INTENT_GENERAL_FAQ),
        ]
        for query, expected_intent in test_cases:
            detected = AIService.classify_assistant_intent(query, role='customer')
            self.assertEqual(
                detected, expected_intent,
                f"Query '{query}' expected {expected_intent}, got {detected}"
            )

    def test_entity_extraction(self):
        """Verify entity extraction for dates and categories."""
        ent1 = AIService.extract_assistant_entities('booking made on 12 sept')
        self.assertIn('date', ent1)
        self.assertEqual(ent1['date'].day, 12)
        self.assertEqual(ent1['date'].month, 9)

        ent2 = AIService.extract_assistant_entities('I need a plumber tomorrow')
        self.assertEqual(ent2.get('category'), 'Plumber')
        self.assertIn('date', ent2)

        ent3 = AIService.extract_assistant_entities('status of booking SR-2026-000004')
        self.assertEqual(ent3.get('request_id'), 'SR-2026-000004')

    def test_database_status_lookup_for_customer(self):
        """Verify database lookup produces concise, conversational responses."""
        with self.app.app_context():
            # User 11 is Anita Sharma
            ent = AIService.extract_assistant_entities('booking made on 12 sept')
            res = AIService.lookup_booking_status(11, entities=ent)
            self.assertIsNotNone(res)
            reply = res['reply']
            # Should mention scheduled for 12 Sep 2026 and status
            self.assertIn('12 Sep 2026', reply)
            self.assertIn('currently', reply.lower())

    def test_context_switch_and_slot_trap_prevention(self):
        """
        Simulate user trapped in session['assistant_booking'], then asking for status.
        Must NOT echo prompt into category ('Great. What Is My Latest Booking Status? service').
        Must instead switch context and return status!
        """
        import time
        with self.client:
            with self.app.app_context():
                anita = User.query.get(11)
                self.assertIsNotNone(anita)

            with self.client.session_transaction() as sess:
                sess['_user_id'] = '11'
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0
                # Simulate customer currently in booking flow at 'category' step
                sess['assistant_booking'] = {'step': 'category'}

            # Now customer asks: "What is my latest booking status?"
            resp = self.client.post('/api/assistant', json={'message': 'What is my latest booking status?'})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            reply = data.get('reply', '')

            # Assert prompt was NOT echoed as a category
            self.assertNotIn('What Is My Latest Booking Status?', reply)
            self.assertNotIn('What is the problem?', reply)
            # Assert status was returned
            self.assertTrue(
                any(status in reply for status in ['Travelling', 'In Progress', 'Pending', 'Assigned', 'Closed', 'Completed']),
                f"Expected status in reply, got: {reply}"
            )

            # Check that booking flow was cleared from session
            with self.client.session_transaction() as sess:
                self.assertNotIn('assistant_booking', sess)

    def test_category_strict_validation(self):
        """
        When user is in booking flow and types unrecognized trade name,
        it should not echo it into category.
        """
        import time
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = '11'
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0
                sess['assistant_booking'] = {'step': 'category'}

            # User types nonsense
            resp = self.client.post('/api/assistant', json={'message': 'random gibberish trade'})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            reply = data.get('reply', '')
            self.assertNotIn('Great. Random Gibberish Trade service', reply)
            self.assertIn('Which service do you need?', reply)

    def test_all_user_problem_queries(self):
        """
        Test each specific query mentioned in the problem description:
        - 'What is my latest booking status?'
        - 'wanna know the status of my booked service'
        - 'booking made on 12 sept'
        - 'where is my worker'
        - 'I need a plumber'
        """
        import time
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = '11'
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            # 1. "wanna know the status of my booked service"
            r1 = self.client.post('/api/assistant', json={'message': 'wanna know the status of my booked service'})
            self.assertEqual(r1.status_code, 200)
            data1 = r1.get_json()
            self.assertIn('EMG-2026-000009', data1['reply'])
            self.assertIn('Travelling', data1['reply'])
            self.assertIn('Jdoe', data1['reply'])

            # 2. "booking made on 12 sept"
            r2 = self.client.post('/api/assistant', json={'message': 'booking made on 12 sept'})
            self.assertEqual(r2.status_code, 200)
            data2 = r2.get_json()
            self.assertIn('12 Sep 2026', data2['reply'])
            self.assertIn('EMG-2026-000009', data2['reply'])

            # 3. "where is my worker"
            r3 = self.client.post('/api/assistant', json={'message': 'where is my worker'})
            self.assertEqual(r3.status_code, 200)
            data3 = r3.get_json()
            self.assertIn('Jdoe', data3['reply'])
            self.assertIn('traveling to your location', data3['reply'])

            # 4. "I need a plumber"
            r4 = self.client.post('/api/assistant', json={'message': 'I need a plumber'})
            self.assertEqual(r4.status_code, 200)
            data4 = r4.get_json()
            self.assertIn('Plumber service', data4['reply'])
            self.assertEqual(data4.get('state'), 'booking_problem')

            # 5. Mid-flow switch: While in booking problem step, user asks for status
            r5 = self.client.post('/api/assistant', json={'message': 'What is my latest booking status?'})
            self.assertEqual(r5.status_code, 200)
            data5 = r5.get_json()
            # Must NOT echo into problem or title
            self.assertNotIn('What is the problem?', data5['reply'])
            self.assertIn('EMG-2026-000009', data5['reply'])

    def test_worker_assistant_queries(self):
        """Verify assistant handles worker role intents properly."""
        import time
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = '3'  # jdoe (worker)
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            # 1. Next job query
            r1 = self.client.post('/api/assistant', json={'message': 'What is my next job?'})
            self.assertEqual(r1.status_code, 200)
            data1 = r1.get_json()
            self.assertTrue('job' in data1['reply'].lower() or 'assigned' in data1['reply'].lower())

            # 2. Attendance query
            r2 = self.client.post('/api/assistant', json={'message': 'How do I check in?'})
            self.assertEqual(r2.status_code, 200)
            data2 = r2.get_json()
            self.assertIn('GPS attendance', data2['reply'])

            # 3. Earnings query
            r3 = self.client.post('/api/assistant', json={'message': 'Show my earnings'})
            self.assertEqual(r3.status_code, 200)
            data3 = r3.get_json()
            self.assertTrue('earnings' in data3['reply'].lower() or '₹' in data3['reply'])

if __name__ == '__main__':
    unittest.main()


