import unittest
import time
from app import app, db
from models.worker import Worker
from models.worker_features import WorkerCertification

class TestWorkerBenefitsAndCertificates(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_worker_benefits_page_decoupled(self):
        """
        Verify /worker/benefits:
        1. Returns 200
        2. Focuses exclusively on Suraksha Nidhi, PMSBY, PMJJBY, ESIC, and Cess History
        3. Does NOT contain 'Skills & Certificates' section
        4. Renders proper breadcrumb ('Benefits') without collision
        5. Highlights Benefits sidebar link as active and Certificates as inactive
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = '3'  # worker 'jdoe'
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            resp = self.client.get('/worker/benefits')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            # Welfare & Social Security content
            self.assertIn('Suraksha Nidhi', html)
            self.assertIn('Welfare Pool', html)
            self.assertIn('PMSBY', html)
            self.assertIn('PMJJBY', html)
            self.assertIn('ESIC', html)
            self.assertIn('Welfare Cess Contribution History', html)

            # Skills & Certificates must NOT bleed into Benefits page
            self.assertNotIn('Skills &amp; Certificates', html)
            self.assertNotIn('Skills & Certificates', html)

            # Check status badge text is rendered and not empty
            self.assertIn('Active Protection', html)

            # Check breadcrumb renders Benefits
            self.assertIn('<span class="bc-current">Benefits</span>', html)

            # Sidebar active state check: Benefits must be active, Certificates must not be active
            self.assertIn('href="/worker/benefits" title="Benefits & Social Security" class="nav-link active"', html)
            self.assertNotIn('href="/worker/certificates" title="Certificates" class="nav-link active"', html)

    def test_worker_certificates_page_dedicated(self):
        """
        Verify /worker/certificates:
        1. Returns 200
        2. Renders Trade Skills & Certifications header, skill badges, and document table
        3. Contains 'Upload New Certificate' trigger and modal form
        4. Highlights Certificates sidebar link as active and Benefits as inactive
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = '3'  # worker 'jdoe'
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            resp = self.client.get('/worker/certificates')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn('Trade Skills & Certifications', html)
            self.assertIn('Upload New Certificate', html)
            self.assertIn('uploadCertModal', html)
            self.assertIn('Skill India Recognized', html)
            self.assertIn('Cooperative KYC', html)

            # Check breadcrumb renders Certificates
            self.assertIn('<span class="bc-current">Certificates</span>', html)

            # Sidebar active state check: Certificates must be active, Benefits must not be active
            self.assertIn('href="/worker/certificates" title="Certificates" class="nav-link active"', html)
            self.assertNotIn('href="/worker/benefits" title="Benefits & Social Security" class="nav-link active"', html)

    def test_worker_certificate_upload_workflow(self):
        """
        Verify POST /worker/certificates/upload:
        1. Inserts a new WorkerCertification record with status 'Pending'
        2. Redirects cleanly back to /worker/certificates
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = '3'
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            unique_title = f"Test Electrical Safety Cert {int(time.time())}"
            form_data = {
                'cert_title': unique_title,
                'issuing_body': 'State Technical Board',
                'cert_number': 'STB-998811',
                'issue_date': '2025-01-15'
            }

            post_resp = self.client.post('/worker/certificates/upload', data=form_data, follow_redirects=True)
            self.assertEqual(post_resp.status_code, 200)
            html = post_resp.get_data(as_text=True)
            self.assertIn(unique_title, html)
            self.assertIn('Pending Approval', html)

            # Verify in DB
            with self.app.app_context():
                cert = WorkerCertification.query.filter_by(worker_id=3, cert_title=unique_title).first()
                self.assertIsNotNone(cert)
                self.assertEqual(cert.status, 'Pending')
                self.assertEqual(cert.cert_number, 'STB-998811')

    def test_endpoint_aliases_and_routing(self):
        """
        Verify both route aliases resolve without 404:
        /worker/benefits & /worker/benefits-page
        /worker/certificates & /worker/certificates-page
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_user_id'] = '3'
                sess['_fresh'] = True
                sess['login_time'] = time.time() + 10000.0

            r1 = self.client.get('/worker/benefits')
            self.assertEqual(r1.status_code, 200)

            r2 = self.client.get('/worker/benefits-page')
            self.assertEqual(r2.status_code, 200)

            r3 = self.client.get('/worker/certificates')
            self.assertEqual(r3.status_code, 200)

            r4 = self.client.get('/worker/certificates-page')
            self.assertEqual(r4.status_code, 200)

if __name__ == '__main__':
    unittest.main()
