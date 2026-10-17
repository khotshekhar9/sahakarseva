# SahakarSeva — Cooperative-Owned Digital Service Marketplace Platform for Household & Community Services

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-MySQL-orange.svg)](https://www.mysql.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Multi--Tenant%20SaaS-purple.svg)]()
[![Multilingual](https://img.shields.io/badge/Language-English%20%7C%20%E0%A4%B9%E0%A4%BF%E0%A4%A8%E0%A5%8D%E0%A4%A6%E0%A5%80%20%7C%20%E0%A4%AE%E0%A4%B0%E0%A4%BE%E0%A4%A0%E0%A5%80-teal.svg)]()

---

## 📌 Background
> Labour Cooperative Federations and Labour Cooperative Societies possess a large pool of skilled workers such as electricians, plumbers, carpenters, painters, domestic helpers, caregivers, drivers, gardeners, cleaners, and technicians. However, they lack a structured digital platform to connect these workers with households and institutions requiring such services. Private platforms currently dominate this market, while cooperative workers often remain underutilized despite having skills and local presence.

---

## 📱 Simple Mobile-First Experience & Dedicated Portals
The platform fulfills all core requirements while presenting a clean, dedicated user journey for each role:
* **Customer Hub**: Dedicated views for **Book Service**, **My Bookings** (with pre-assignment edit support), **Payments**, **Messages**, and **Profile**.
* **Worker Workspace**: Dedicated views for **My Jobs**, **GPS Attendance**, **Earnings**, **Welfare Benefits**, **Messages**, and **Profile**.
* **Cooperative Admin Console**: Management views for **Workers**, **Customers**, **Service Requests**, **Quotations**, **Welfare Ledger**, and **AI Demand Forecasting**.
* **Apex Federation Command**: Oversight for affiliated **Societies**, **KYC Approvals**, **Grievances/Complaints**, **State Circulars**, **Welfare Reserves**, and **Security Audits**.

### Role-Aware Assistant
A built-in **Ask Assistant** is available across portals. It accepts text and browser voice input, guiding users directly to booking, jobs, payments, benefits, and demand forecasting. The assistant features deterministic offline fallbacks so the entire application remains fully functional even without external AI API keys.

### PWA / Mobile-Ready
Engineered as a mobile-first Progressive Web App (PWA) with an installable manifest, touch-friendly targets (29px–32px), safe viewport padding, and persistent bottom drawer navigation. The layout dynamically scales across phones, tablets, laptops, and desktop monitors.

---

## 🎯 Problem Statement
- **Problem Statement ID**: **26089**
- **Problem Statement Title**: **Cooperative Gig Services Platform for Household & Community Services**
- **Organization**: **Ministry of Cooperation**
- **Department**: **National Council for Cooperative Training (NCCT)**
- **Category**: **Software**
- **Theme**: **Agriculture, FoodTech & Rural Development**
- **Description / Objective**:
  > To develop a cooperative-owned digital service marketplace platform that enables Labour Cooperative Federations and Labour Cooperative Societies to provide verified household and community services while ensuring fair wages, worker welfare, and consumer trust.

---

## 🏗️ The Six Core Technology Components

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               SAHAKARSEVA COOPERATIVE PLATFORM                                   │
├──────────────────────────────┬──────────────────────────────┬────────────────────────────────────┤
│ 1. MOBILE APPLICATIONS       │ 2. ARTIFICIAL                │ 3. GEO-SPATIAL                     │
│    • Mobile-First Responsive │    INTELLIGENCE (AI)         │    TECHNOLOGY                      │
│    • 29px/32px Touch Inputs  │    • Google Gemini & Grok    │    • OpenStreetMap Geocoding       │
│    • 2x2 Metric KPI Grids    │    • Smart Worker Match      │    • Haversine Dispatch Proximity  │
│    • Bottom Drawer Navigation│    • Heuristic Cost Estimator│    • GPS Geofenced Attendance      │
│    • PWA Adaptive Layout     │    • Delay & Surge Predict   │    • Live Technician Tracking      │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ 4. DIGITAL PAYMENT           │ 5. CLOUD COMPUTING           │ 6. PROPOSED MODE                   │
│    SYSTEMS                   │    • Multi-Tenant Row Scoping│    SOFTWARE                        │
│    • Central Financial Ledger│    • Decoupled Blueprints    │    • 4-Role Stakeholder Ecosystem  │
│    • Automated 18% GST       │    • Cloud MySQL / MariaDB   │    • 12-Stage Lifecycle Engine     │
│    • HTML5 Canvas Signatures │    • RESTful API Suite       │    • Cryptographic 6-Digit OTP Gate│
│    • 90/4/4/2 Wage & Cess    │    • SocketIO Real-Time Sync │    • PMSBY/PMJJBY/ESIC Suraksha    │
└──────────────────────────────┴──────────────────────────────┴────────────────────────────────────┘
```

### 1. 📱 Mobile Applications
- **Mobile-First Responsive Design System**: Engineered in [`static/css/style.css`](static/css/style.css) with fluid media queries (`@media (max-width: 768px)` and `@media (max-width: 576px)`).
- **Touch-Optimized Form Inputs**: Constrained single-line inputs and select dropdowns to clean 29px (phones) and 32px (tablets) touch targets, eliminating bloated heights and mobile keyboard clipping.
- **Mobile KPI Cards & Auto-Wrap**: 2x2 card grids (`col-6`) on smartphones, collapsible icon sidebar (68px), and bottom drawer interaction.
- **Device Agnostic**: Universal responsive layouts for Android/iOS mobile browsers, tablets, laptops, and wide monitors.

### 2. 🧠 Artificial Intelligence (AI)
Located in [`services/ai_service.py`](services/ai_service.py):
- **Generative LLM Assistance (`AIService.call_external_llm`)**: Optional Google Gemini API (`gemini-2.0-flash`) and Grok API (`grok-beta`) integration for real-time generative cost estimation, scope breakdown, and technical advice with deterministic offline fallback.
- **AI Cost Estimator (`AIService.estimate_service_cost`)**: Heuristic engine analyzing house dimensions, room counts, urgency tiers, and domain keywords to compute itemized labor costs, material estimates, and confidence scores (60%–99%).
- **Smart Worker Recommendation Engine (`AIService.recommend_workers_smart`)**: Multi-factor scoring algorithm balancing NLP trade skill matching, GPS Haversine proximity, concurrent job load, customer ratings, and attendance history.
- **AI Delay & Schedule Risk Prediction (`AIService.predict_project_delay`)**: Evaluates attendance records and milestone progress velocity to forecast project delays.
- **AI Demand Forecasting & Workforce Allocation (`AIService.forecast_gig_service_demand`)**: 7-day rolling trade demand forecasts with automated surge detection across urban zones.

### 3. 🗺️ Geo-Spatial Technology
- **Reverse Geocoding Proxy (`/customer/api/geocode`)**: Resolves latitude/longitude coordinates to human-readable street addresses using OpenStreetMap Nominatim with server-side caching.
- **GIS Proximity-Based Matching**: Computes accurate Haversine and Euclidean distances between customer service addresses and registered worker locations to prioritize nearest available artisans.
- **GPS Geofenced Artisan Attendance (`models/attendance.py`)**: Captures real-time clock-in and clock-out coordinates (`latitude`, `longitude`) to guarantee verified physical presence at job locations.

### 4. 💳 Digital Payment Systems
Located in [`models/finance.py`](models/finance.py), [`routes/customer.py`](routes/customer.py), and [`services/pdf_service.py`](services/pdf_service.py):
- **Centralized Financial Ledger**: Automated revenue, expense, and wage tracking with dynamic **18% GST tax calculation** and discount application.
- **HTML5 Canvas Digital Signatures**: Allows customers to draw binding signatures directly on digital invoices via touch or mouse before payment (`/customer/invoice/sign`).
- **ReportLab PDF Invoicing**: Automated PDF invoice and quotation generator rendering cooperative branding, GST numbers, itemized billing, and payment status stamps.
- **Cooperative 4-Tier Fair Wage & Welfare Split (`services/welfare_service.py` & `AIService.get_fair_wage_breakdown`)**:
  - **90%** Direct Worker Fair Wage Payout (zero private aggregator commissions)
  - **4%** Primary Cooperative Society Operations & Field Toolkits
  - **4%** Apex Federation Platform Support & Governance Fee
  - **2%** Worker Welfare & Social Security Cess (*Suraksha Nidhi* fund automatically funding annual PMSBY ₹20 and PMJJBY ₹436 premiums)

### 5. ☁️ Cloud Computing
- **Multi-Tenant SaaS Topology**: Strict row-level data isolation via `contractor_id` foreign keys, allowing hundreds of independent district labour societies to operate securely on a single cloud database.
- **Modular Microservice Blueprints**: Decoupled Flask Blueprints (`auth`, `admin`, `worker`, `customer`, `publisher`) for horizontal scaling and maintainability.
- **Database**: Uses MySQL / MariaDB as the primary database with automatic table creation, seeding, and legacy `utf8` charset compatibility.
- **Real-Time WebSockets Sync**: Instant dispatch notifications, arrival alerts, and live messaging powered by `Flask-SocketIO`.

### 6. 📦 Proposed Mode Software Architecture
- **Cooperative Paradigm Shift**: Replaces exploitative private aggregators (extracting 25%–35% commission with zero insurance) with a worker-owned cooperative model offering 90% direct pay, mandatory state insurance, and cryptographic arrival gates.
- **4-Role Stakeholder Ecosystem**: Apex Federation (`publisher`), Labour Society (`admin`), Member Artisan (`worker`), Household Client (`customer`).
- **12-Stage Lifecycle State Machine**:
  $$\text{Requested} \rightarrow \text{Assigned} \rightarrow \text{In-Transit} \rightarrow \text{OTP Arrival} \rightarrow \text{In-Progress} \rightarrow \text{Quality Review} \rightarrow \text{Customer Sign-Off} \rightarrow \text{Invoiced} \rightarrow \text{Paid} \rightarrow \text{Completed} \rightarrow \text{Feedback} \rightarrow \text{Archived}$$
- **Cryptographic 6-Digit OTP Gate**: Physical technician verification gate preventing job starts until the customer shares their one-time arrival code.

---

## ✨ Expected Solution Features — Implementation Matrix

| # | Expected Solution Feature | Technical Implementation | Core Files / Endpoints |
|---|---|---|---|
| 1 | **Service Provider Registration and Verification** | 3-step registration wizard for Labour Cooperative Societies with state registration/bye-law uploads, followed by Apex Federation KYC review and approval. | [`templates/register_contractor.html`](templates/register_contractor.html), [`routes/publisher.py`](routes/publisher.py) |
| 2 | **Worker Skill Profiling and Certification** | Comprehensive trade profiling across all 10 trades with certification tracking (`worker_certifications`), trade license numbers, and skill ratings. | [`models/worker.py`](models/worker.py), [`templates/admin/workers.html`](templates/admin/workers.html) |
| 3 | **Customer Booking and Scheduling System** | 3-step client booking wizard with audio voice recording, photo attachments, date/time slot scheduling, emergency flags, and pre-dispatch booking editing. | [`templates/customer/book_service.html`](templates/customer/book_service.html), [`templates/customer/edit_booking.html`](templates/customer/edit_booking.html), [`routes/customer.py`](routes/customer.py) |
| 4 | **Geo-Location Based Service Matching** | OpenStreetMap reverse geocoding proxy combined with Haversine GPS proximity calculations to match nearest verified artisans. | [`routes/customer.py`](routes/customer.py), [`services/ai_service.py`](services/ai_service.py) |
| 5 | **Digital Payments and Invoicing** | Automated 18% GST calculation, HTML5 canvas customer e-signature pad, one-click payment settlement, and ReportLab PDF invoices. | [`models/finance.py`](models/finance.py), [`services/pdf_service.py`](services/pdf_service.py) |
| 6 | **Rating and Feedback Mechanism** | Verified customer 1–5 star reviews and qualitative feedback updating society public ratings and artisan reliability scores. | [`models/contractor.py`](models/contractor.py), [`templates/customer/contractor_detail.html`](templates/customer/contractor_detail.html) |
| 7 | **Worker Welfare and Insurance Integration** | Automated 2% welfare cess allocation (*Suraksha Nidhi*), policy renewal tracking for PMSBY (₹20/yr) and PMJJBY (₹436/yr), and ESIC integration. | [`models/worker.py`](models/worker.py), [`services/welfare_service.py`](services/welfare_service.py), [`templates/worker/benefits.html`](templates/worker/benefits.html) |
| 8 | **Emergency and On-Demand Service Booking** | High-priority emergency dispatches with pre-approved cooperative tariffs, accelerated worker claiming, and a cryptographic 6-digit OTP arrival gate. | [`models/service_request.py`](models/service_request.py), [`services/dispatch_service.py`](services/dispatch_service.py), [`templates/customer/bookings.html`](templates/customer/bookings.html) |
| 9 | **Cooperative Federation Administration Dashboard** | Apex command console monitoring state-wide affiliated district societies, KYC document audits, welfare reserves, and state circular broadcasts. | [`templates/publisher/dashboard.html`](templates/publisher/dashboard.html), [`routes/publisher.py`](routes/publisher.py) |
| 10 | **Multilingual Mobile Application** | Full-page real-time translation powered by Google Translator API proxy (`/api/translate`) with immutable WeakMap loss-free reversibility (English ⇄ Marathi ⇄ Hindi). | [`app.py`](app.py), [`static/js/translations.js`](static/js/translations.js) |
| 11 | **AI-Based Demand Forecasting & Workforce Allocation** | 7-day rolling trade demand forecasts with predictive surge detection and smart artisan gap recommendations. | [`services/ai_service.py`](services/ai_service.py), [`templates/admin/ai_demand.html`](templates/admin/ai_demand.html) |

---

## 🛠️ The 10 Cooperative Skilled Trades

| # | Trade Category | Standard Shift Rate | Typical Household & Community Services |
|---|---|---|---|
| 1 | **Electricians** | ₹450 / shift | Wiring, short circuit resolution, MCB distribution boards, inverter setup |
| 2 | **Plumbers** | ₹480 / shift | Pipe leakages, booster water pumps, drainage unclogging, sanitary fittings |
| 3 | **Carpenters** | ₹500 / shift | Furniture repair, door/window lock installations, modular woodwork |
| 4 | **Painters** | ₹460 / shift | Wall waterproofing, interior/exterior painting, touch-up finishing |
| 5 | **Caregivers** | ₹550 / shift | Elderly care, mobility assistance, post-operative support, vitals checking |
| 6 | **Domestic Helpers** | ₹400 / shift | Housekeeping, cooking, laundry, kitchen meal preparation |
| 7 | **Drivers** | ₹520 / shift | Personal chauffeur, family transit, commercial & heavy vehicle operation |
| 8 | **Cleaners** | ₹420 / shift | Deep home cleaning, bathroom sanitization, overhead water tank cleaning |
| 9 | **Gardeners** | ₹440 / shift | Lawn mowing, tree pruning, organic soil composting, terrace gardening |
| 10 | **Technicians** | ₹500 / shift | AC servicing, refrigerator, washing machine, microwave, RO water purifiers |

---

## ⚡ Quick Start & Installation

### Option A: One-Click Automatic Start (Recommended)

The project includes an intelligent launcher that automatically provisions `.venv`, installs dependencies, creates the MySQL database & missing tables, generates demo accounts, and prepares LAN mobile access.

1. **Start the application**:
   ```bash
   python main.py
   ```
   *(On Windows, you can also simply double-click **`START.bat`**)*

2. **Mobile Access**:
   - Keep the computer and phone on the same Wi-Fi network.
   - The launcher automatically detects your LAN IP and creates **`mobile_access_qr.png`**.
   - Scan the QR code with your phone camera or visit the printed network address.
   - Choose **Add to Home Screen / Install app** to install the PWA.

---

### Option B: Manual Setup

If you prefer step-by-step control:

1. **Prerequisites**: Python 3.10+ (Recommended: Python 3.13) & MySQL 8.0+ / MariaDB.

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration (Optional)**:
   Copy `.env.example` to `.env`. Default database settings (`root:root@localhost:3306/contractor_erp_db`) work out of the box with standard XAMPP or local MySQL setups.

5. **Initialize & Seed Database**:
   ```bash
   python seed_db.py
   ```

6. **Run Server**:
   ```bash
   python app.py
   ```
   Access at: `http://127.0.0.1:5000/`

---

## 🔑 Default Test Credentials

| Role | Username | Password | Dashboard URL | Primary Governance & Operations Controls |
|---|---|---|---|---|
| **State Federation (Apex)** | `publisher` | `publisher123` | `/publisher/dashboard` | Society KYC, Welfare Oversight, State Circulars, Security Logs |
| **Labour Cooperative Society** | `admin` | `admin123` | `/admin/dashboard` | Member Dispatch, AI Demand Forecasting, Invoices, Toolkits |
| **Cooperative Member Artisan** | `jdoe` | `worker123` | `/worker/dashboard` | Today's Jobs, GPS Check-In, OTP Verification, Wage Slip |
| **Household Client** | `anita` | `customer123` | `/customer/dashboard` | Book Service, Track Technician, Digital Sign & Pay |

---

## 📁 Repository Structure

```
SahakarSeva/
├── main.py                     # One-click launcher (auto-venv, DB bootstrap, LAN QR code)
├── START.bat                   # Windows double-click automated startup script
├── run_mobile.bat              # Mobile LAN access startup script
├── app.py                      # Application entrypoint & global route registry (74+ routes)
├── config.py                   # Environment-driven database & security configuration
├── database.py                 # SQLAlchemy database instance, connection diagnostics & helpers
├── seed_db.py                  # Consolidated seeder for all 22 cooperative tables and 100% field coverage
├── export_db.py                # Complete SQL schema & data backup exporter
├── DATABASE.MD                 # Live database schema specification & data dictionary (22 tables)
├── database_schema_and_data.sql# Full SQL database export with tables & verified seed records
├── SAHAKARSEVA_MASTER_DOCUMENTATION.md # Master architectural specification & slide deck
├── walkthrough.md              # Comprehensive demonstration walkthrough guide
├── models/                     # SQLAlchemy database models (22 active cooperative tables)
│   ├── __init__.py             # Model exports and package initialization
│   ├── user.py                 # Base authentication & credentials (users)
│   ├── contractor.py           # Multi-tenant cooperative society entity, reviews & subscriptions
│   ├── worker.py               # Member artisan, certifications & PMSBY/ESIC insurance
│   ├── worker_features.py      # Timesheets, task checklists, expense claims & safety reports
│   ├── customer.py             # Household & community client profiles
│   ├── service_request.py      # 12-stage service request lifecycle, emergency dispatch & OTP
│   ├── quotation.py            # Formal contractor price quotations & material estimates
│   ├── finance.py              # Payments, digital invoices & Suraksha Nidhi welfare transactions
│   ├── expense.py              # Project expense tracking
│   ├── inventory.py            # Toolkits, supplies, materials and equipment registry
│   ├── attendance.py           # GPS attendance logs & QR verification coordinates
│   ├── leave.py                # Worker leave applications and approvals
│   ├── communication.py        # Direct messages, notifications, system settings & audit logs
│   ├── dispute.py              # Grievance & dispute resolution tickets
│   ├── document.py             # Contractor KYC and regulatory documents
│   ├── ai_data.py              # AI estimates, delay forecasts & material predictions
│   └── platform.py             # Federation governance & security settings
├── routes/                     # Modular Flask Blueprints
│   ├── auth.py                 # Login, 2FA, and registration routing
│   ├── admin.py                # Society admin console & dispatch controls
│   ├── worker.py               # Member artisan mobile portal & timesheets
│   ├── customer.py             # Client hub, marketplace, and service booking
│   └── publisher.py            # Apex Federation state council dashboard
├── services/                   # Business logic engines
│   ├── ai_service.py           # AI heuristics, LLM integration, demand forecasting
│   ├── dispatch_service.py     # Emergency & on-demand dispatch engine with standard rate cards
│   ├── welfare_service.py      # Worker welfare & insurance fund engine (Suraksha Nidhi)
│   └── pdf_service.py          # ReportLab PDF invoice and quotation generator
├── static/                     # Frontend assets
│   ├── css/style.css           # Glassmorphic design system & universal mobile scaling
│   ├── css/pro_ui.css          # High-contrast color-restored professional cooperative styles
│   └── js/translations.js      # Full-page Google Translator API multilingual engine
└── templates/                  # Jinja2 HTML5 responsive views
    ├── base.html               # Master layout with omni-search, toast & language switch
    ├── login.html              # Role-based login & resident/artisan onboarding
    ├── register_contractor.html# 3-step society registration wizard
    ├── admin/                  # Dedicated society management dashboards & service tickets
    ├── worker/                 # Mobile-optimized artisan workspace, jobs & benefits
    ├── customer/               # Dedicated client bookings, payments, and marketplace
    └── publisher/              # Apex Federation command center & compliance audit
```

---

*SahakarSeva — Empowering Labour Cooperatives, Safeguarding Workers, Serving Communities.*
