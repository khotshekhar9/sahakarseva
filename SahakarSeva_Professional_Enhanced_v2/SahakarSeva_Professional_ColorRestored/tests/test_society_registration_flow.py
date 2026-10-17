import unittest
import time
from app import app, db
from models.user import User
from models.contractor import Contractor
from models.communication import ActivityLog, Notification


class TestSocietyRegistrationFlow(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_registration_page_renders_with_simplified_copy_and_demo_filler(self):
        """Verify the 3-step registration page renders with plain English copy and demo button."""
        res = self.client.get('/register-contractor')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # 1. Check Demo Autofill button
        self.assertIn('Auto-Fill Chembur Cooperative', html)
        self.assertIn('fillDemoSociety()', html)

        # 2. Check Step 1 copy & field simplifications
        self.assertIn('Step 1: Society Details & Registration', html)
        self.assertIn('Society Name *', html)
        self.assertIn('Primary Trade / Service *', html)
        self.assertIn('Registration License No. *', html)
        self.assertIn('Operating Ward / Areas *', html)
        self.assertIn('Worker Welfare & Society Overview', html)
        self.assertIn('Upload Registration Certificate (PDF or Image)', html)

        # 3. Check Step 2 copy
        self.assertIn('Step 2: Society Secretary / Admin Account', html)
        self.assertIn('Admin Username *', html)
        self.assertIn('Email Address *', html)
        self.assertIn('Mobile / Helpline *', html)
        self.assertIn('Password *', html)
        self.assertIn('Office Address', html)

        # 4. Check Step 3 copy & button text
        self.assertIn('Step 3: Review Application & Submit', html)
        self.assertIn('Primary Cooperative Society Details', html)
        self.assertIn('Submit Registration to Apex Federation', html)

        # 5. Verify optional fields do not have required attribute
        self.assertNotIn('name="description" id="inp_description" rows="2" required', html)
        self.assertNotIn('name="license_document" id="inp_license_document" accept="image/*,application/pdf" required', html)

    def test_registration_route_aliases(self):
        """Verify /register_contractor and /register-society routes load cleanly."""
        res1 = self.client.get('/register_contractor')
        self.assertEqual(res1.status_code, 200)

        res2 = self.client.get('/register-society')
        self.assertEqual(res2.status_code, 200)

    def test_submit_registration_with_autofill_data_without_file_upload(self):
        """Verify submitting registration without uploading a file auto-mocks sample certificate and creates pending society."""
        ts = int(time.time() * 1000) % 1000000
        test_username = f"chembur_soc_{ts}"
        test_email = f"admin_{ts}@chemburcoop.org"

        payload = {
            'company_name': 'Chembur Shramik Labour Cooperative Society Ltd.',
            'business_type': 'Multi-Trade Household Services',
            'license_number': f'MH/MUM/COOP/2026/{ts}',
            'service_areas': 'Kurla, Chembur, Govandi, Ghatkopar',
            'description': 'Affiliated primary labour cooperative with 45 artisan members.',
            'username': test_username,
            'email': test_email,
            'phone': '+91 98201 54321',
            'password': 'SocietyPass123!',
            'office_address': 'Office 12, Sahakar Bhavan, Chembur, Mumbai 400071'
        }

        res = self.client.post('/register-contractor', data=payload, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers.get('Location', ''))

        with self.app.app_context():
            user = User.query.filter_by(username=test_username).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, test_email)
            self.assertEqual(user.role, 'admin')

            contractor = Contractor.query.filter_by(user_id=user.id).first()
            self.assertIsNotNone(contractor)
            self.assertEqual(contractor.company_name, 'Chembur Shramik Labour Cooperative Society Ltd.')
            self.assertEqual(contractor.onboarding_status, 'pending_approval')
            self.assertFalse(contractor.is_verified)
            self.assertIsNotNone(contractor.license_document)
            self.assertIn('sample_business_license.pdf', contractor.license_document)


if __name__ == '__main__':
    unittest.main()
