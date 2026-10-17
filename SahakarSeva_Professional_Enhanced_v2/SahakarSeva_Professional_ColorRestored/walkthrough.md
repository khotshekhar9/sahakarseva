# SahakarSeva — Comprehensive System Walkthrough & Demonstration Guide

## 📌 Background
> Labour Cooperative Federations and Labour Cooperative Societies possess a large pool of skilled workers such as electricians, plumbers, carpenters, painters, domestic helpers, caregivers, drivers, gardeners, cleaners, and technicians. However, they lack a structured digital platform to connect these workers with households and institutions requiring such services. Private platforms currently dominate this market, while cooperative workers often remain underutilized despite having skills and local presence.

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

## 🏛️ The Six Core Technology Components

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               SAHAKARSEVA COOPERATIVE PLATFORM                                   │
├──────────────────────────────┬──────────────────────────────┬────────────────────────────────────┤
│ 1. MOBILE APPLICATIONS       │ 2. ARTIFICIAL                │ 3. GEO-SPATIAL                     │
│    • Mobile-First Responsive │    INTELLIGENCE (AI)         │    TECHNOLOGY                      │
│    • 29px/32px Touch Inputs  │    • Google Gemini 2.0 & Grok│    • OpenStreetMap Geocoding       │
│    • 2x2 Metric KPI Grids    │    • Smart Worker Match      │    • Haversine Dispatch Proximity  │
│    • Bottom Drawer Navigation│    • Heuristic Cost Estimator│    • GPS Geofenced Attendance      │
│    • PWA Adaptive Layout     │    • Delay & Surge Predict   │    • Live Technician Tracking      │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ 4. DIGITAL PAYMENT           │ 5. CLOUD COMPUTING           │ 6. PROPOSED MODE                   │
│    SYSTEMS                   │    • Multi-Tenant Row Scoping│    SOFTWARE                        │
│    • Central Financial Ledger│    • Decoupled Blueprints    │    • 4-Role Stakeholder Ecosystem  │
│    • Automated 18% GST       │    • Cloud MySQL / MariaDB   │    • 12-Stage Lifecycle Engine     │
│    • HTML5 Canvas Signatures │    • RESTful API Suite       │    • Cryptographic 6-Digit OTP Gate│
│    • 88/8/4 Living Wage/Cess │    • SocketIO Real-Time Sync │    • PMSBY/PMJJBY/ESIC Integration │
└──────────────────────────────┴──────────────────────────────┴────────────────────────────────────┘
```

### Component 1: 📱 Mobile Applications
- **Fluid Mobile Design System**: Responsive CSS rules in [`static/css/style.css`](static/css/style.css) with root `font-size` scaling (12.5px–14.5px) and clamping on smartphones.
- **Form Touch Scaling**: Single-line form inputs, select dropdowns, and button elements constrained to sleek 29px (phones) and 32px (tablets) touch targets.
- **Mobile Card Architecture**: 2x2 KPI stat cards (`col-6`), auto-wrapping card headers, and compact 68px collapsible sidebar.

### Component 2: 🧠 Artificial Intelligence (AI)
Located in [`services/ai_service.py`](services/ai_service.py):
- **Generative LLM Assistance (`AIService.call_external_llm`)**: Google Gemini 2.0 (`gemini-2.0-flash`) and Grok API (`grok-beta`) integration for real-time generative cost estimation, scope breakdown, and technical guidance with offline fallback.
- **AI Cost & Duration Estimator (`AIService.estimate_service_cost`)**: Heuristic engine analyzing house size, room counts, urgency tiers, and domain keywords to compute labor, material estimates, and confidence scores (60%–99%).
- **Smart Worker Recommendation Engine (`AIService.recommend_workers_smart`)**: Multi-factor scoring algorithm balancing NLP trade skill matching, GPS Haversine proximity, concurrent job load, customer ratings, and attendance history.
- **AI Delay Prediction (`AIService.predict_project_delay`)**: Evaluates attendance consistency and milestone velocity to forecast project delays.
- **AI Demand Forecasting & Workforce Allocation (`AIService.forecast_gig_service_demand`)**: 7-day rolling trade demand forecasts with automated surge detection across urban zones.

### Component 3: 🗺️ Geo-Spatial Technology
- **Reverse Geocoding Proxy (`/customer/api/geocode`)**: Resolves GPS coordinates to human-readable street addresses using OpenStreetMap Nominatim with server-side caching.
- **GIS Proximity-Based Matching**: Computes accurate Haversine and Euclidean distances between customer service addresses and registered worker locations to prioritize nearest available artisans.
- **GPS Geofenced Artisan Attendance (`models/attendance.py`)**: Captures real-time clock-in and clock-out coordinates (`latitude`, `longitude`) to guarantee verified physical presence at job locations.

### Component 4: 💳 Digital Payment Systems
Located in [`models/finance.py`](models/finance.py), [`routes/customer.py`](routes/customer.py), and [`services/pdf_service.py`](services/pdf_service.py):
- **Centralized Financial Ledger**: Automated revenue, expense, and wage tracking with dynamic **18% GST tax calculation** and discount application.
- **HTML5 Canvas Digital Signatures**: Allows customers to draw binding signatures directly on digital invoices via touch or mouse before payment (`/customer/invoice/sign`).
- **ReportLab PDF Invoicing**: Automated PDF invoice and quotation generator rendering company branding, GST numbers, itemized billing, and payment status stamps.
- **Cooperative 3-Tier Fair Wage & Welfare Split (`services/welfare_service.py` & `AIService.get_fair_wage_breakdown`)**:
  - **88%** Direct Worker Living Wage Payout (zero private aggregator commissions)
  - **8%** Primary Labour Cooperative Society Operations & Field Toolkits
  - **4%** Suraksha Nidhi Welfare & Social Security Reserve (PMSBY ₹20, PMJJBY ₹436, and healthcare insurance)

### Component 5: ☁️ Cloud Computing
- **Multi-Tenant SaaS Topology**: Strict row-level data isolation via `contractor_id` foreign keys, allowing hundreds of independent district labour societies to operate securely on a single cloud database.
- **Modular Microservice Blueprints**: Decoupled Flask Blueprints (`auth`, `admin`, `worker`, `customer`, `publisher`) for horizontal scaling and maintainability.
- **Production Database Pooling**: Supports MySQL 8.0 and MariaDB with connection pooling and automated table provisioning.
- **Real-Time WebSockets Sync**: Instant dispatch notifications, arrival alerts, and live messaging powered by `Flask-SocketIO`.

### Component 6: 📦 Proposed Mode Software Architecture
- **Cooperative Paradigm Shift**: Replaces exploitative private aggregators (extracting 25%–35% commission with zero insurance) with a worker-owned cooperative model offering 90% direct pay, mandatory state insurance, and cryptographic arrival gates.
- **4-Role Ecosystem**: Apex Federation (`publisher`), Labour Society (`admin`), Member Artisan (`worker`), Household Client (`customer`).
- **12-Stage Lifecycle State Machine**:
  $$\text{Requested} \rightarrow \text{Assigned} \rightarrow \text{In-Transit} \rightarrow \text{OTP Arrival} \rightarrow \text{In-Progress} \rightarrow \text{Quality Review} \rightarrow \text{Customer Sign-Off} \rightarrow \text{Invoiced} \rightarrow \text{Paid} \rightarrow \text{Completed} \rightarrow \text{Feedback} \rightarrow \text{Archived}$$
- **Cryptographic 6-Digit OTP Gate**: Physical technician verification gate preventing job starts until the customer shares their one-time arrival code.

---

> **UX update:** Demonstrations should use the simplified mobile-first flows: Customer → Book Service → My Bookings → Payments; Worker → My Jobs → Attendance → Earnings → Benefits; Admin → Bookings → Workers → Payments → AI & Demand.

## ✨ Demonstration Verification of the 11 Expected Solution Features

| # | Solution Feature | How to Verify in Live Demo | Expected Outcome |
|---|---|---|---|
| 1 | **Service Provider Registration & Verification** | Visit `/register-contractor`, submit a new society, then login as `publisher` and toggle verified badge. | Society verified status active across marketplace. |
| 2 | **Worker Skill Profiling & Certification** | Open `/admin/workers`, click on worker profile, inspect trade certifications and daily wage rate. | 10 trades profiled with verified certificates. |
| 3 | **Customer Booking & Scheduling** | Login as `anita` at `/customer/book-service`, pick trade, choose time slot, record voice note, and submit. Pre-dispatch editing supported. | Ticket generated with real-time status tracker in `/customer/bookings`. |
| 4 | **Geo-Location Based Service Matching** | Submit booking with GPS coordinates, view recommended workers in `/admin/service-requests`. | Nearest artisans ranked by Haversine proximity. |
| 5 | **Digital Payments & Invoicing** | Open completed job invoice, sign on HTML5 canvas, and click Pay. | 18% GST computed, signature stamped, PDF invoice downloaded. |
| 6 | **Rating & Feedback Mechanism** | Visit completed request in customer portal, submit 1-5 star rating and comment. | Society `average_rating` and review count recalculated. |
| 7 | **Worker Welfare & Insurance** | Login as `jdoe` at `/worker/benefits`, view Suraksha Nidhi Social Security Card. | Active PMSBY/ESIC policy numbers and coverage (₹2,00,000) displayed. |
| 8 | **Emergency & On-Demand Booking** | In booking wizard, toggle "Emergency / Urgent Priority". | Request routed with pre-approved cooperative tariffs and 1-click worker claiming. |
| 9 | **Federation Administration Dashboard** | Login as `publisher` at `/publisher/dashboard`. | State-wide overview of all district societies, KYC, and circulars. |
| 10 | **Multilingual Mobile Application** | Click language switcher in navigation bar, toggle to **मराठी** or **हिंदी**. | Full-page instant translation via Google Translator API proxy. |
| 11 | **AI Demand Forecasting & Allocation** | In `/admin/ai-demand`, review the 7-Day AI Gig Demand curve. | Predictive demand graph with surge alerts and worker gap advice. |

---

## 🛠️ The 10 Cooperative Skilled Trades

| # | Trade Category | Standard Shift Rate | Common Household Services |
|---|---|---|---|
| 1 | **Electricians** | ₹450 / shift | Wiring, short circuit repair, MCB panel boards, inverter backup |
| 2 | **Plumbers** | ₹480 / shift | Leakage repair, booster pumps, drainage unclogging, sanitary fittings |
| 3 | **Carpenters** | ₹500 / shift | Furniture repair, door/window locks, modular woodwork |
| 4 | **Painters** | ₹460 / shift | Waterproofing, interior/exterior painting, touch-up finishes |
| 5 | **Caregivers** | ₹550 / shift | Elderly assistance, post-operative care, vitals monitoring |
| 6 | **Domestic Helpers** | ₹400 / shift | Housekeeping, cooking, laundry, kitchen assistance |
| 7 | **Drivers** | ₹520 / shift | Personal chauffeur, family transport, commercial vehicle |
| 8 | **Cleaners** | ₹420 / shift | Deep home cleaning, bathroom scrubbing, water tank sanitization |
| 9 | **Gardeners** | ₹440 / shift | Lawn maintenance, tree pruning, organic compost healthcare |
| 10 | **Technicians** | ₹500 / shift | AC, refrigerator, washing machine, microwave, RO water purifier |

---

## 🔑 Live Test Credentials & Role Access

| Role | Username | Password | Dashboard URL | Primary Governance & Operation Controls |
|---|---|---|---|---|
| **State Federation (Apex)** | `publisher` | `publisher123` | `/publisher/dashboard` | Society KYC, Welfare Oversight, Circulars, Security Logs |
| **Labour Society** | `admin` | `admin123` | `/admin/dashboard` | Member Dispatch, AI Demand Forecast, Invoices, Toolkits |
| **Member Artisan** | `jdoe` | `worker123` | `/worker/dashboard` | Today's Jobs, GPS Check-In, OTP Verification, Wage Slip |
| **Household Client** | `anita` | `customer123` | `/customer/dashboard` | Book Service, Track Technician, Digital Sign & Pay |

---

## 🧭 Step-by-Step Judge Demonstration Script

### Step 1: Apex Federation Governance (Publisher Role)
1. Navigate to `/login` and sign in as `publisher` / `publisher123`.
2. Inspect the **State Federation Command Center**:
   - Total affiliated district cooperative societies, active member artisans, and welfare reserve funds.
3. Visit **Society Verification**:
   - Inspect newly registered PACS / Labour Societies and toggle their verified badge.
4. Visit **Security Audit Logs**:
   - Review immutable IP logs, 2FA logins, and operational audit records.

### Step 2: District Society Operations & AI Forecasting (Admin Role)
1. Sign in as `admin` / `admin123` to access the **Labour Cooperative Society Console**.
2. Review the **AI Demand & Workforce Allocation Forecast**:
   - 7-day trade demand curve with surge predictions for urban zones (`/admin/ai-demand`).
3. Review **Member Artisans & Social Security**:
   - Inspect member artisan profiles with verified Pradhan Mantri Bima Yojana (PMSBY/PMJJBY) policy numbers.
4. Navigate to **Service Request Management**:
   - Review incoming tickets, utilize the **Smart Worker Recommendation** engine, and dispatch technicians.

### Step 3: Household Client Booking & Transparent Pricing (Customer Role)
1. Sign in as `anita` / `customer123` to access the **Household Client Hub**.
2. Click **Book Service**:
   - Select one of the 10 skilled trades (e.g. Caregiver, Electrician, Plumber).
   - Test instant **AI Cost Estimation** detailing labor, materials, and confidence level.
   - View the transparent **90/4/4/2 Fair Wage Breakdown** (90% Worker Fair Wage, 4% Society Operations, 4% Federation Platform Support, 2% Worker Welfare Cess).
3. View **My Bookings**:
   - Observe the real-time timeline and the **6-digit arrival OTP** generated for technician check-in.
4. Test **Digital Sign & Pay**:
   - Open an invoice, use the **HTML5 canvas pad** to capture a digital signature, and settle the payment.

### Step 4: Member Artisan Field Workspace (Worker Role)
1. Sign in as `jdoe` / `worker123` to access the **Artisan Mobile Workspace**.
2. Test **GPS Geofenced Attendance**:
   - Perform clock-in with simulated coordinates.
3. Verify **Site Arrival via OTP**:
   - Enter the customer's 6-digit OTP to transition the job to `'In-Progress'`.
4. Review **Social Security & Fair Wage Slip** (`/worker/benefits` & `/worker/earnings`):
   - Verify PMSBY coverage status, welfare cess balance, and transparent direct earnings breakdown.

### Step 5: Full-Page Multilingual Translation
1. Click the top navigation language dropdown.
2. Switch from **English** to **मराठी (Marathi)**:
   - Observe full-page translation via `/api/translate` proxy without page refresh.
3. Switch to **हिंदी (Hindi)**:
   - Observe accurate regional translation.
4. Switch back to **English**:
   - Verify that the **immutable WeakMap** engine restores the exact original English strings with 0% distortion.

---

## 🧪 Automated Verification & System Status

- **Database Integrity**: All **35 tables** verified in MySQL (`contractor_erp_db`). Both [`DATABASE.MD`](DATABASE.MD) and [`database_schema_and_data.sql`](database_schema_and_data.sql) are 100% updated and synchronized.
- **Python Health**: 0 syntax or linting errors across all 30+ Python files.
- **Route Registry**: 74+ active routes loaded across 5 Flask Blueprints.
- **Mobile Responsiveness**: Verified fluid layout scaling across 375px, 412px, and 768px viewports.
