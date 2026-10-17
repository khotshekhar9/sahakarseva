import unittest
import time
from datetime import datetime, timedelta
from app import app, db
from models.user import User
from models.worker import Worker
from models.service_request import ServiceRequest
from services.ai_service import AIService

class TestAiDemandForecasting(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.created_sr_ids = []
        with self.app.app_context():
            from models.customer import Customer
            from models.contractor import Contractor
            cust = Customer.query.first()
            contractor = Contractor.query.first()
            self.customer_id = cust.id if cust else 17
            self.contractor_id = contractor.id if contractor else 1

    def tearDown(self):
        with self.app.app_context():
            for sr_id in self.created_sr_ids:
                sr = db.session.get(ServiceRequest, sr_id)
                if sr:
                    db.session.delete(sr)
            db.session.commit()

    def _login_admin(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = '2'  # Admin user id 2 ('admin')
            sess['_fresh'] = True
            sess['login_time'] = time.time() + 10000.0


    def test_forecast_reads_directly_from_service_requests_and_workers(self):
        """
        Verification Criterion 1:
        Querying /admin/ai-demand reads directly from ServiceRequest and Worker tables
        rather than static dictionaries.
        """
        with self.app.app_context():
            forecast = AIService.forecast_gig_service_demand(city="Mumbai")
            self.assertIsInstance(forecast, dict)
            self.assertIn('forecast_data', forecast)
            self.assertIn('demand_matrix', forecast)
            self.assertIn('chart_labels', forecast)
            self.assertIn('chart_datasets', forecast)
            self.assertIn('total_projected_7d_jobs', forecast)
            self.assertIn('active_roster_count', forecast)
            self.assertEqual(len(forecast['chart_labels']), 7)
            self.assertEqual(len(forecast['forecast_data']), 8)

            # Confirm active workers count reflects actual DB count of verified available workers
            actual_available = Worker.query.filter(
                Worker.is_verified == True,
                Worker.availability_status == 'available'
            ).count()
            self.assertEqual(forecast['active_roster_count'], actual_available)

    def test_inserting_10_electrical_requests_immediately_updates_forecast_and_shifts_risk(self):
        """
        Verification Criterion 2:
        Inserting 10 new service requests for 'Electrical' in the database immediately
        updates the 7-day forecast count and shifts the Electrical risk badge from Balanced to Moderate/High.
        """
        with self.app.app_context():
            # 1. Baseline forecast before insert
            baseline = AIService.forecast_gig_service_demand(city="Mumbai")
            elec_baseline = next(d for d in baseline['forecast_data'] if 'Electrical' in d['trade'])
            base_proj = elec_baseline['projected_7d_demand']
            base_risk = elec_baseline['risk_level']

            # 2. Insert 10 new service requests for Electrical
            for i in range(10):
                sr = ServiceRequest(
                    request_id=f"TEST-EMG-SURGE-{int(time.time())}-{i}",
                    customer_id=self.customer_id,
                    customer_name="Anita Sharma",
                    mobile_number="+91-9820011223",
                    address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                    contractor_id=self.contractor_id,
                    category="Electrical",
                    title=f"Emergency Short Circuit Incident #{i}",
                    status="Pending",
                    created_at=datetime.utcnow()
                )
                db.session.add(sr)
                db.session.flush()
                self.created_sr_ids.append(sr.id)
            db.session.commit()

            # 3. Dynamic forecast immediately after DB insert
            updated = AIService.forecast_gig_service_demand(city="Mumbai")
            elec_updated = next(d for d in updated['forecast_data'] if 'Electrical' in d['trade'])
            new_proj = elec_updated['projected_7d_demand']
            new_risk = elec_updated['risk_level']
            new_deficit = elec_updated['deficit']

            # The 7-day forecast count must increase
            self.assertGreater(new_proj, base_proj, "Projected demand must increase after inserting 10 requests")
            # The risk level must shift to Moderate or High
            self.assertIn(new_risk, ['Moderate', 'High'], "Risk level must shift to Moderate or High")
            self.assertGreaterEqual(new_deficit, 1, "Deficit must be at least 1 after surge insert")

            # Check that recommendation mentions Chembur West
            self.assertIn('Chembur West', elec_updated['recommendation'])

    def test_admin_ai_demand_page_renders_cleanly(self):
        """
        Verification Criterion 3:
        Querying /admin/ai-demand renders the executive metric strip, dynamic table,
        and Chart.js setup without template or syntax errors.
        """
        self._login_admin()
        resp = self.client.get('/admin/ai-demand')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Verify executive metric strip
        self.assertTrue('AI Demand Forecasting & Surge Center' in html or 'AI Demand Forecasting &amp; Surge Center' in html)
        self.assertIn('7-Day Projected Demand', html)
        self.assertIn('Active Verified Roster', html)
        self.assertIn('Trades at Deficit Risk', html)

        # Verify dynamic table headers and trade rows
        self.assertTrue('Electrical & Appliance Repair' in html or 'Electrical &amp; Appliance Repair' in html)
        self.assertTrue('Plumbing & Drainage' in html or 'Plumbing &amp; Drainage' in html)
        self.assertTrue('Housekeeping & Deep Cleaning' in html or 'Housekeeping &amp; Deep Cleaning' in html)
        self.assertTrue('Caregivers & Patient Attendants' in html or 'Caregivers &amp; Patient Attendants' in html)

        # Verify Chart.js integration
        self.assertIn('demandForecastChart', html)
        self.assertIn('new Chart(', html)

        # Verify cooperative mobility advice
        self.assertIn('Cooperative Mobility', html)


if __name__ == '__main__':
    unittest.main()
