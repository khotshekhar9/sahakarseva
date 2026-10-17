#!/usr/bin/env python3
"""
seed_db.py - Consolidated, Production-Grade Database Seeder for SahakarSeva.

Fully covers all 22 active tables in the clean SahakarSeva cooperative gig service schema:
  - Multi-tenant Cooperative Societies (Chembur, Kurla-Govandi, Ghatkopar, ContractorFlow)
  - All User Roles (publisher, admin, worker, customer)
  - Cooperative Artisans with full Statutory Tiering (Master Artisan, Skilled Craftsman, Apprentice)
  - Social Security & Welfare Fund (Suraksha Nidhi, PMJJBY, PMSBY, ESIC)
  - Service Requests across complete lifecycle (Pending, Claimed, Travelling, In Progress, Completed, Emergency)
  - 88/8/4 Fair Wage Split Payments & Welfare Micro-Ledger Transactions
  - Worker Attendance with GPS & QR Verification
  - Worker Trade Certifications & Task Checklists
  - AI Analytics (Estimates, Delay Predictions, Trade Material Depletion Forecasts)
  - Governance & Communications (Unified Multi-Tier Support & Apex Disputes, System Announcements,
    Notifications, Activity Logs, Login Histories, System Governance Settings, Contractor Documents)

Purges and removes the 13 obsolete construction/SaaS tables:
  subscription_payments, worker_leave_requests, worker_timesheets, worker_safety_reports,
  worker_expense_claims, project_expenses, equipment_assignments, equipment, project_materials,
  materials, platform_settings, dispute_tickets, messages.

Usage:
  python seed_db.py              # Safe run-once (skips if already fully seeded)
  python seed_db.py --clean      # Force purge + reseed all 22 active tables
  python seed_db.py --force      # Same as --clean
"""

import os
import sys
import json
import mysql.connector
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from flask import Flask

# ── MySQL Legacy Compatibility Monkey-Patch ────────────────────────────────────
from sqlalchemy.dialects.mysql.base import MySQLDialect

_orig_get_isolation = MySQLDialect.get_isolation_level
def _patched_get_isolation(self, dbapi_connection):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT @@tx_isolation")
        row = cursor.fetchone()
    except Exception:
        cursor.close()
        return _orig_get_isolation(self, dbapi_connection)
    val = row[0]
    cursor.close()
    if isinstance(val, bytes):
        val = val.decode()
    return val.upper().replace("-", " ")
MySQLDialect.get_isolation_level = _patched_get_isolation

_orig_fetch_setting = MySQLDialect._fetch_setting
def _patched_fetch_setting(self, connection, setting_name):
    try:
        return _orig_fetch_setting(self, connection, setting_name)
    except Exception:
        sql = "SHOW VARIABLES LIKE '%s'" % setting_name
        show_var = connection.exec_driver_sql(sql)
        row = self._compat_first(show_var, charset=self._connection_charset)
        if not row:
            return None
        return row[1]
MySQLDialect._fetch_setting = _patched_fetch_setting

# ── Step 1: Ensure MySQL Database Exists ───────────────────────────────────────
from config import Config
from database import db

try:
    print("[Seeder] Connecting to MySQL server to check/create database...")
    _conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        charset="utf8"
    )
    _cur = _conn.cursor()
    _cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` "
        "CHARACTER SET utf8 COLLATE utf8_unicode_ci"
    )
    _cur.close()
    _conn.close()
    print(f"[Seeder] MySQL database verified/created: {Config.MYSQL_DATABASE}")
except Exception as _e:
    print(f"[Seeder] Fatal: cannot reach MySQL — {_e}")
    raise SystemExit(1)

# ── Step 2: Boot Flask App Context ─────────────────────────────────────────────
app = Flask(__name__)
os.makedirs(app.instance_path, exist_ok=True)
app.config.from_object(Config)
db.init_app(app)

force_clean = (
    any(arg in sys.argv for arg in ["--clean", "--force", "--reset"]) or
    os.environ.get("RESEED_DB") == "true"
)


def seed():
    with app.app_context():
        # Import the 22 active models
        from models.user import User
        from models.contractor import Contractor, ContractorReview
        from models.worker import Worker
        from models.customer import Customer
        from models.attendance import Attendance
        from models.finance import Payment, WelfareTransaction
        from models.communication import (
            Notification, SupportTicket, ActivityLog, LoginHistory,
            SystemSettings, SystemAnnouncement, PlatformSetting
        )
        from models.service_request import ServiceRequest
        from models.quotation import Quotation
        from models.ai_data import AIEstimate, AIDelayPrediction, AIMaterialForecast
        from models.document import ContractorDocument
        from models.worker_features import WorkerTaskChecklist, WorkerCertification

        # ── Step 3: Purge Dropped 13 Tables from MySQL Schema ────────────────────
        print("[Seeder] Ensuring obsolete construction/SaaS tables are dropped...")
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.session.execute(db.text("""
            DROP TABLE IF EXISTS 
                `subscription_payments`,
                `worker_leave_requests`,
                `worker_timesheets`,
                `worker_safety_reports`,
                `worker_expense_claims`,
                `project_expenses`,
                `equipment_assignments`,
                `equipment`,
                `project_materials`,
                `materials`,
                `platform_settings`,
                `dispute_tickets`,
                `messages`,
                `ai_material_forecasts`;
        """))
        db.session.commit()
        print("[Seeder] 13 obsolete tables dropped.")

        # ── Step 4: Create/Verify Schema for the 22 Active Tables ───────────────
        print("[Seeder] Creating/verifying database schema for 22 active cooperative tables...")
        db.create_all()
        print("[Seeder] Database schema is ready.")

        # ── Step 5: Idempotency Guard ──────────────────────────────────────────
        if not force_clean:
            user_count = User.query.count()
            sr_count = ServiceRequest.query.count()
            flag = SystemSettings.query.filter_by(key="demo_seeded").first()
            if flag and flag.value == "true" and user_count >= 10 and sr_count >= 5:
                print(f"[INFO] Database already populated ({user_count} users, {sr_count} service requests). Skipping seed.")
                print("       Use 'python seed_db.py --clean' to force complete reseed.")
                return

        # ── Step 6: Clean Active Tables for Fresh Seed ──────────────────────────
        print("[Seeder] Purging existing records for fresh complete seed...")
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0;"))
        active_tables_to_purge = [
            WorkerTaskChecklist, WorkerCertification, ContractorDocument,
            AIMaterialForecast, AIDelayPrediction, AIEstimate, Quotation,
            WelfareTransaction, Payment, Attendance, ServiceRequest,
            LoginHistory, ActivityLog, SupportTicket, Notification,
            SystemAnnouncement, ContractorReview, Worker, Customer,
            Contractor, User, SystemSettings
        ]
        for tbl in active_tables_to_purge:
            try:
                db.session.query(tbl).delete()
            except Exception:
                pass
        db.session.commit()
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1;"))
        print("[Seeder] Clean purge complete. Inserting perfect comprehensive sample data...")

        # Disable FK checks during bulk seed to allow deterministic IDs
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0;"))

        now = datetime.utcnow()
        today = date.today()

        # ══════════════════════════════════════════════════════════════════════════
        # 1. SYSTEM SETTINGS (Unified System & Governance Configuration)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 1/22: Seeding System Governance & Operational Settings...")
        sys_settings = {
            "company_name": "SahakarSeva Cooperative Gig Federation (Mumbai Central)",
            "company_email": "support@sahakarseva.coop",
            "company_phone": "+91 (022) 2522-9100",
            "company_address": "Sahakar Bhavan, Chembur Naka, Chembur, Mumbai, MH 400071",
            "business_hours": "07:00 - 21:00 (Emergency 24x7)",
            "tax_rate": "18.00",
            "language": "en",
            "currency": "Rs.",
            "theme": "light",
            "email_smtp_host": "smtp.sahakarseva.coop",
            "email_smtp_port": "587",
            "email_sender": "alerts@sahakarseva.coop",
            "sms_provider": "CDAC-Gov-SMS",
            "sms_api_key": "sahakar_sms_live_key_99182",
            "demo_seeded": "true",
            "demo_data_seeded": "true",
            "statutory_min_hourly_wage": "275.00",
            "emergency_dispatch_window_mins": "15",
            # Smart India Hackathon 2026 Problem Statement 26089 Alignment
            "sih_problem_id": "26089",
            "sih_problem_title": "Cooperative Gig Services Platform for Household & Community Services",
            "sih_organization": "Ministry of Cooperation",
            "sih_department": "National Council for Cooperative Training (NCCT)",
            "sih_category": "Software",
            "sih_theme": "Agriculture, FoodTech & Rural Development",
            # Unified Platform Governance Keys
            "maintenance_mode": "false",
            "global_banner": "SahakarSeva: Certified Labour Cooperatives for Trusted Household & Community Gig Services",
            "service_region": "Mumbai Eastern Suburbs (Kurla - Chembur - Govandi - Ghatkopar)",
            "welfare_cess_percentage": "4.0",
            "worker_fair_wage_percentage": "88.0",
            "society_admin_fee_percentage": "8.0",
            "minimum_hourly_rate": "250.00",
            "kyc_mandatory": "true",
            "instant_dispatch_radius_km": "7.5",
            "lockout_workers": "false",
            "lockout_customers": "false",
            "lockout_contractors": "false"
        }
        for k, v in sys_settings.items():
            db.session.add(SystemSettings(key=k, value=v))
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 2. USERS (Publisher, Admins, Workers, Customers)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 2/22: Seeding Platform Users (All 4 Cooperative Roles)...")
        users_data = [
            # 1: Publisher (Apex Federation Super Admin)
            (1, "publisher", "federation.admin@sahakarseva.coop", "publisher123", "publisher",
             "+91-9820010001", "Apex State Labour Cooperative Federation, Mumbai Central, Mumbai - 400008",
             "/static/uploads/profiles/publisher.jpg", False, None, '{"nav_collapsed":false,"default_tab":"governance"}'),
            
            # 2: Chembur Society Admin
            (2, "admin", "admin@chemburseva.coop", "admin123", "admin",
             "+91-9820012345", "Plot 14, Cooperative Bhavan, Chembur Naka, Chembur, Mumbai - 400071",
             "/static/uploads/profiles/chembur_admin.jpg", False, None, '{"dashboard_view":"compact","auto_refresh":true}'),

            # 3: Kurla Society Admin
            (3, "kurla_admin", "admin@kurlashramik.coop", "admin123", "admin",
             "+91-9820054321", "Shramik Seva Kendra, Building 24, Nehru Nagar, Kurla East, Mumbai - 400024",
             "/static/uploads/profiles/kurla_admin.jpg", False, None, '{"dashboard_view":"full"}'),

            # 4: Ghatkopar Society Admin
            (4, "ghatkopar_admin", "admin@ghatkoparcoop.in", "admin123", "admin",
             "+91-9820078901", "Amrut Nagar Sahakari Complex, LBS Marg, Ghatkopar West, Mumbai - 400086",
             "/static/uploads/profiles/ghatkopar_admin.jpg", False, None, '{"dashboard_view":"compact"}'),

            # 5: ContractorFlow Private Admin (Pending Onboarding)
            (5, "contractorflow_admin", "contact@contractorflow.in", "admin123", "admin",
             "+91-9820098765", "Suite 401, Trade Center, Dadar West, Mumbai - 400028",
             "/static/uploads/profiles/flow_admin.jpg", False, None, '{}'),

            # 6: Apex Federation Auditor
            (6, "apex_auditor", "audit@sahakarseva.coop", "auditor123", "publisher",
             "+91-9820010099", "Directorate of Cooperative Audit, New Administrative Building, Mumbai - 400032",
             "/static/uploads/profiles/auditor.jpg", False, None, '{"view":"compliance"}'),

            # 7-16: Cooperative Workers (Artisans)
            (7, "jdoe", "john.doe@chemburseva.coop", "worker123", "worker",
             "+91-9820091001", "Room 12, Sahakar Vasahat, Tilak Nagar, Chembur, Mumbai - 400089",
             "/static/uploads/profiles/worker_jdoe.jpg", False, None, '{"shift":"morning"}'),
            
            (8, "savitri", "savitri.kamble@chemburseva.coop", "worker123", "worker",
             "+91-9820091002", "B-204, Shramik Chawl, Govandi East, Mumbai - 400043",
             "/static/uploads/profiles/worker_savitri.jpg", False, None, '{"shift":"morning"}'),

            (9, "jsmith", "john.smith@chemburseva.coop", "worker123", "worker",
             "+91-9820091003", "Plot 45, Labour Camp, Ghatkopar West, Mumbai - 400086",
             "/static/uploads/profiles/worker_jsmith.jpg", False, None, '{"shift":"general"}'),

            (10, "ramesh", "ramesh.shinde@kurlashramik.coop", "worker123", "worker",
             "+91-9820091004", "Building 18, Kamgar Nagar, Kurla East, Mumbai - 400024",
             "/static/uploads/profiles/worker_ramesh.jpg", False, None, '{"shift":"morning"}'),

            (11, "ganesh", "ganesh.jadhav@kurlashramik.coop", "worker123", "worker",
             "+91-9820091005", "102, Shramik Seva Society, Qureshi Nagar, Kurla East, Mumbai - 400024",
             "/static/uploads/profiles/worker_ganesh.jpg", False, None, '{"shift":"evening"}'),

            (12, "prakash", "prakash.more@ghatkoparcoop.in", "worker123", "worker",
             "+91-9820091006", "304, Sahyadri Chawl, Bhatwadi, Ghatkopar West, Mumbai - 400084",
             "/static/uploads/profiles/worker_prakash.jpg", False, None, '{"shift":"morning"}'),

            (13, "anand", "anand.kadam@chemburseva.coop", "worker123", "worker",
             "+91-9820091007", "D-11, Subhash Nagar, Chembur, Mumbai - 400071",
             "/static/uploads/profiles/worker_anand.jpg", False, None, '{"shift":"general"}'),

            (14, "meena", "meena.gaikwad@chemburseva.coop", "worker123", "worker",
             "+91-9820091008", "Room 8, Indira Nagar Zopadpatti, Chembur East, Mumbai - 400074",
             "/static/uploads/profiles/worker_meena.jpg", False, None, '{"shift":"morning"}'),

            (15, "sunil", "sunil.jadhav@chemburseva.coop", "worker123", "worker",
             "+91-9820091009", "C-3, Siddharth Colony, Chembur, Mumbai - 400071",
             "/static/uploads/profiles/worker_sunil.jpg", False, None, '{"shift":"morning"}'),

            (16, "vikram", "vikram.sawant@kurlashramik.coop", "worker123", "worker",
             "+91-9820091010", "Room 401, Ekta CHS, Chunabhatti, Kurla East, Mumbai - 400022",
             "/static/uploads/profiles/worker_vikram.jpg", False, None, '{"shift":"morning"}'),

            # 17-21: Customers (Households & Housing Societies)
            (17, "anita_deshmukh", "anita.deshmukh@gmail.com", "customer123", "customer",
             "+91-9820033001", "Flat 402, Neelkanth Valley, Ghatkopar East, Mumbai - 400077",
             "/static/uploads/profiles/cust_anita.jpg", False, None, '{}'),

            (18, "rahul_sharma", "rahul.sharma@outlook.com", "customer123", "customer",
             "+91-9820033002", "B-1201, Diamond Garden Heights, Central Avenue, Chembur, Mumbai - 400071",
             "/static/uploads/profiles/cust_rahul.jpg", False, None, '{}'),

            (19, "deonar_heights_chs", "secretary@deonarheights.org", "customer123", "customer",
             "+91-9820033003", "Deonar Heights Co-op Housing Society Ltd., Deonar Farm Road, Deonar, Mumbai - 400088",
             "/static/uploads/profiles/cust_deonar.jpg", False, None, '{"is_bulk_buyer":true}'),

            (20, "priya_nair", "priya.nair@tcs.com", "customer123", "customer",
             "+91-9820033004", "Flat 603, Green Acres CHS, Tilak Nagar, Chembur, Mumbai - 400089",
             "/static/uploads/profiles/cust_priya.jpg", False, None, '{}'),

            (21, "vikas_patil", "vikas.patil@rediffmail.com", "customer123", "customer",
             "+91-9820033005", "Office 301, Commercial Arcade, LBS Marg, Kurla West, Mumbai - 400070",
             "/static/uploads/profiles/cust_vikas.jpg", False, None, '{}')
        ]

        for uid, uname, uemail, upass, urole, uph, uaddr, uprof, is_arch, lock_until, upref in users_data:
            u = User(
                id=uid, username=uname, email=uemail, role=urole,
                phone=uph, address=uaddr, profile_pic=uprof,
                is_archived=is_arch,
                dashboard_config=upref, created_at=now - timedelta(days=120)
            )
            u.set_password(upass)
            db.session.add(u)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 3. CONTRACTORS (Primary Labour Cooperative Societies)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 3/22: Seeding Primary Labour Cooperative Societies...")
        contractors_data = [
            # 1: Chembur Labour Cooperative
            (1, 2, "Chembur Labour Cooperative Society Ltd.",
             "/static/uploads/contractors/chembur_logo.png",
             "REG-BOM-LABOUR-1982-0042", "Multi-Trade Cooperative",
             "Premier multi-trade labour cooperative registered in 1982. Providing certified electrical, plumbing, carpentry, and masonry artisans across Eastern Mumbai.",
             "Chembur, Govandi, Deonar, Tilak Nagar", "https://chemburseva.coop", 1982,
             "MAH/BOM/COOP/1982/042", "Maharashtra Apex Labour Cooperative Federation",
             "+91-9820012345", "admin@chemburseva.coop",
             "Plot 14, Cooperative Bhavan, Chembur Naka, Chembur, Mumbai - 400071",
             "07:00 - 21:00", "approved", True, True, 342, Decimal("4.88"), 342),

            # 2: Kurla-Govandi Shramik Sahakari Sanstha
            (2, 3, "Kurla-Govandi Shramik Sahakari Sanstha Maryadit",
             "/static/uploads/contractors/kurla_logo.png",
             "REG-BOM-SHRAMIK-1994-0118", "Civil & Structural Cooperative",
             "Affiliated labour cooperative federation unit specialized in civil works, fabrication, pipefitting, and emergency household repairs with 120+ registered artisans.",
             "Kurla, Chunabhatti, Nehru Nagar, Qureshi Nagar", "https://kurlashramik.coop", 1994,
             "MAH/BOM/COOP/1994/118", "Maharashtra Apex Labour Cooperative Federation",
             "+91-9820054321", "admin@kurlashramik.coop",
             "Shramik Seva Kendra, Building 24, Nehru Nagar, Kurla East, Mumbai - 400024",
             "07:30 - 20:30", "approved", True, True, 215, Decimal("4.79"), 215),

            # 3: ContractorFlow Private Services
            (3, 5, "ContractorFlow Facilities Pvt. Ltd.",
             "/static/uploads/contractors/flow_logo.png",
             "U74999MH2021PTC368910", "Facilities Engineering Enterprise",
             "Private facilities engineering enterprise integrating with SahakarSeva under cooperative joint venture framework for specialized HVAC and industrial refrigeration.",
             "Dadar, Lower Parel, Prabhadevi", "https://contractorflow.in", 2021,
             "PVT-JV-2021-368", "Maharashtra Apex Labour Cooperative Federation",
             "+91-9820098765", "contact@contractorflow.in",
             "Suite 401, Trade Center, Dadar West, Mumbai - 400028",
             "09:00 - 18:00", "pending_approval", True, False, 18, Decimal("4.60"), 18),

            # 4: Ghatkopar Sahakari Mazdoor Society
            (4, 4, "Ghatkopar Sahakari Mazdoor Sangh Maryadit",
             "/static/uploads/contractors/ghatkopar_logo.png",
             "REG-BOM-MAZDOOR-2001-0309", "Home & Commercial Maintenance Cooperative",
             "Community cooperative with dedicated women artisan collectives specializing in house painting, deep cleaning, domestic maintenance, and pest barrier application.",
             "Ghatkopar, Vidyavihar, Pant Nagar, Amrut Nagar", "https://ghatkoparcoop.in", 2001,
             "MAH/BOM/COOP/2001/309", "Maharashtra Apex Labour Cooperative Federation",
             "+91-9820078901", "admin@ghatkoparcoop.in",
             "Amrut Nagar Sahakari Complex, LBS Marg, Ghatkopar West, Mumbai - 400086",
             "08:00 - 20:00", "approved", True, True, 189, Decimal("4.91"), 189)
        ]

        for cid, uid, cname, clogo, lno, btype, cdesc, sareas, web, eyear, creg, fedname, cph, cem, oaddr, bhours, ostatus, iactive, iverif, comp_proj, avgrat, totrev in contractors_data:
            c = Contractor(
                id=cid, user_id=uid, company_name=cname, company_logo=clogo,
                license_number=lno, business_type=btype, description=cdesc,
                service_areas=sareas, website=web, established_year=eyear,
                cooperative_reg_no=creg, federation_name=fedname,
                contact_phone=cph, contact_email=cem, office_address=oaddr,
                business_hours=bhours, onboarding_status=ostatus,
                is_active=iactive, is_verified=iverif,
                total_projects_completed=comp_proj, average_rating=avgrat,
                total_reviews=totrev
            )
            db.session.add(c)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 4. CUSTOMERS
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 4/22: Seeding Household & Institutional Customers...")
        customers_data = [
            (17, "Anita Deshmukh Residence", "Flat 402, Neelkanth Valley, Ghatkopar East, Mumbai - 400077", "Ashok Deshmukh (+91-9820033091)"),
            (18, "Rahul Sharma Household", "B-1201, Diamond Garden Heights, Central Avenue, Chembur, Mumbai - 400071", "Sunita Sharma (+91-9820033092)"),
            (19, "Deonar Heights Co-op Housing Society Ltd.", "Deonar Heights CHS, Deonar Farm Road, Deonar, Mumbai - 400088", "CHS Security Office (+91-9820033093)"),
            (20, "Priya Nair Apartment", "Flat 603, Green Acres CHS, Tilak Nagar, Chembur, Mumbai - 400089", "Rajesh Nair (+91-9820033094)"),
            (21, "Vikas Patil Enterprises", "Office 301, Commercial Arcade, LBS Marg, Kurla West, Mumbai - 400070", "Estate Manager (+91-9820033095)")
        ]

        for cust_id, ccomp, cbill, cemrg in customers_data:
            cust = Customer(
                id=cust_id, is_archived=False, company_name=ccomp,
                billing_address=cbill, emergency_contact=cemrg
            )
            db.session.add(cust)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 5. WORKERS (Cooperative Artisans with Statutory Social Security)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 5/22: Seeding Cooperative Artisans with Social Security & Tiers...")
        workers_data = [
            (7, 1, "Master Electrical Wireman, High-Voltage Panel DB Maintenance, Inverter Overhaul",
             12, Decimal("650.00"), Decimal("4.95"), "available", True, "approved",
             "/static/uploads/ids/jdoe_aadhaar.pdf", "Sunita Doe (Wife) +91-9820091091",
             "Union Bank of India, Chembur Br, A/C: 382901928401, IFSC: UBIN0538299",
             "/static/uploads/docs/jdoe_certs.zip", "Master Artisan",
             Decimal("19.06200000"), Decimal("72.89900000"),
             "The New India Assurance Co. Ltd.", "NIA-MUM-COOP-2026-00124", today + timedelta(days=280),
             Decimal("500000.00"), True, "WF-CHEMBUR-2026-007", 3240.00,
             "PMJJBY-LIC-2026-781920", "Active", today + timedelta(days=240),
             "PMSBY-NIC-2026-441829", "Active", today + timedelta(days=240), "3100984521"),

            (8, 1, "Carpentry, Teak Wood Cabinetry, Locksmithing, Door Alignment, Modular Kitchens",
             8, Decimal("550.00"), Decimal("4.85"), "busy", True, "approved",
             "/static/uploads/ids/savitri_aadhaar.pdf", "Mahadev Kamble (Husband) +91-9820091092",
             "State Bank of India, Govandi Br, A/C: 20192840192, IFSC: SBIN0001053",
             "/static/uploads/docs/savitri_certs.zip", "Master Artisan",
             Decimal("19.05500000"), Decimal("72.90500000"),
             "National Insurance Company Ltd.", "NIC-MUM-COOP-2026-00561", today + timedelta(days=190),
             Decimal("500000.00"), True, "WF-CHEMBUR-2026-008", 2860.00,
             "PMJJBY-LIC-2026-781921", "Active", today + timedelta(days=180),
             "PMSBY-NIC-2026-441830", "Active", today + timedelta(days=180), "3100984522"),

            (9, 1, "Plumbing & Sanitaryware, Concealed Piping, Booster Pumps, Water Tank Sanitation",
             10, Decimal("600.00"), Decimal("4.90"), "available", True, "approved",
             "/static/uploads/ids/jsmith_aadhaar.pdf", "Pooja Smith (Wife) +91-9820091093",
             "Bank of Baroda, Chembur Br, A/C: 049281029481, IFSC: BARB0CHEMBU",
             "/static/uploads/docs/jsmith_certs.zip", "Master Artisan",
             Decimal("19.06400000"), Decimal("72.89700000"),
             "The New India Assurance Co. Ltd.", "NIA-MUM-COOP-2026-00125", today + timedelta(days=310),
             Decimal("500000.00"), True, "WF-CHEMBUR-2026-009", 2580.00,
             "PMJJBY-LIC-2026-781922", "Active", today + timedelta(days=260),
             "PMSBY-NIC-2026-441831", "Active", today + timedelta(days=260), "3100984523"),

            (10, 2, "Masonry, Waterproofing, Concrete Repair, Plastering, Anti-Seepage Chemical Injections",
             15, Decimal("600.00"), Decimal("4.80"), "available", True, "approved",
             "/static/uploads/ids/ramesh_aadhaar.pdf", "Lata Shinde (Wife) +91-9820091094",
             "Maharashtra State Co-op Bank, Kurla Br, A/C: 11029481029, IFSC: MSCB0000014",
             "/static/uploads/docs/ramesh_certs.zip", "Master Artisan",
             Decimal("19.06900000"), Decimal("72.88000000"),
             "United India Insurance Co.", "UII-MUM-COOP-2026-00812", today + timedelta(days=150),
             Decimal("500000.00"), True, "WF-KURLA-2026-010", 3890.00,
             "PMJJBY-LIC-2026-781923", "Active", today + timedelta(days=120),
             "PMSBY-NIC-2026-441832", "Active", today + timedelta(days=120), "3100984524"),

            (11, 2, "Civil Tiling, Marble Laying, Terrace Waterproofing, Grouting",
             6, Decimal("500.00"), Decimal("4.75"), "available", True, "approved",
             "/static/uploads/ids/ganesh_aadhaar.pdf", "Sarika Jadhav (Wife) +91-9820091095",
             "Canara Bank, Kurla Br, A/C: 294810294810, IFSC: CNRB0002948",
             "/static/uploads/docs/ganesh_certs.zip", "Skilled Craftsman",
             Decimal("19.07100000"), Decimal("72.88500000"),
             "United India Insurance Co.", "UII-MUM-COOP-2026-00813", today + timedelta(days=150),
             Decimal("300000.00"), True, "WF-KURLA-2026-011", 1740.00,
             "PMJJBY-LIC-2026-781924", "Active", today + timedelta(days=120),
             "PMSBY-NIC-2026-441833", "Active", today + timedelta(days=120), "3100984525"),

            (12, 4, "Appliance Repair, Inverter AC Gas Filling, Washing Machine PCB Diagnosis",
             7, Decimal("550.00"), Decimal("4.88"), "busy", True, "approved",
             "/static/uploads/ids/prakash_aadhaar.pdf", "Rekha More (Wife) +91-9820091096",
             "Punjab National Bank, Ghatkopar Br, A/C: 092810294810, IFSC: PUNB0092800",
             "/static/uploads/docs/prakash_certs.zip", "Skilled Craftsman",
             Decimal("19.08500000"), Decimal("72.90800000"),
             "Oriental Insurance Company Ltd.", "OIC-MUM-COOP-2026-00339", today + timedelta(days=220),
             Decimal("300000.00"), True, "WF-GHATKOPAR-2026-012", 2150.00,
             "PMJJBY-LIC-2026-781925", "Active", today + timedelta(days=190),
             "PMSBY-NIC-2026-441834", "Active", today + timedelta(days=190), "3100984526"),

            (13, 1, "Interior & Exterior Painting, Texture Finishes, Damp Wall Polymer Plaster",
             5, Decimal("450.00"), Decimal("4.78"), "available", True, "approved",
             "/static/uploads/ids/anand_aadhaar.pdf", "Shobha Kadam (Mother) +91-9820091097",
             "Union Bank of India, Chembur Br, A/C: 382901928405, IFSC: UBIN0538299",
             "/static/uploads/docs/anand_certs.zip", "Skilled Craftsman",
             Decimal("19.05800000"), Decimal("72.89500000"),
             "The New India Assurance Co. Ltd.", "NIA-MUM-COOP-2026-00126", today + timedelta(days=310),
             Decimal("300000.00"), True, "WF-CHEMBUR-2026-013", 1420.00,
             "PMJJBY-LIC-2026-781926", "Active", today + timedelta(days=260),
             "PMSBY-NIC-2026-441835", "Active", today + timedelta(days=260), "3100984527"),

            (14, 1, "Domestic Helper & Housekeeping, Deep House Cleaning, Sanitation, Floor Scrubbing",
             3, Decimal("400.00"), Decimal("4.93"), "available", True, "approved",
             "/static/uploads/ids/meena_aadhaar.pdf", "Prakash Gaikwad (Husband) +91-9820091098",
             "Bank of India, Chembur Br, A/C: 00192840192, IFSC: BKID0000019",
             "/static/uploads/docs/meena_certs.zip", "Skilled Craftsman",
             Decimal("19.05400000"), Decimal("72.89900000"),
             "National Insurance Company Ltd.", "NIC-MUM-COOP-2026-00928", today + timedelta(days=210),
             Decimal("300000.00"), True, "WF-CHEMBUR-2026-014", 1280.00,
             "PMJJBY-LIC-2026-781927", "Active", today + timedelta(days=150),
             "PMSBY-NIC-2026-441836", "Active", today + timedelta(days=150), "3100984528"),

            (15, 1, "Gardener & Caregiver Assistant, Horticulture, Lawn Maintenance, Trainee Plumbing",
             1, Decimal("350.00"), Decimal("4.70"), "pending_verification", False, "pending",
             "/static/uploads/ids/sunil_aadhaar.pdf", "Vasant Jadhav (Father) +91-9820091099",
             "State Bank of India, Chembur Br, A/C: 30192840192, IFSC: SBIN0000301",
             None, "Apprentice",
             Decimal("19.06000000"), Decimal("72.89600000"),
             "The New India Assurance Co. Ltd.", "NIA-PENDING-2026", today + timedelta(days=90),
             Decimal("200000.00"), True, "WF-CHEMBUR-2026-015", 350.00,
             "PMJJBY-PENDING", "Pending", today + timedelta(days=60),
             "PMSBY-PENDING", "Pending", today + timedelta(days=60), "3100984529"),

            (16, 2, "Verified Commercial Driver, Transport Logistics, ARC & TIG Welding Fabrication",
             9, Decimal("700.00"), Decimal("4.94"), "available", True, "approved",
             "/static/uploads/ids/vikram_aadhaar.pdf", "Suvarna Sawant (Wife) +91-9820091000",
             "IDBI Bank, Kurla Br, A/C: 01928401920, IFSC: IBKL0000192",
             "/static/uploads/docs/vikram_certs.zip", "Master Artisan",
             Decimal("19.07300000"), Decimal("72.88100000"),
             "United India Insurance Co.", "UII-MUM-COOP-2026-00820", today + timedelta(days=270),
             Decimal("500000.00"), True, "WF-KURLA-2026-016", 2980.00,
             "PMJJBY-LIC-2026-781928", "Active", today + timedelta(days=230),
             "PMSBY-NIC-2026-441837", "Active", today + timedelta(days=230), "3100984530")
        ]

        for wid, cid, sk, exp, sal, pr, as_, iv, vs, idp, ec, bk, dp, tr, lat, lng, iprov, ipol, ival, icov, cwf, wfid, wbal, pmj_id, pmj_st, pmj_ren, pms_id, pms_st, pms_ren, esic in workers_data:
            w = Worker(
                id=wid, is_archived=False, contractor_id=cid, skills=sk,
                experience_years=exp, salary_rate=sal, performance_rating=pr,
                availability_status=as_, is_verified=iv, verification_status=vs,
                id_proof_file=idp, emergency_contact=ec, bank_details=bk,
                documents_paths=dp, tier=tr, tier_updated_at=now - timedelta(days=30),
                gps_lat=lat, gps_lng=lng, gps_last_updated=now - timedelta(minutes=15),
                insurance_provider=iprov, insurance_policy_no=ipol,
                insurance_valid_until=ival, insurance_coverage_amount=icov,
                coop_welfare_fund_enrolled=cwf, welfare_fund_id=wfid, welfare_balance=wbal,
                pmjjby_id=pmj_id, pmjjby_status=pmj_st, pmjjby_renewal_date=pmj_ren,
                pmsby_id=pms_id, pmsby_status=pms_st, pmsby_renewal_date=pms_ren,
                esic_ip_number=esic
            )
            db.session.add(w)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 6. SERVICE REQUESTS (Cooperative Gig Workflow Across Full Lifecycle)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 6/22: Seeding Service Requests with Lifecycles & 1-Click Dispatch...")
        service_requests_data = [
            # 1: Completed Electrical Overhaul (Anita Deshmukh)
            (1, "SR-2026-00101", 1, 17, "Anita Deshmukh", "+91-9820033001", "Electrical",
             "Complete DB Box Overhaul & Master Circuit Breaker Tripping Resolution",
             "Main switchboard sparking on heavy appliance load. Requires full load rebalancing, replacement of burnt 32A MCB, and insulation testing across 4 circuit lines.",
             "/static/uploads/voice/req_101.wav", "/static/uploads/requests/db_box_burnt.jpg",
             "Flat 402, Neelkanth Valley, Ghatkopar East, Mumbai - 400077",
             Decimal("19.07700000"), Decimal("72.90800000"), "Completed",
             7, today - timedelta(days=5), Decimal("4850.00"), "Urgent",
             False, "Standard", Decimal("4850.00"), "Claimed", 5.0, now - timedelta(days=5, hours=4), now - timedelta(days=5, hours=3),
             "4829", True, now - timedelta(days=5, hours=3, minutes=45), "10:00 AM - 01:00 PM", 100,
             "/static/uploads/videos/db_box_test.mp4", "1x Havells 16A MCB, 15m Polycab FR 2.5 wire, PVC insulation tape",
             Decimal("3.50"), now - timedelta(days=5, hours=1),
             "/static/uploads/completions/db_box_done.jpg",
             "Replaced burnt MCB with genuine Havells 16A unit. Neutral loop corrected. Tested on 4kW heating load with Fluke meter. Megger insulation resistance > 100 Megaohms.",
             "/static/uploads/voice/comp_101.wav", 5,
             "Exceptional cooperative service! John arrived promptly with safety gear and resolved the dangerous sparking in less than 3 hours. Transparent rates!",
             None, "Paid", now - timedelta(days=6)),

            # 2: Completed Pump Maintenance (Deonar Heights CHS)
            (2, "SR-2026-00102", 1, 19, "Deonar Heights Co-op Housing Society Ltd.", "+91-9820033003", "Plumbing",
             "Society Underground Booster Pump Overhaul & Non-Return Valve Replacement",
             "Overhead distribution pump vibrating excessively with low discharge pressure to 7th floor wings. Needs bearing replacement and 2-inch NRV inspection.",
             "/static/uploads/voice/req_102.wav", "/static/uploads/requests/pump_leak.jpg",
             "Deonar Heights CHS, Deonar Farm Road, Deonar, Mumbai - 400088",
             Decimal("19.05200000"), Decimal("72.91500000"), "Completed",
             9, today - timedelta(days=3), Decimal("8600.00"), "Normal",
             False, "Standard", Decimal("8600.00"), "Claimed", 8.0, now - timedelta(days=3, hours=6), now - timedelta(days=3, hours=5),
             "7712", True, now - timedelta(days=3, hours=5, minutes=10), "09:00 AM - 02:00 PM", 100,
             "/static/uploads/videos/pump_pressure_test.mp4", "2x SKF Ball Bearings, 1x Leader 1-inch Brass Ball Valve, Teflon gland packing",
             Decimal("5.00"), now - timedelta(days=3, hours=1),
             "/static/uploads/completions/pump_overhaul_done.jpg",
             "Replaced degraded bearings and installed new Leader brass valve. Discharge pressure restored to 4.2 Bar across all terrace risers.",
             "/static/uploads/voice/comp_102.wav", 5,
             "Extremely reliable cooperative execution. Society committee appreciated the detailed bill of materials and digital warranty.",
             None, "Paid", now - timedelta(days=4)),

            # 3: In Progress Carpentry Service (Rahul Sharma)
            (3, "SR-2026-00103", 1, 18, "Rahul Sharma", "+91-9820033002", "Carpentry",
             "Teak Wood Main Entrance Door Alignment & Godrej High-Security Lock Fitting",
             "Main entrance door rubbing against marble floor due to hinge sag. Customer requested installation of multi-bolt smart biometric lock and weather seal strip.",
             "/static/uploads/voice/req_103.wav", "/static/uploads/requests/door_hinge.jpg",
             "B-1201, Diamond Garden Heights, Central Avenue, Chembur, Mumbai - 400071",
             Decimal("19.06100000"), Decimal("72.89950000"), "In Progress",
             8, today, Decimal("3200.00"), "Normal",
             False, "Standard", Decimal("3200.00"), "Claimed", 5.0, now - timedelta(hours=3), now - timedelta(hours=2),
             "9143", True, now - timedelta(hours=1, minutes=45), "11:00 AM - 03:00 PM", 65,
             None, "Heavy duty brass ball-bearing hinges, 4-inch screws",
             Decimal("2.25"), None, None, None, None, None, None, None, "Pending", now - timedelta(days=1)),

            # 4: Travelling / En Route Service (Priya Nair)
            (4, "SR-2026-00104", 1, 20, "Priya Nair", "+91-9820033004", "Appliance",
             "Split Air Conditioner Cooling Coil Gas Leakage Diagnosis & Refilling",
             "Daikin 1.5 Ton inverter AC blowing warm air. Gas pressure drop suspected in outdoor unit flared copper joints.",
             "/static/uploads/voice/req_104.wav", "/static/uploads/requests/ac_leak.jpg",
             "Flat 603, Green Acres CHS, Tilak Nagar, Chembur, Mumbai - 400089",
             Decimal("19.06300000"), Decimal("72.89450000"), "Travelling",
             12, today, Decimal("2600.00"), "Normal",
             False, "Standard", Decimal("2600.00"), "Claimed", 6.0, now - timedelta(minutes=45), now - timedelta(minutes=15),
             "3891", False, None, "02:00 PM - 04:00 PM", 25,
             None, "R32 Refrigerant canister, Nitrogen testing kit",
             Decimal("0.50"), None, None, None, None, None, None, None, "Pending", now - timedelta(hours=3)),

            # 5: Worker Assigned / Scheduled (Vikas Patil)
            (5, "SR-2026-00105", 2, 21, "Vikas Patil Enterprises", "+91-9820033005", "Civil",
             "Commercial Office Restroom Anti-Skid Tile Laying & Concealed Grouting",
             "Restroom floor tile renovation across 180 sq ft area. Epoxy grouting required to prevent floor seepage into lower server room.",
             "/static/uploads/voice/req_105.wav", "/static/uploads/requests/office_tiles.jpg",
             "Office 301, Commercial Arcade, LBS Marg, Kurla West, Mumbai - 400070",
             Decimal("19.06700000"), Decimal("72.87800000"), "Assigned",
             11, today + timedelta(days=1), Decimal("14500.00"), "Normal",
             False, "Standard", Decimal("14500.00"), "Claimed", 10.0, now - timedelta(hours=6), now - timedelta(hours=5),
             "6152", False, None, "Tomorrow 09:00 AM", 10,
             None, "Kajaria 300x300 anti-skid tiles, Laticrete epoxy grout",
             Decimal("0.00"), None, None, None, None, None, None, None, "Pending", now - timedelta(hours=8)),

            # 6: Emergency 1-Click Dispatch (Broadcasting — Anita Deshmukh)
            (6, "SR-2026-00106", 1, 17, "Anita Deshmukh", "+91-9820033001", "Plumbing",
             "EMERGENCY: Burst Main Kitchen Angle Cock Flooding Apartment",
             "High pressure hot water line burst behind sink cabinet. Water cascading into living room. Immediate isolation and angle cock replacement required!",
             "/static/uploads/voice/req_106.wav", "/static/uploads/requests/emergency_leak.jpg",
             "Flat 402, Neelkanth Valley, Ghatkopar East, Mumbai - 400077",
             Decimal("19.07700000"), Decimal("72.90800000"), "Pending",
             None, today, Decimal("1200.00"), "Emergency",
             True, "Critical", Decimal("1200.00"), "Broadcasting", 7.5, None, now + timedelta(minutes=45),
             "5521", False, None, "Immediate Emergency Dispatch", 0,
             None, "1/2 inch brass angle cock, Teflon tape, heavy pipe wrench",
             Decimal("0.00"), None, None, None, None, None, None, None, "Pending", now - timedelta(minutes=10)),

            # 7: Completed Metal Fabrication with Rework Comments (Deonar Heights CHS)
            (7, "SR-2026-00107", 2, 19, "Deonar Heights Co-op Housing Society Ltd.", "+91-9820033003", "Fabrication",
             "Security Gate Heavy Duty Hinges Re-Welding & Anti-Rust Polyurethane Coating",
             "Main entrance compound swing gate sagged due to fractured bottom pivot pin. Needs heavy steel plate gusset reinforcement and ARC welding.",
             "/static/uploads/voice/req_107.wav", "/static/uploads/requests/gate_broken.jpg",
             "Deonar Heights CHS, Deonar Farm Road, Deonar, Mumbai - 400088",
             Decimal("19.05200000"), Decimal("72.91500000"), "Completed",
             16, today - timedelta(days=8), Decimal("11200.00"), "Urgent",
             False, "Standard", Decimal("11200.00"), "Claimed", 8.0, now - timedelta(days=8, hours=8), now - timedelta(days=8, hours=7),
             "8902", True, now - timedelta(days=8, hours=7, minutes=30), "08:30 AM - 05:00 PM", 100,
             "/static/uploads/videos/gate_welding.mp4", "10mm MS Plate gussets, E6013 welding electrodes, 2L Red Oxide primer",
             Decimal("6.50"), now - timedelta(days=8, hours=1),
             "/static/uploads/completions/gate_finished.jpg",
             "Fabricated new heavy-duty pivot bracket, double-pass welded joints, and applied dual coats of zinc chromate primer and black enamel paint.",
             "/static/uploads/voice/comp_107.wav", 4,
             "Strong welding work. Needed slight touch up on inner latch paint which worker completed without hassle.",
             "Touch-up coat on latch bolt applied on 2nd inspection.", "Paid", now - timedelta(days=9)),

            # 8: Pending Quotation Review (Rahul Sharma)
            (8, "SR-2026-00108", 1, 18, "Rahul Sharma", "+91-9820033002", "Painting",
             "Interior Hall & Dining Waterproof Coating with 2-Tone Royale Luxury Finish",
             "Wall seepage near window sill caused blistering of paint. Full scraping, polymer putty touch-up, and 2 coats of Asian Paints Royale required.",
             "/static/uploads/voice/req_108.wav", "/static/uploads/requests/wall_peel.jpg",
             "B-1201, Diamond Garden Heights, Central Avenue, Chembur, Mumbai - 400071",
             Decimal("19.06100000"), Decimal("72.89950000"), "Pending",
             None, today + timedelta(days=2), Decimal("18500.00"), "Normal",
             False, "Standard", None, "None", 5.0, None, None,
             "1289", False, None, "Next Monday 10:00 AM", 0,
             None, "Asian Paints Damp Sheath, TruCare wall putty, 20L Royale Luxury emulsion",
             Decimal("0.00"), None, None, None, None, None, None, None, "Pending", now - timedelta(days=2))
        ]

        for srid, req_id, cid, cust_id, cname, cmob, cat, title, desc, vpath, photos, addr, lat, lng, stat, wid, vdate, ecost, prio, is_em, em_sev, frate, bstat, drad, cl_at, b_exp, otp_val, otp_ver, arr_at, ptime, prog, comp_vids, mat_used, twrk, cdate, cphotos, cnotes, cvoice, rat, rcomm, rew_comm, pstat, cr_at in service_requests_data:
            sr = ServiceRequest(
                id=srid, is_archived=False, request_id=req_id, contractor_id=cid,
                customer_id=cust_id, customer_name=cname, mobile_number=cmob,
                category=cat, title=title, description=desc, voice_path=vpath,
                photos=photos, address=addr, latitude=lat, longitude=lng,
                status=stat, assigned_worker_id=wid, visit_date=vdate,
                estimated_cost=ecost, priority=prio, is_emergency=is_em,
                emergency_severity=em_sev, fixed_rate=frate, broadcast_status=bstat,
                dispatch_radius_km=drad, claimed_at=cl_at, broadcast_expires_at=b_exp,
                otp=otp_val, otp_verified=otp_ver, arrived_at=arr_at,
                preferred_time=ptime, progress=prog, completion_videos=comp_vids,
                materials_used=mat_used, time_worked=twrk, completion_date=cdate,
                completion_photos=cphotos, completion_notes=cnotes,
                completion_voice_path=cvoice, rating=rat, review_comment=rcomm,
                rework_comments=rew_comm, payment_status=pstat, created_at=cr_at
            )
            db.session.add(sr)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 7. QUOTATIONS
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 7/22: Seeding Itemized Gig Quotations...")
        quotations_data = [
            (1, "QT-2026-00101", 1,
             json.dumps([
                 {"name": "Havells 16A MCB Single Pole", "qty": 1, "rate": 185.00, "total": 185.00},
                 {"name": "Polycab FR 2.5 sq mm Wire", "qty": 15, "rate": 28.00, "total": 420.00},
                 {"name": "PVC Insulation & Consumables", "qty": 1, "rate": 150.00, "total": 150.00}
             ]),
             Decimal("3500.00"), Decimal("250.00"), Decimal("572.00"), Decimal("200.00"),
             Decimal("4850.00"), "Standard 6-month cooperative service warranty against electrical arcing.",
             today + timedelta(days=30), "Approved", now - timedelta(days=6)),

            (2, "QT-2026-00102", 2,
             json.dumps([
                 {"name": "SKF Industrial Deep Groove Ball Bearings", "qty": 2, "rate": 850.00, "total": 1700.00},
                 {"name": "Leader 1-inch Brass Ball Valve", "qty": 1, "rate": 495.00, "total": 495.00},
                 {"name": "Mechanical Seal & Gland Gaskets", "qty": 1, "rate": 650.00, "total": 650.00}
             ]),
             Decimal("4800.00"), Decimal("500.00"), Decimal("1242.00"), Decimal("500.00"),
             Decimal("8600.00"), "Includes 1-year cooperative guarantee on booster pump alignment.",
             today + timedelta(days=30), "Approved", now - timedelta(days=4)),

            (3, "QT-2026-00108", 8,
             json.dumps([
                 {"name": "Asian Paints Damp Sheath Polymer Primer", "qty": 10, "rate": 420.00, "total": 4200.00},
                 {"name": "TruCare Acrylic Wall Putty (40kg)", "qty": 2, "rate": 950.00, "total": 1900.00},
                 {"name": "Asian Paints Royale Luxury Emulsion (20L)", "qty": 1, "rate": 5800.00, "total": 5800.00}
             ]),
             Decimal("5500.00"), Decimal("300.00"), Decimal("2050.00"), Decimal("1000.00"),
             Decimal("18500.00"), "Includes 3-year warranty against dampness and peeling on prepared surface.",
             today + timedelta(days=15), "Pending", now - timedelta(days=1))
        ]
        for qid, qnum, srid, mlist, lcost, eqcost, gst_val, disc, gtotal, t_c, vdate, qstat, cr_at in quotations_data:
            q = Quotation(
                id=qid, is_archived=False, quotation_number=qnum, service_request_id=srid,
                material_list=mlist, labour_cost=lcost, equipment_charges=eqcost,
                gst=gst_val, discount=disc, grand_total=gtotal, terms_conditions=t_c,
                validity_date=vdate, status=qstat, created_at=cr_at
            )
            db.session.add(q)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 8. ATTENDANCE LOGS (With GPS & QR Code Verification)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 8/22: Seeding Attendance Logs with GPS & QR Verification...")
        attendance_data = [
            (1, 7, 1, today - timedelta(days=5),
             datetime.combine(today - timedelta(days=5), time(9, 58)),
             datetime.combine(today - timedelta(days=5), time(13, 30)),
             "Present", Decimal("19.07700000"), Decimal("72.90800000"),
             Decimal("19.07702000"), Decimal("72.90801000"), True, True),

            (2, 9, 2, today - timedelta(days=3),
             datetime.combine(today - timedelta(days=3), time(8, 55)),
             datetime.combine(today - timedelta(days=3), time(14, 0)),
             "Present", Decimal("19.05200000"), Decimal("72.91500000"),
             Decimal("19.05201000"), Decimal("72.91502000"), True, True),

            (3, 8, 3, today,
             datetime.combine(today, time(10, 52)),
             None, "Present", Decimal("19.06100000"), Decimal("72.89950000"),
             None, None, True, True),

            (4, 16, 7, today - timedelta(days=8),
             datetime.combine(today - timedelta(days=8), time(8, 25)),
             datetime.combine(today - timedelta(days=8), time(15, 0)),
             "Present", Decimal("19.05200000"), Decimal("72.91500000"),
             Decimal("19.05201000"), Decimal("72.91501000"), True, True),

            (5, 10, None, today - timedelta(days=1),
             datetime.combine(today - timedelta(days=1), time(9, 10)),
             datetime.combine(today - timedelta(days=1), time(17, 30)),
             "Present", Decimal("19.06880000"), Decimal("72.87970000"),
             Decimal("19.06880000"), Decimal("72.87970000"), True, False),

            (6, 11, None, today - timedelta(days=2),
             datetime.combine(today - timedelta(days=2), time(8, 45)),
             datetime.combine(today - timedelta(days=2), time(17, 0)),
             "Present", Decimal("19.07120000"), Decimal("72.88500000"),
             Decimal("19.07120000"), Decimal("72.88500000"), True, False)
        ]
        for aid, wid, srid, adate, cin, cout, astat, cin_lat, cin_lng, cout_lat, cout_lng, v_gps, v_qr in attendance_data:
            att = Attendance(
                id=aid, is_archived=False, worker_id=wid, service_request_id=srid,
                project_id=srid, date=adate, check_in_time=cin, check_out_time=cout,
                status=astat, check_in_lat=cin_lat, check_in_lng=cin_lng,
                check_out_lat=cout_lat, check_out_lng=cout_lng,
                verified_by_gps=v_gps, verified_by_qr=v_qr
            )
            db.session.add(att)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 9. PAYMENTS (88/8/4 Cooperative Fair Wage Split & Audit Trail)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 9/22: Seeding Payments with 88% Worker / 8% Society / 4% Welfare Cess...")
        payments_data = [
            # 1: SR-2026-00101 Electrical Payment
            (1, "revenue", Decimal("4850.00"), today - timedelta(days=5), "Paid",
             1, 17, 7, 1, "INV-2026-00101",
             "Payment for DB Box Overhaul & Master Circuit Breaker Tripping Resolution (SR-2026-00101)",
             "/static/uploads/receipts/rec_101.pdf", True, "/static/uploads/signatures/sig_anita.png",
             "QT-2026-00101", Decimal("200.00"), Decimal("572.00"), Decimal("3500.00"), Decimal("755.00"),
             Decimal("4268.00"), Decimal("388.00"), Decimal("0.00"), Decimal("194.00")),

            # 2: SR-2026-00102 Pump Overhaul Payment
            (2, "revenue", Decimal("8600.00"), today - timedelta(days=3), "Paid",
             1, 19, 9, 2, "INV-2026-00102",
             "Payment for Society Underground Booster Pump Overhaul (SR-2026-00102)",
             "/static/uploads/receipts/rec_102.pdf", True, "/static/uploads/signatures/sig_deonar.png",
             "QT-2026-00102", Decimal("500.00"), Decimal("1242.00"), Decimal("4800.00"), Decimal("2845.00"),
             Decimal("7568.00"), Decimal("688.00"), Decimal("0.00"), Decimal("344.00")),

            # 3: SR-2026-00107 Security Gate Fabrication
            (3, "revenue", Decimal("11200.00"), today - timedelta(days=8), "Paid",
             2, 19, 16, 7, "INV-2026-00107",
             "Payment for Security Gate Heavy Duty Welding & PU Coating (SR-2026-00107)",
             "/static/uploads/receipts/rec_107.pdf", True, "/static/uploads/signatures/sig_deonar.png",
             None, Decimal("0.00"), Decimal("1708.00"), Decimal("6500.00"), Decimal("3000.00"),
             Decimal("9856.00"), Decimal("896.00"), Decimal("0.00"), Decimal("448.00")),

            # 4: Worker Advance Salary / Living Wage Disbursement (88% Reconciled Fair Wage Settlement)
            (4, "salary", Decimal("11836.00"), today - timedelta(days=15), "Paid",
             1, None, 7, None, "SAL-2026-001",
             "Bi-weekly Guaranteed Fair Wage Settlement for John Doe",
             "/static/uploads/receipts/sal_jdoe.pdf", False, None,
             None, Decimal("0.00"), Decimal("0.00"), Decimal("11836.00"), Decimal("0.00"),
             Decimal("11836.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00"))
        ]

        for pid, ptype, pamt, pdate, pstat, cid, cust_id, wid, srid, inv_no, desc, rec_path, s_cust, sig_path, qno, disc, gst_val, lcost, mcost, wpayout, soc_fee, fed_fee, wcess in payments_data:
            pay = Payment(
                id=pid, is_archived=False, type=ptype, amount=pamt, date=pdate,
                status=pstat, contractor_id=cid, customer_id=cust_id, worker_id=wid,
                project_id=srid, service_request_id=srid, invoice_number=inv_no,
                description=desc, receipt_path=rec_path, signed_by_customer=s_cust,
                signature_path=sig_path, quotation_number=qno, discount=disc,
                gst=gst_val, labour_cost=lcost, material_cost=mcost,
                worker_payout=wpayout, society_admin_fee=soc_fee,
                federation_fee=fed_fee, welfare_cess=wcess
            )
            db.session.add(pay)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 10. WELFARE TRANSACTIONS (Suraksha Nidhi Fund Audit Ledger)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 10/22: Seeding Suraksha Nidhi Welfare Fund Micro-Ledger...")
        welfare_data = [
            (1, 7, 1, 1, "CESS_CREDIT", 194.00, 3240.00, "Suraksha Nidhi 4% Welfare Allocation from Invoice #INV-2026-00101", "INV-2026-00101", now - timedelta(days=5)),
            (2, 9, 2, 2, "CESS_CREDIT", 344.00, 2580.00, "Suraksha Nidhi 4% Welfare Allocation from Invoice #INV-2026-00102", "INV-2026-00102", now - timedelta(days=3)),
            (3, 16, 3, 7, "CESS_CREDIT", 448.00, 2980.00, "Suraksha Nidhi 4% Welfare Allocation from Invoice #INV-2026-00107", "INV-2026-00107", now - timedelta(days=8)),
            (4, 7, None, None, "PMSBY_PREMIUM", -20.00, 3046.00, "Automated Annual Premium Debit: Pradhan Mantri Suraksha Bima Yojana", "PMSBY-NIC-2026-441829", now - timedelta(days=40)),
            (5, 7, None, None, "PMJJBY_PREMIUM", -436.00, 3066.00, "Automated Annual Premium Debit: Pradhan Mantri Jeevan Jyoti Bima Yojana", "PMJJBY-LIC-2026-781920", now - timedelta(days=40)),
            (6, 8, None, None, "WELFARE_GRANT", 2500.00, 2860.00, "Cooperative Artisan Child Merit Education Scholarship Grant", "COOP-EDU-GRANT-2026-01", now - timedelta(days=25))
        ]
        for wtid, wid, payid, srid, ttype, wamt, bafter, wdesc, ref_id, cr_at in welfare_data:
            wt = WelfareTransaction(
                id=wtid, worker_id=wid, payment_id=payid, service_request_id=srid,
                transaction_type=ttype, amount=wamt, balance_after=bafter,
                description=wdesc, reference_id=ref_id, created_at=cr_at
            )
            db.session.add(wt)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 11. CONTRACTOR REVIEWS
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 11/22: Seeding Verified Cooperative Society Reviews...")
        reviews_data = [
            (1, 1, 17, 1, 1, 5, "Exemplary Cooperative Electrical Service",
             "John from Chembur Cooperative was professional, equipped with calibrated Fluke meters, and fixed our dangerous sparking circuit with full transparency.", True, now - timedelta(days=5)),
            (2, 1, 19, 2, 2, 5, "Flawless Booster Pump Overhaul for CHS",
             "Overhead pressure across our 7th floor wings is completely restored. Impressed by the cooperative ethos and lack of hidden charges.", True, now - timedelta(days=3)),
            (3, 2, 19, 7, 7, 5, "Robust Compound Gate Welding",
             "The Kurla cooperative welder reinforced the pivot hinge with heavy gussets. Sturdy and well finished.", True, now - timedelta(days=7))
        ]
        for rid, cid, cust_id, srid, pid, rating, title, rtext, is_app, cr_at in reviews_data:
            cr = ContractorReview(
                id=rid, contractor_id=cid, customer_id=cust_id, service_request_id=srid,
                project_id=pid, rating=rating, title=title, review_text=rtext,
                is_approved=is_app, created_at=cr_at
            )
            db.session.add(cr)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 12. CONTRACTOR DOCUMENTS (Centralized Regulatory Vault)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 12/22: Seeding Cooperative Regulatory & Compliance Documents...")
        documents_data = [
            (1, 1, None, 1, "State Cooperative Registration Certificate", "Site Permit",
             "/static/uploads/vault/chembur_coop_registration.pdf", "1.4 MB",
             "Official registration under Maharashtra Cooperative Societies Act 1960", today + timedelta(days=730), now - timedelta(days=100)),
            (2, 1, 7, 1, "Class-A Government Electrical Contractor License", "Worker License",
             "/static/uploads/vault/jdoe_electrical_license_a.pdf", "850 KB",
             "Certified for high voltage up to 33kV installations by Maharashtra PWD", today + timedelta(days=365), now - timedelta(days=90)),
            (3, 1, None, None, "Federation Comprehensive Public Liability Insurance", "Insurance Policy",
             "/static/uploads/vault/chembur_public_liability_2026.pdf", "2.1 MB",
             "Rs. 2.5 Crore coverage for residential and commercial site liabilities", today + timedelta(days=280), now - timedelta(days=85)),
            (4, 2, None, 2, "Kurla-Govandi Cooperative State Registration Bye-Laws", "Contract",
             "/static/uploads/vault/kurla_bye_laws_2026.pdf", "3.2 MB",
             "Approved Labour Cooperative Bye-laws ratified by District Registrar", today + timedelta(days=1000), now - timedelta(days=95))
        ]
        for did, cid, wid, srid, title, cat, fpath, fsize, notes, exp_date, up_at in documents_data:
            cdoc = ContractorDocument(
                id=did, contractor_id=cid, worker_id=wid, project_id=srid,
                service_request_id=srid, title=title, category=cat, file_path=fpath,
                file_size=fsize, notes=notes, expiry_date=exp_date, uploaded_at=up_at
            )
            db.session.add(cdoc)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 13. WORKER CERTIFICATIONS (Statutory Verification)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 13/22: Seeding Worker Trade Certifications & NCVT/ITI Licenses...")
        certs_data = [
            (1, 7, "National Trade Certificate (NTC) - Electrician", "NCVT / Directorate General of Training, Govt of India",
             "NTC-ELE-MH-2017-9102", "/static/uploads/certs/jdoe_ntc.pdf", today - timedelta(days=3200), None, "Verified",
             "Verified against NCVT MIS portal roll number database.", now - timedelta(days=60)),
            (2, 8, "NSDC Level 4 Master Carpenter Trade Certificate", "National Skill Development Corporation (NSDC)",
             "NSDC-CARP-2020-4102", "/static/uploads/certs/savitri_nsdc.pdf", today - timedelta(days=2100), None, "Verified",
             "Verified through Skill India Digital portal QR verification.", now - timedelta(days=50)),
            (3, 9, "NABET Master Certified Pipefitter & Sanitary Inspector", "National Accreditation Board for Education & Training",
             "NABET-PLB-2018-7712", "/static/uploads/certs/jsmith_nabet.pdf", today - timedelta(days=2800), None, "Verified",
             "Original trade certificate verified by Chembur Cooperative Committee.", now - timedelta(days=55)),
            (4, 16, "Government Industrial Training Institute (ITI) ARC Welder", "ITI Kurla, Directorate of Vocational Education, Govt of MH",
             "ITI-WLD-KURLA-2016", "/static/uploads/certs/vikram_iti.pdf", today - timedelta(days=3500), None, "Verified",
             "Verified with Govt ITI Kurla institutional records.", now - timedelta(days=45))
        ]
        for cert_id, wid, title, ibody, cnum, dfile, idate, edate, stat, anotes, cr_at in certs_data:
            wc = WorkerCertification(
                id=cert_id, worker_id=wid, cert_title=title, issuing_body=ibody,
                cert_number=cnum, document_file=dfile, issue_date=idate,
                expiry_date=edate, status=stat, admin_notes=anotes, created_at=cr_at
            )
            db.session.add(wc)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 14. WORKER TASK CHECKLISTS (SOP Safety & Verification)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 14/22: Seeding Worker SOP Task Checklists...")
        checklists_data = [
            (1, 1, 1, 1, 7, "Isolate Main Incoming Power Supply & Tag Out", "Ensure zero voltage using Fluke tester before handling panel wires", True, now - timedelta(days=5, hours=3)),
            (2, 1, 1, 1, 7, "Inspect Busbar & Remove Burnt 32A MCB", "Carefully unclip melted breaker and check DIN rail for oxidation", True, now - timedelta(days=5, hours=2, minutes=30)),
            (3, 1, 1, 1, 7, "Install Genuine Havells 16A MCB & Re-torque Terminals", "Torque terminal screws to manufacturer specification (2.5 Nm)", True, now - timedelta(days=5, hours=1, minutes=45)),
            (4, 1, 1, 1, 7, "Perform Insulation & Megger Earth Leakage Test", "Verify insulation resistance exceeds 100M Ohm to ensure safety", True, now - timedelta(days=5, hours=1)),
            (5, 1, 3, 3, 8, "Measure Door Clearance & Unhinge Leaf", "Mark rubbing zones on bottom edge and plane evenly", True, now - timedelta(hours=2)),
            (6, 1, 3, 3, 8, "Mortise Pocket for High-Security Smart Lock", "Chisel precise pocket and install heavy brass strike plate", False, None)
        ]
        for chkid, cid, srid, pid, wid, tname, tdesc, is_comp, comp_at in checklists_data:
            wtc = WorkerTaskChecklist(
                id=chkid, contractor_id=cid, service_request_id=srid, project_id=pid,
                worker_id=wid, task_name=tname, description=tdesc,
                is_completed=is_comp, completed_at=comp_at
            )
            db.session.add(wtc)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 15. AI ESTIMATES
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 15/22: Seeding AI Cost & Completion Estimates...")
        ai_estimates_data = [
            (1, 1, "Electrical", Decimal("1200.00"), 3, "Burnt MCB and Load Imbalance", "Urgent",
             Decimal("755.00"), Decimal("3500.00"), Decimal("4255.00"), "3.5 hours", Decimal("96.50")),
            (2, 2, "Plumbing", Decimal("4500.00"), 12, "Pump Bearing Seizure & Flow Restriction", "Normal",
             Decimal("2845.00"), Decimal("4800.00"), Decimal("7645.00"), "5.0 hours", Decimal("94.20")),
            (3, 3, "Carpentry", Decimal("950.00"), 2, "Door Sag & Smart Lock Fitting", "Normal",
             Decimal("650.00"), Decimal("2400.00"), Decimal("3050.00"), "4.0 hours", Decimal("92.80")),
            (4, 8, "Painting", Decimal("1800.00"), 4, "Monsoon Dampness & Flaking Paint", "Normal",
             Decimal("11900.00"), Decimal("5500.00"), Decimal("17400.00"), "24.0 hours", Decimal("91.40"))
        ]
        for aid, srid, stype, hsize, nrooms, ptype, urg, mcost, lcost, tcost, ctime, cscore in ai_estimates_data:
            ae = AIEstimate(
                id=aid, service_request_id=srid, service_type=stype,
                house_size=hsize, num_rooms=nrooms, problem_type=ptype,
                urgency=urg, est_material_cost=mcost, est_labour_cost=lcost,
                est_total_cost=tcost, est_completion_time=ctime,
                confidence_score=cscore
            )
            db.session.add(ae)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 16. AI DELAY PREDICTIONS
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 16/22: Seeding AI Risk & Delay Analytics...")
        delay_data = [
            (1, 1, 1, "Low", Decimal("0.00"), 0,
             "All required genuine MCB units in stock at Chembur hub. No transit delay predicted.",
             "Standard dispatch procedure maintained.", now - timedelta(days=6)),
            (2, 8, 8, "Medium", Decimal("35.00"), 2,
             "Monsoon precipitation humidity level > 85% in Mumbai suburbs may prolong wall putty curing time.",
             "Utilize rapid-curing polymer damp-proofing coat before primer application.", now - timedelta(days=1)),
            (3, 5, 5, "Low", Decimal("5.00"), 0,
             "Tile consignment arriving on schedule via Kurla logistics depot.",
             "Commence surface hacking in parallel with logistics arrival.", now - timedelta(hours=6))
        ]
        for did, srid, pid, rlevel, dperc, edays, rsn, sactions, cr_at in delay_data:
            adp = AIDelayPrediction(
                id=did, service_request_id=srid, project_id=pid, risk_level=rlevel,
                delay_percentage=dperc, expected_delay_days=edays, reason=rsn,
                suggested_actions=sactions, created_at=cr_at
            )
            db.session.add(adp)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 17. AI MATERIAL FORECASTS (Decoupled Trade Category Forecasts)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 17/22: Seeding AI Trade Material Depletion Forecasts...")
        forecast_data = [
            (1, "Electrical", "Flame Retardant Copper Wire (2.5 sq mm)", 8, Decimal("25.00"), "Polycab India Depot, Chembur (+91-9820044001)", "Medium", now - timedelta(days=2)),
            (2, "Painting", "Exterior Weatherguard Emulsion Drums (20L)", 4, Decimal("15.00"), "Asian Paints Colour World, Chembur (+91-9820044004)", "Critical", now - timedelta(days=1)),
            (3, "Masonry", "High Performance Portland Pozzolana Cement", 6, Decimal("50.00"), "UltraTech Depot, Kurla West (+91-9820044006)", "Medium", now - timedelta(days=3))
        ]
        for fid, tcat, mname, drem, rec_qty, srec, alevel, cr_at in forecast_data:
            amf = AIMaterialForecast(
                id=fid, trade_category=tcat, material_name=mname, days_remaining=drem,
                recommended_purchase_qty=rec_qty, supplier_recommendation=srec,
                alert_level=alevel, created_at=cr_at
            )
            db.session.add(amf)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 18. SUPPORT TICKETS (Unified Support & Apex Conciliation / Disputes)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 18/22: Seeding Multi-Tier Support Tickets & Apex Arbitrations...")
        support_tickets_data = [
            # Standard Society & Apex Support Inquiries
            (1, False, 17, "Query regarding GST invoice breakdown for housing society audit",
             "Please issue a formal digitally stamped GST tax invoice copy for SR-2026-00101 to submit to our housing society auditor.",
             "Resolved", "Medium", now - timedelta(days=4), now - timedelta(days=3),
             "society", "society", False, 1, "Chembur Labour Cooperative Society Ltd.",
             "Official digitally signed invoice #INV-2026-00101 emailed to anita.deshmukh@gmail.com.", "Resolved by Society Admin"),

            (2, False, 19, "Request for Apex Federation Verification of Cooperative Bye-laws",
             "Housing society management committee requests certified copy of Maharashtra State Federation bye-law affiliation.",
             "Resolved", "Low", now - timedelta(days=10), now - timedelta(days=8),
             "apex", "apex", False, 1, "Chembur Labour Cooperative Society Ltd.",
             "Federation affiliation certificate MH-FED-2026 provided via document vault.", "Verified by Apex Federation"),

            (3, False, 21, "Expedited commercial site safety clearance request",
             "Commercial complex management requires worker insurance certificate (PMJJBY/PMSBY/ESIC) before site entry tomorrow morning.",
             "In Progress", "High", now - timedelta(hours=6), now - timedelta(hours=2),
             "society", "society", False, 2, "Kurla-Govandi Shramik Sahakari Sanstha",
             "Compiling ESIC IP numbers and PMJJBY policy certificates for worker Ganesh Shinde.", "Processing Certificate Dispatch"),

            # Escalated Apex Disputes (Consolidated from dispute_tickets)
            (4, False, 19, "Dispute over inner latch spray finish and paint overspray",
             "Customer noted that overspray from the compound gate primer reached the adjacent boundary flower bed and the inner latch bolt was slightly stiff.",
             "Resolved", "High", now - timedelta(days=7), now - timedelta(days=6),
             "apex", "apex", True, 2, "Kurla-Govandi Shramik Sahakari Sanstha Maryadit",
             "Arbitrated by Apex State Federation Super Admin. Contractor agreed to apply secondary gloss coat and clean flower bed edging.", "Resolved in Customer Favor"),

            (5, False, 18, "Quotation clarification on dampness treatment chemical brands",
             "Customer requested confirmation that Dr Fixit / Asian Paints certified polymer primer is being used instead of standard white cement.",
             "Open", "Medium", now - timedelta(days=1), now - timedelta(days=1),
             "apex", "apex", True, 1, "Chembur Labour Cooperative Society Ltd.",
             "Under review by Society Chief Engineer. Brand specification sheet shared with customer.", "Arbitration Underway")
        ]
        for stid, is_arch, cust_id, title, desc, stat, prio, cr_at, up_at, ttier, esc_lvl, is_apex, cid, cname, rnotes, arb_act in support_tickets_data:
            st = SupportTicket(
                id=stid, is_archived=is_arch, customer_id=cust_id, title=title,
                description=desc, status=stat, priority=prio, created_at=cr_at,
                updated_at=up_at, target_tier=ttier, escalation_level=esc_lvl,
                is_apex_dispute=is_apex, contractor_id=cid, contractor_name=cname,
                resolution_notes=rnotes, arbitration_action=arb_act
            )
            db.session.add(st)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 19. SYSTEM ANNOUNCEMENTS
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 19/22: Seeding Federation System Announcements...")
        announcements_data = [
            (1, "Statutory Monsoon Safety Protocols for all Cooperative Electrical Artisans",
             "All primary societies and artisans must strictly adhere to Indian Standard IS 732:2019 during heavy rainfall. Ensure double earthing and use CAT-IV rated insulated gloves at all outdoor installations.",
             "worker", True, now - timedelta(days=15), 1),
            (2, "State Cooperative Federation Annual General Body Meeting (AGM) Notice",
             "The 28th Annual General Body Meeting of all accredited Primary Labour Cooperatives will convene at Sahakar Bhavan, Mumbai Central on 15th October 2026. Review of Suraksha Nidhi allocations on agenda.",
             "admin", True, now - timedelta(days=10), 1),
            (3, "Subsidized Festive Home Maintenance Services for Cooperative Housing Societies",
             "Cooperative housing societies across Chembur, Kurla, and Ghatkopar can now book certified pre-monsoon plumbing and electrical maintenance at pre-fixed cooperative tariffs.",
             "customer", True, now - timedelta(days=5), 1)
        ]
        for aid, title, content, trole, is_act, cr_at, cb_id in announcements_data:
            sa = SystemAnnouncement(
                id=aid, title=title, content=content, target_role=trole,
                is_active=is_act, created_at=cr_at, created_by_id=cb_id
            )
            db.session.add(sa)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 20. NOTIFICATIONS
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 20/22: Seeding Multi-Role Notifications...")
        notifications_data = [
            (1, False, 17, "Service Request Completed", "Your DB Box overhaul (SR-2026-00101) has been certified complete by Master Artisan John Doe. Please provide your review.", True, now - timedelta(days=5, hours=1), "Success", "Normal"),
            (2, False, 7, "Suraksha Nidhi Fund Credit", "Rs. 194.00 (4% statutory welfare cess) credited to your Suraksha Nidhi Social Security Account from job #SR-2026-00101.", True, now - timedelta(days=5), "Success", "High"),
            (3, False, 2, "Emergency Job Dispatched", "Emergency request #SR-2026-00106 broadcasted in Ghatkopar East radius. 3 workers alerted.", False, now - timedelta(minutes=10), "Alert", "Emergency"),
            (4, False, 1, "New Contractor Application", "ContractorFlow Ltd. submitted accreditation application. Pending Apex verification.", False, now - timedelta(days=3), "Info", "High"),
            (5, False, 18, "Quotation Ready for Review", "Quotation QT-2026-00108 for your painting service is ready for review.", False, now - timedelta(days=1), "Info", "Normal")
        ]
        for nid, is_arch, uid, title, msg, is_rd, tstamp, ntype, prio in notifications_data:
            notif = Notification(
                id=nid, is_archived=is_arch, user_id=uid, title=title,
                message=msg, is_read=is_rd, timestamp=tstamp,
                type=ntype, priority=prio
            )
            db.session.add(notif)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 21. ACTIVITY LOGS (Enterprise Audit Trail)
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 21/22: Seeding Enterprise Activity Audit Logs...")
        activity_logs_data = [
            (1, 1, "ONBOARD_CONTRACTOR", "Apex Federation approved Chembur Labour Cooperative Society Ltd. with Pro tier.", None, "Approved", "Contractor", 1, now - timedelta(days=120), "127.0.0.1"),
            (2, 2, "DISPATCH_WORKER", "Assigned Master Artisan John Doe to Service Request SR-2026-00101", "Unassigned", "Assigned: jdoe", "ServiceRequest", 1, now - timedelta(days=5, hours=4), "192.168.1.101"),
            (3, 7, "VERIFY_OTP", "Worker John Doe verified Customer OTP 4829 for Service Request SR-2026-00101", "OTP_PENDING", "OTP_VERIFIED", "ServiceRequest", 1, now - timedelta(days=5, hours=3, minutes=45), "192.168.1.55"),
            (4, 17, "PAYMENT_SUCCESS", "Customer Anita Deshmukh settled Rs. 4,850.00 via Razorpay for Invoice INV-2026-00101", "Pending", "Paid", "Payment", 1, now - timedelta(days=5, hours=1), "103.21.124.4"),
            (5, 1, "SURAKSHA_NIDHI_RECONCILE", "Automated welfare engine reconciled 4% Suraksha Nidhi cess ledger for Chembur society.", "Unreconciled", "Reconciled", "WelfareLedger", 1, now - timedelta(days=1), "127.0.0.1")
        ]
        for lid, uid, act, dtls, oval, nval, etype, eid, tstamp, ip in activity_logs_data:
            alog = ActivityLog(
                id=lid, user_id=uid, action=act, details=dtls,
                old_value=oval, new_value=nval, entity_type=etype,
                entity_id=eid, timestamp=tstamp, ip_address=ip
            )
            db.session.add(alog)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # 22. LOGIN HISTORIES
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] 22/22: Seeding User Authentication Histories...")
        login_data = [
            (1, 1, now - timedelta(hours=1), "127.0.0.1", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SahakarSeva/Desktop", "Success"),
            (2, 2, now - timedelta(hours=2), "192.168.1.101", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0", "Success"),
            (3, 7, now - timedelta(hours=3), "192.168.1.55", "Mozilla/5.0 (Linux; Android 14; Mobile) SahakarSevaWorker/2.0", "Success"),
            (4, 17, now - timedelta(days=1), "103.21.124.4", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)", "Success"),
            (5, 3, now - timedelta(days=2), "192.168.1.112", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/128.0", "Success"),
            (6, 18, now - timedelta(hours=5), "103.21.124.8", "Mozilla/5.0 (Linux; Android 14; Pixel 8)", "Success")
        ]
        for lhid, uid, tstamp, ip, uagent, stat in login_data:
            lh = LoginHistory(
                id=lhid, user_id=uid, timestamp=tstamp,
                ip_address=ip, user_agent=uagent, status=stat
            )
            db.session.add(lh)
        db.session.flush()

        # ══════════════════════════════════════════════════════════════════════════
        # FINAL VERIFICATION & COMMIT
        # ══════════════════════════════════════════════════════════════════════════
        print("[Seeder] Finalizing database commit and foreign key verification...")
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.session.commit()
        print("\n" + "=" * 76)
        print("  SahakarSeva Clean Cooperative Database Seeding Completed Successfully!")
        print("=" * 76)
        print("  All 22 Active Tables Populated with High-Fidelity Maharashtra Cooperative Data:")
        print("    - 4 Platform Roles: Publisher (Apex), Admins, Workers, Customers")
        print("    - 4 Primary Cooperatives & Enterprises (Chembur, Kurla, Ghatkopar, ContractorFlow)")
        print("    - 10 Verified Cooperative Artisans with PMJJBY/PMSBY/ESIC Welfare & Skill Tiers")
        print("    - 8 Real-World Service Requests (Pending, Travelling, In Progress, Completed, Emergency)")
        print("    - 88/8/4 Fair Wage Split Payments & Suraksha Nidhi Welfare Micro-Transactions")
        print("    - Worker Attendance with GPS & QR Verification")
        print("    - Worker Trade Certifications & Task Checklists")
        print("    - AI Forecasting, Estimates & Delay Analytics")
        print("    - Unified Multi-Tier Support, Apex Disputes, System Announcements & Enterprise Logs")
        print("=" * 76 + "\n")


if __name__ == "__main__":
    seed()
