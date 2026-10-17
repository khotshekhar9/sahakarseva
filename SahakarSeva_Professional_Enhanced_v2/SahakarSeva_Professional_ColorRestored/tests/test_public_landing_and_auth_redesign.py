import unittest
from app import app, db
from models.user import User

class TestPublicLandingAndAuthRedesign(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_public_landing_page_renders(self):
        """Verify GET / renders the full-width, clean CivicPulse public landing page."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # 1. Top Navigation Bar elements
        self.assertIn('SahakarSeva', html)
        self.assertIn('COOPERATIVE GIG PLATFORM', html)
        self.assertIn('Features', html)
        self.assertIn('How It Works', html)
        self.assertIn('Cooperative Societies', html)
        self.assertIn('Suraksha Nidhi', html)
        self.assertIn('Book a Service', html)

        # 2. Hero Section elements
        self.assertIn('STATUTORY COOPERATIVE GIG PLATFORM', html)
        self.assertIn('Empowering Local Artisans.', html)
        self.assertIn('Fair Gig Services for Communities.', html)
        self.assertIn('Regulated Under Maharashtra Cooperative Societies Framework', html)
        self.assertNotIn('National Hackathon Prototype', html)
        self.assertNotIn('Problem Statement ID', html)

        # 3. 4 Live Platform Snapshot metric cards
        self.assertIn('₹2,48,500+', html)
        self.assertIn('Direct Artisan Wages Distributed', html)
        self.assertIn('1,240+', html)
        self.assertIn('Verified Cooperative Jobs Completed', html)
        self.assertIn('100%', html)
        self.assertIn('Social Security & Suraksha Nidhi Coverage', html)
        self.assertIn('< 15 Mins', html)
        self.assertIn('Average Local Dispatch Time', html)

        # 4. 6 Capabilities Grid
        self.assertIn('Direct Cooperative Hiring', html)
        self.assertIn('Statutory 88/8/4 Wage Split', html)
        self.assertIn('Suraksha Nidhi Insurance', html)
        self.assertIn('QR-Verified Site Attendance', html)
        self.assertIn('Real-Time WebSocket Dispatch', html)
        self.assertIn('Apex Federation Governance', html)

        # 5. 4-Step Process Section
        self.assertIn('Citizen Request', html)
        self.assertIn('Cooperative Dispatch', html)
        self.assertIn('Verified Execution', html)
        self.assertIn('Transparent Split', html)

        # 6. Verify split-screen banner was eliminated from landing
        self.assertNotIn('Simple service. Trusted workers. Fair work.', html)

    def test_standalone_login_page_renders_clean_centered_card(self):
        """Verify GET /login renders a clean, centered card with 1-click demo logins and no green half-banner."""
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # 1. Clean card structure
        self.assertIn('Sign In', html)
        self.assertIn('Access your cooperative dashboard or community services portal.', html)
        self.assertIn('Username or Email Address', html)
        self.assertIn('Password', html)
        self.assertIn('name="username"', html)
        self.assertIn('name="password"', html)

        # 2. Quick Role Sign-in Bar
        self.assertIn('QUICK ROLE SIGN-IN', html)
        self.assertIn('Federation Admin', html)
        self.assertIn('Society Admin', html)
        self.assertIn('Artisan (Worker)', html)
        self.assertIn('Customer', html)
        self.assertIn('trigger1ClickDemo', html)
        self.assertNotIn('Problem Statement ID', html)

        # 3. Footer Links
        self.assertIn('Create an account', html)
        self.assertIn('Register Society', html)

        # 4. Ensure old split screen banner text is gone
        self.assertNotIn('Simple service. Trusted workers. Fair work.', html)

    def test_1click_demo_authentication(self):
        """Verify 1-click demo credentials authenticate smoothly to respective dashboards."""
        with self.app.app_context():
            # Ensure demo publisher user exists or is set up
            pub = User.query.filter_by(username='publisher').first()
            if not pub:
                pub = User(username='publisher', email='publisher@sahakarseva.org', role='publisher')
                pub.set_password('publisher123')
                db.session.add(pub)
                db.session.commit()

        # Test login with demo password tolerance
        res = self.client.post('/login', data={
            'username': 'publisher',
            'password': 'password123'
        }, follow_redirects=False)

        # Should redirect to publisher dashboard
        self.assertEqual(res.status_code, 302)
        self.assertIn('/publisher/dashboard', res.headers.get('Location', ''))

    def test_register_page_renders_tabbed_onboarding(self):
        """Verify GET /register provides options for Customer registration and Society onboarding."""
        res = self.client.get('/register')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn('Create Account', html)
        self.assertIn('Citizen / Client', html)
        self.assertIn('Labour Society', html)
        self.assertIn('Artisan', html)
        self.assertIn('Register Primary Labour Cooperative Society', html)
        self.assertTrue('/register-contractor' in html or '/register_contractor' in html)

    def test_landing_alias_redirects_to_root(self):
        """Verify /landing alias redirects to /."""
        res = self.client.get('/landing')
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.headers.get('Location'), '/')

if __name__ == '__main__':
    unittest.main()
