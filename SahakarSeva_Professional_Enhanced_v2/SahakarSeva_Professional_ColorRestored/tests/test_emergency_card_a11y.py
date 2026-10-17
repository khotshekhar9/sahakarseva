import unittest
import time
import re
from app import app, db
from models.user import User
from models.worker import Worker
from models.service_request import ServiceRequest
from models.customer import Customer

def calculate_relative_luminance(hex_color):
    """Calculates relative luminance according to WCAG 2.1 specifications."""
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    
    def adjust(channel):
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    r_lin = adjust(r)
    g_lin = adjust(g)
    b_lin = adjust(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

def contrast_ratio(hex1, hex2):
    """Calculates contrast ratio between two colors."""
    l1 = calculate_relative_luminance(hex1)
    l2 = calculate_relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


class TestEmergencyCardA11y(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            worker_user = User.query.filter_by(username='jdoe').first()
            if not worker_user:
                worker_user = User.query.filter_by(role='worker').first()
            self.worker_id = worker_user.id
            cust = Customer.query.first()
            self.customer_id = cust.id if cust else 17

    def test_worker_service_requests_emergency_card_rendering(self):
        """Verify worker service_requests view renders high-contrast emergency card for emergency jobs."""
        with self.app.app_context():
            emg = ServiceRequest.query.filter_by(assigned_worker_id=self.worker_id, is_emergency=True).first()
            created_id = None
            if not emg or emg.status in ('Completed', 'Closed'):
                emg = ServiceRequest(
                    request_id=f"TEST-EMG-REND-{int(time.time())}",
                    customer_id=self.customer_id,
                    customer_name="Anita Sharma",
                    mobile_number="9822000000",
                    category="Electrical",
                    title="Active Live Emergency Short Circuit",
                    address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                    status="Travelling",
                    is_emergency=True,
                    assigned_worker_id=self.worker_id,
                    latitude=19.0657,
                    longitude=72.8794,
                    fixed_rate=650.0
                )
                db.session.add(emg)
                db.session.commit()
                created_id = emg.id

        try:
            with self.client:
                with self.client.session_transaction() as sess:
                    sess['_user_id'] = str(self.worker_id)  # jdoe (Worker with assigned emergency jobs)
                    sess['_fresh'] = True
                    sess['login_time'] = time.time() + 10000.0

                resp = self.client.get('/worker/service-requests')
                self.assertEqual(resp.status_code, 200)
                html = resp.get_data(as_text=True)

                # Check emergency card components
                self.assertIn('emergency-status-card', html)
                self.assertIn('Live Emergency Destination (GPS)', html)
                self.assertIn('emergency-heading', html)
                self.assertIn('emergency-address-text', html)
                self.assertIn('emergency-instruction-text', html)
                self.assertIn('emergency-coord-badge', html)
                self.assertIn('emergency-pulse-dot', html)
        finally:
            if created_id:
                with self.app.app_context():
                    sr = ServiceRequest.query.get(created_id)
                    if sr:
                        db.session.delete(sr)
                        db.session.commit()

    def test_wcag_contrast_ratios(self):
        """Verify that color combinations pass WCAG 2.1 AA (4.5:1) and AAA (7:1)."""
        white = '#ffffff'
        danger_bootstrap = '#dc3545'
        danger_red_700 = '#b91c1c'
        danger_red_800 = '#991b1b'
        dark_grey = '#4a5568'
        amber_bg = '#f59e0b'
        amber_text = '#0f172a'

        # 1. Broken legacy state contrast (fails WCAG AA)
        broken_contrast = contrast_ratio(dark_grey, danger_bootstrap)
        self.assertLess(broken_contrast, 4.5, "Dark grey on solid red correctly demonstrates contrast failure")

        # 2. White text on Bootstrap red #dc3545 meets WCAG AA (>= 4.5:1)
        ratio_dc3545 = contrast_ratio(white, danger_bootstrap)
        self.assertGreaterEqual(ratio_dc3545, 4.5)

        # 3. White text on deep red #b91c1c / #991b1b meets high-contrast / WCAG AAA (up to 8.65:1)
        ratio_b91c1c = contrast_ratio(white, danger_red_700)
        self.assertGreaterEqual(ratio_b91c1c, 6.4, "White on #b91c1c exceeds 6.4:1 contrast")

        ratio_991b1b = contrast_ratio(white, danger_red_800)
        self.assertGreaterEqual(ratio_991b1b, 7.0, "White on #991b1b meets WCAG AAA enhanced contrast (8.65:1)")

        # 4. Amber Start Travel button text contrast
        ratio_amber_btn = contrast_ratio(amber_text, amber_bg)
        self.assertGreaterEqual(ratio_amber_btn, 7.0, "Amber button text meets WCAG AAA")

    def test_css_files_contain_emergency_a11y_overrides(self):
        """Verify style.css and final_polish.css include scoped rules neutralizing dark text inheritance."""
        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            style_css = f.read()

        with open('static/css/final_polish.css', 'r', encoding='utf-8') as f:
            polish_css = f.read()

        for css_content, filename in [(style_css, 'style.css'), (polish_css, 'final_polish.css')]:
            self.assertIn('.emergency-status-card', css_content, f"Missing in {filename}")
            self.assertIn('.emergency-instruction-text', css_content, f"Missing in {filename}")
            self.assertIn('.emergency-heading', css_content, f"Missing in {filename}")
            self.assertIn('.emergency-address-box', css_content, f"Missing in {filename}")
            self.assertIn('.emergency-coord-badge', css_content, f"Missing in {filename}")
            # Ensure dark utility neutralization is in place
            self.assertIn('.emergency-status-card .text-secondary', css_content, f"Missing in {filename}")
            self.assertIn('.emergency-status-card .text-muted', css_content, f"Missing in {filename}")
            self.assertIn('.emergency-status-card .text-dark', css_content, f"Missing in {filename}")

    def test_leaflet_osm_tiles_and_coordinate_guards(self):
        """Verify worker portal uses free OpenStreetMap tiles, validates coordinates, and provides fallback placeholders."""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(self.worker_id)
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            resp = self.client.get('/worker/service-requests')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # 1. Non-token OpenStreetMap tile layer used
            self.assertIn('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', html)
            self.assertNotIn('basemaps.cartocdn.com', html)

            # 2. Invalidate size called to prevent half-rendered grey tiles
            self.assertIn('invalidateSize()', html)

            # 3. Coordinate validation & placeholder fallback logic
            self.assertIn('map-placeholder', html)
            self.assertIn('Location coordinates pending', html)

    def test_job_update_and_completed_contrast_rules(self):
        """Verify contrast CSS rules for green and red panels in style.css and scoped styles."""
        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            style_css = f.read()

        # Green panels: .job-update-panel, .job-completed-banner, .panel-success
        self.assertIn('.job-update-panel', style_css)
        self.assertIn('.job-completed-banner', style_css)
        self.assertIn('.panel-success', style_css)

        # Red emergency panels: .emergency-destination-card, .panel-danger
        self.assertIn('.emergency-destination-card', style_css)
        self.assertIn('.panel-danger', style_css)

        # Map placeholder styling
        self.assertIn('.map-placeholder', style_css)

        # Contrast calculations
        white = '#ffffff'
        green_panel = '#198754'
        dark_green = '#0f5132'
        deep_red = '#b91c1c'
        dark_text = '#334155'

        # Demonstrating dark-on-dark legibility failure:
        dark_on_green = contrast_ratio(dark_text, green_panel)
        self.assertLess(dark_on_green, 4.5, "Dark text on green has severe legibility defect")

        # White on green passes WCAG AA:
        white_on_green = contrast_ratio(white, green_panel)
        self.assertGreaterEqual(white_on_green, 4.5, "White on #198754 green passes WCAG AA")

        # White on dark green passes WCAG AAA:
        white_on_dark_green = contrast_ratio(white, dark_green)
        self.assertGreaterEqual(white_on_dark_green, 7.0, "White on #0f5132 meets WCAG AAA")

        # White on deep red passes WCAG AA/AAA:
        white_on_deep_red = contrast_ratio(white, deep_red)
        self.assertGreaterEqual(white_on_deep_red, 6.4, "White on deep red exceeds 6.4:1 contrast")

    def test_state_based_lifecycle_guards_and_data_formatting(self):
        """Verify completed/paid jobs do not leak active emergency navigation and render formatted fallbacks."""
        with self.app.app_context():
            # Create completed test job and active job
            worker = Worker.query.get(self.worker_id)
            self.assertIsNotNone(worker)

            completed_job = ServiceRequest(
                request_id=f"TEST-DONE-{int(time.time())}",
                customer_id=self.customer_id,
                customer_name="Anita Sharma",
                mobile_number="9822000000",
                category="Electrical",
                title="Finished Wire Repair",
                address="Flat 402, Building 3B, Chheda Nagar, Chembur West, Mumbai - 400089",
                status="Completed",
                is_emergency=True,
                assigned_worker_id=worker.id,
                visit_date=None,
                fixed_rate=0.0,
                estimated_cost=0.0
            )
            db.session.add(completed_job)
            db.session.commit()
            comp_id = completed_job.id

        try:
            with self.client:
                with self.client.session_transaction() as sess:
                    sess['_user_id'] = str(self.worker_id)
                    sess['_fresh'] = True
                    sess['login_time'] = time.time() + 10000.0

                resp = self.client.get('/worker/service-requests')
                self.assertEqual(resp.status_code, 200)
                html = resp.get_data(as_text=True)

                # Fallback placeholders properly formatted
                self.assertIn('Flexible / On-Demand', html)
                self.assertIn('Tariff on Assessment', html)

                # Completed job proof of conclusion
                self.assertIn('Job concluded on', html)

                # In the completed card container, active navigation button should NOT be rendered
                card_html = html.split(f'id="job-{comp_id}"')[1].split('class="premium-card')[0] if f'id="job-{comp_id}"' in html else ""
                self.assertNotIn('⚡ Navigate to Live Emergency Location', card_html)
                self.assertIn('Job concluded on', card_html)

        finally:
            with self.app.app_context():
                sr = ServiceRequest.query.get(comp_id)
                if sr:
                    db.session.delete(sr)
                    db.session.commit()

if __name__ == '__main__':
    unittest.main()
