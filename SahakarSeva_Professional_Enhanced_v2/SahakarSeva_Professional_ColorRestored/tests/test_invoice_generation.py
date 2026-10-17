import unittest
import time
from datetime import datetime, date
from app import app, db
from models.user import User
from models.customer import Customer
from models.contractor import Contractor
from models.service_request import ServiceRequest
from models.quotation import Quotation
from models.finance import Payment
from services.welfare_service import WelfareService
from services.dispatch_service import DispatchService

class TestAutomaticInvoiceAndPaymentGeneration(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.clean_ids = []
        with self.app.app_context():
            from models.customer import Customer
            from models.contractor import Contractor
            cust = Customer.query.first()
            contractor = Contractor.query.first()
            self.customer_id = cust.id if cust else 17
            self.contractor_id = contractor.id if contractor else 1
            self.customer_user_id = self.customer_id

    def tearDown(self):
        with self.app.app_context():
            for req_id in self.clean_ids:
                Payment.query.filter_by(service_request_id=req_id).delete()
                Quotation.query.filter_by(service_request_id=req_id).delete()
                sr = db.session.get(ServiceRequest, req_id)
                if sr:
                    db.session.delete(sr)
            db.session.commit()

    def test_welfare_service_88_8_4_calculation(self):
        """Verify WelfareService computes the 88/8/4 cooperative margin ledger."""
        split = WelfareService.calculate_cess_split(8000.40, split_mode="88_8_4")
        self.assertEqual(split['gross_amount'], 8000.40)
        self.assertEqual(split['worker_percentage'], 88)
        self.assertEqual(split['society_percentage'], 8)
        self.assertEqual(split['welfare_percentage'], 4)
        self.assertAlmostEqual(split['worker_payout'], round(8000.40 * 0.88, 2), places=2)
        self.assertAlmostEqual(split['society_admin_fee'], round(8000.40 * 0.08, 2), places=2)
        self.assertAlmostEqual(split['welfare_cess'], round(8000.40 * 0.04, 2), places=2)

    def test_automatic_invoice_generation_on_quotation_approval(self):
        """
        Verify that clicking 'Approve Quotation' on a standard quotation:
        1. Updates quotation to 'Approved' and service request to 'Quotation Approved'
        2. Automatically creates a Payment record with invoice number, amount, and 88/8/4 ledger
        3. Sets payment_status on ServiceRequest
        4. Invoicing card in tracking view renders the invoice, 88/8/4 breakdown, and Pay CTA
        5. Does not show 'No Invoices Issued Yet'
        """
        with self.app.app_context():
            # Create a test service request for customer
            ts = int(time.time() * 1000) % 1000000
            req = ServiceRequest(
                request_id=f"SR-TEST-{ts:06d}",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="9822012345",
                category="Electrical",
                title="Kitchen Rewiring and Distribution Board",
                description="Replace old wiring and install modern circuit breakers.",
                address="Bunglow 14, Sindhi Society, Chembur Central, Mumbai - 400071",
                status="Pending Review"
            )
            db.session.add(req)
            db.session.flush()
            self.clean_ids.append(req.id)
            req_id = req.id

            # Create an attached quotation for ₹8,000.40
            quote = Quotation(
                quotation_number=f"QTN-TEST-{ts:06d}",
                service_request_id=req.id,
                labour_cost=6500.00,
                equipment_charges=500.00,
                gst=1000.40,
                grand_total=8000.40,
                validity_date=date(2026, 12, 31),
                status="Pending"
            )
            db.session.add(quote)
            db.session.commit()
            quote_id = quote.id

        # Log in as Customer
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_user_id)
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            # Approve the quotation
            approve_resp = self.client.post(
                f'/customer/quotation/{quote_id}/respond',
                data={'action': 'approve'},
                follow_redirects=True
            )
            self.assertEqual(approve_resp.status_code, 200)

            # Verify Database State
            with self.app.app_context():
                refreshed_quote = db.session.get(Quotation, quote_id)
                refreshed_req = db.session.get(ServiceRequest, req_id)
                self.assertEqual(refreshed_quote.status, 'Approved')
                self.assertEqual(refreshed_req.status, 'Quotation Approved')

                # Verify Payment / Invoice record was created
                payment = Payment.query.filter_by(service_request_id=req_id, type='revenue').first()
                self.assertIsNotNone(payment, "Payment record was not generated automatically upon quotation approval!")
                self.assertEqual(float(payment.amount), 8000.40)
                self.assertEqual(payment.status, 'Pending')
                self.assertTrue(payment.invoice_number.startswith('INV-'))
                self.assertEqual(payment.quotation_number, refreshed_quote.quotation_number)

                # Verify 88/8/4 cooperative margin ledger fields
                expected_worker = round(8000.40 * 0.88, 2)
                expected_society = round(8000.40 * 0.08, 2)
                expected_welfare = round(8000.40 * 0.04, 2)
                self.assertAlmostEqual(float(payment.worker_payout), expected_worker, places=2)
                self.assertAlmostEqual(float(payment.society_admin_fee), expected_society, places=2)
                self.assertAlmostEqual(float(payment.welfare_cess), expected_welfare, places=2)

                # Test ServiceRequest convenience property
                self.assertIsNotNone(refreshed_req.payment)
                self.assertEqual(refreshed_req.payment.id, payment.id)
                self.assertEqual(refreshed_req.payment_id, payment.id)

            # Check /customer/booking/<id>/details rendering
            resp_details = self.client.get(f'/customer/booking/{req_id}/details')
            self.assertEqual(resp_details.status_code, 200)
            html_details = resp_details.get_data(as_text=True)

            self.assertIn('Invoicing & Payment', html_details)
            self.assertIn('₹8000.40', html_details)
            self.assertIn('Statutory 88/8/4 Cooperative Wage Distribution', html_details)
            self.assertIn('Artisan Wage (88%)', html_details)
            self.assertIn('Society Ops (8%)', html_details)
            self.assertIn('Suraksha Nidhi (4%)', html_details)
            self.assertIn('Pay ₹8000.40 via UPI / Card', html_details)
            self.assertNotIn('No Invoices Issued Yet', html_details)

            # Check /customer/booking/<id>/status route alias rendering
            resp_status = self.client.get(f'/customer/booking/{req_id}/status')
            self.assertEqual(resp_status.status_code, 200)
            html_status = resp_status.get_data(as_text=True)
            self.assertIn('₹8000.40', html_status)
            self.assertIn('Pay ₹8000.40 via UPI / Card', html_status)

    def test_emergency_dispatch_baseline_invoice(self):
        """
        Verify that an emergency dispatch with base tariff ₹650:
        1. Automatically instantiates baseline Payment record with status 'Pending Payment'
        2. Populates 88/8/4 cooperative ledger immediately
        3. Tracking page renders baseline emergency tariff without placeholder
        """
        with self.app.app_context():
            res = DispatchService.create_and_broadcast_emergency(
                customer_id=self.customer_id,
                category="Electrical",
                severity="Critical",
                title="Sparking Main Switchboard",
                description="Emergency short circuit at main breaker panel.",
                address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                lat=19.0601,
                lng=72.8964,
                radius_km=5.0
            )
            self.assertTrue(res['success'])
            emg_id = res['id']
            self.clean_ids.append(emg_id)

            # Verify Payment in DB
            pay = Payment.query.filter_by(service_request_id=emg_id, type='revenue').first()
            self.assertIsNotNone(pay, "Emergency dispatch did not generate baseline payment!")
            self.assertEqual(float(pay.amount), 650.00)
            self.assertEqual(pay.status, 'Pending Payment')
            self.assertTrue(pay.invoice_number.startswith('INV-'))
            self.assertAlmostEqual(float(pay.worker_payout), round(650.0 * 0.88, 2), places=2)
            self.assertAlmostEqual(float(pay.society_admin_fee), round(650.0 * 0.08, 2), places=2)
            self.assertAlmostEqual(float(pay.welfare_cess), round(650.0 * 0.04, 2), places=2)

        # Log in and check tracking page
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.customer_user_id)
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            resp = self.client.get(f'/customer/booking/{emg_id}/status')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn('Invoicing & Payment', html)
            self.assertIn('₹650.00', html)
            self.assertIn('Emergency Tariff', html)
            self.assertIn('Pay ₹650.00 via UPI / Card', html)
            self.assertNotIn('No Invoices Issued Yet', html)

if __name__ == '__main__':
    unittest.main()
