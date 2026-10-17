# SahakarSeva — Clean Database Guide & Table Blueprint
**A Simple, Honest, Cooperative Platform for Everyday Home and Community Services**

---

## 📖 Welcome & Background (What is this project?)
In India, millions of hardworking, skilled people work with their hands every day—electricians, plumbers, carpenters, painters, appliance fixers, cleaners, and masons. Most of them belong to local **Labour Cooperative Societies**. 

Even though these workers have real skills, government certificates, and live in our own neighborhoods, big private companies often take huge cuts from their earnings (sometimes 20% to 30%). 

**SahakarSeva** changes that. It is a digital marketplace **owned and run by the Labour Cooperatives themselves**. It makes sure:
1. **Workers get fair pay** (88% of every rupee paid for labor goes straight to the worker's pocket).
2. **Workers get social safety** (4% goes into the **Suraksha Nidhi** welfare fund for doctor bills, pension, and life insurance like PMJJBY and PMSBY).
3. **Local societies stay strong** (8% goes to the primary cooperative society for office operations and tools).
4. **Customers get peace of mind** (Aadhaar-verified workers, upfront rates, 4-digit arrival OTP, and honest warranty).

---

## 🧹 Why We Cleaned the Database (Why 13 Tables Were Removed)
Earlier, the system had 35 database tables. It had lots of heavy, complicated software code designed for huge multi-crore private construction corporations (like big warehouse inventories, daily expense claims, complicated employee timesheets, machine rentals, and paid corporate subscriptions).

### The Big Improvement:
We completely removed **13 unnecessary tables** and all their code. 

**Why was this the best decision?**
- **Much Simpler Code**: We removed thousands of confusing lines that nobody needed.
- **Smaller File Size**: The app takes less memory, downloads faster, and backups take seconds.
- **Faster Speed**: The system runs much faster on simple computers and mobile phones without slowing down.
- **Zero Confusion**: Cooperative managers and workers see only what matters: jobs, verified workers, attendance, and fair payments.

### Tables Removed:
1. `materials` (Replaced with direct job supplies)
2. `equipment` (Replaced with cooperative toolkits)
3. `project_materials` (Replaced with simple item lists on quotations)
4. `equipment_assignments` (Unneeded tracking overhead)
5. `project_expenses` (Removed corporate construction overhead)
6. `subscription_payments` (Cooperatives are member-owned, not paying monthly SaaS bills)
7. `worker_leave_requests` (Artisans simply set their live status to "Busy" or "Available")
8. `worker_timesheets` (Directly tracked by job clock-in and job completion)
9. `worker_expense_claims` (Simplified into job quotes)
10. `worker_safety_reports` (Handled directly via job checklists and help desk)
11. `platform_settings` (Merged into one clean `system_settings` table)
12. `dispute_tickets` (Merged into one unified `support_tickets` table)
13. `messages` (Alerts and messages unified into instant `notifications`)

**Result:** Exactly **22 clean, lightning-fast tables** remain. Every table has a clear purpose.

---

## 🗺️ The 22 Active Tables Explained in Plain English

Here are the 22 tables grouped into 6 everyday clusters:

```
+--------------------------------------------------------------------------------+
|                        SAHAKARSEVA - 22 ACTIVE TABLES                          |
+--------------------------------------------------------------------------------+
| 1. PEOPLE & LOGINS    : users, contractors, customers, workers                 |
| 2. JOBS & BOOKINGS    : service_requests, quotations, attendance               |
| 3. FAIR PAY & WELFARE : payments, welfare_transactions                         |
| 4. TRUST & SKILLS     : contractor_reviews, contractor_documents,               |
|                         worker_certifications, worker_task_checklists          |
| 5. SMART ASSISTANTS   : ai_estimates, ai_delay_predictions,                    |
|                         ai_material_forecasts                                  |
| 6. NOTICE & SUPPORT   : support_tickets, system_announcements,                 |
|                         notifications, activity_logs, login_histories,         |
|                         system_settings                                        |
+--------------------------------------------------------------------------------+
```

---

### Group 1: People & Logins (Who Uses the App?)

#### 1. `users` (The Master Account List)
- **What it is in simple words**: This is the digital register of every person who can sign into the website.
- **Who is in here?**:
  - **Publisher**: The State Federation Head who oversees all societies.
  - **Admin**: The manager of a local Cooperative Society (like Chembur or Kurla).
  - **Worker**: The skilled technician (electrician, plumber, carpenter).
  - **Customer**: The citizen or housing society secretary who needs work done.
- **Key Information Saved**: Username, email, scrambled secret password (hash), phone number, home address, profile photo, and role.
- **Current Records**: 21 active users.

#### 2. `contractors` (The Labour Cooperative Societies)
- **What it is in simple words**: The registered cooperative societies that provide workers.
- **Why is it called contractors?**: In Indian law and municipal tenders, primary cooperatives bid as registered labour societies.
- **Key Information Saved**: Society name, official government cooperative registration number, office address, phone, email, areas served (e.g. Chembur, Govandi, Kurla), star rating, and verification badge.
- **Current Records**: 4 cooperative organizations.

#### 3. `customers` (The Households & Housing Societies)
- **What it is in simple words**: The people and apartment buildings ordering repair services.
- **Key Information Saved**: Connects to their `users` account, billing address, company or society name (e.g., *Deonar Heights CHS*), and emergency phone numbers.
- **Current Records**: 5 registered customers.

#### 4. `workers` (The Skilled Artisans)
- **What it is in simple words**: The actual electricians, plumbers, carpenters, and painters doing the job.
- **Key Information Saved**:
  - **Skills & Experience**: Years on the job and trades known.
  - **Skill Tier**: *Apprentice* (learning), *Skilled Craftsman* (experienced), or *Master Artisan* (expert lead).
  - **Live Availability**: Is the worker free right now, or busy on another job?
  - **Live Location**: GPS latitude and longitude so the app can find the nearest worker in an emergency.
  - **Social Security**: Bank account for direct wages, PMJJBY insurance ID, PMSBY insurance ID, and ESIC number.
- **Current Records**: 10 verified artisans.

---

### Group 2: Everyday Jobs & Attendance

#### 5. `service_requests` (The Job Bookings)
- **What it is in simple words**: Every single customer request for help—from a leaking kitchen pipe to an electrical switchboard short-circuit.
- **How it works step-by-step**:
  1. Customer books a job (they can even record a quick voice message or attach a photo).
  2. The system checks if it is an **Emergency 1-Click Dispatch** or a scheduled visit.
  3. A nearby skilled artisan claims the job and taps "Travelling".
  4. The artisan arrives at the customer's doorstep and asks for the **4-digit secret OTP** (e.g. `4829`) to prove they arrived at the right home.
  5. The artisan finishes the work, ticks the safety checklist, takes a photo of the completed job, and collects payment.
- **Current Records**: 8 real-life job tickets.

#### 6. `quotations` (The Upfront Cost Estimate)
- **What it is in simple words**: The honest bill presented to the customer before major work starts, so there are never any surprises or hidden fees.
- **Key Information Saved**: List of parts needed with prices, labor charges, government tax (GST), discounts, and final total.
- **Current Records**: 3 detailed quotations.

#### 7. `attendance` (The Worker Daily Punch-In)
- **What it is in simple words**: Proves the artisan showed up on time and at the correct customer location.
- **How it works**:
  - Artisan taps "Punch In" on their mobile phone.
  - The phone checks **GPS location** (geofence) to confirm the artisan is truly on site.
  - Customer shows a **QR code** on their phone that the artisan scans.
- **Current Records**: 6 verified attendance records.

---

### Group 3: Fair Pay & Worker Social Security

#### 8. `payments` (The Fair Pay Engine)
- **What it is in simple words**: The register of all money paid by customers and how that money gets fairly split.
- **The Statutory 88 / 8 / 4 Fair Split**:
  - **88%** goes directly to the **Worker** as an honest living wage.
  - **8%** goes to the **Primary Cooperative Society** for operational expenses.
  - **4%** goes to the **Suraksha Nidhi Fund** for worker welfare and insurance.
- **Key Information Saved**: Bill number, customer signature picture, payment method (Cash, UPI, Card), and exact rupee breakdown.
- **Current Records**: 4 settled payment invoices.

#### 9. `welfare_transactions` (The Worker Passbook for Suraksha Nidhi)
- **What it is in simple words**: Like a bank passbook specifically for worker social security.
- **What gets written in here?**:
  - **Deposits (+)**: Every time a job finishes, 4% of the bill is added to the worker's welfare balance.
  - **Insurance Auto-Debits (-)**: Once a year, the system automatically pays ₹20 for PMSBY (accident insurance) and ₹436 for PMJJBY (life insurance) so the worker's family is always protected.
  - **Grants (+)**: Emergency medical grants or child school scholarship awards.
- **Current Records**: 6 passbook transactions.

---

### Group 4: Trust, Safety & Official Papers

#### 10. `contractor_reviews` (Customer Star Ratings & Reviews)
- **What it is in simple words**: 1 to 5 star ratings and written reviews from customers after a job is finished. Keeps cooperative quality high.
- **Current Records**: 3 verified reviews.

#### 11. `contractor_documents` (The Official Document Vault)
- **What it is in simple words**: Safe online locker storing PDF copies of government cooperative registration certificates, public liability insurance policies, and PWD electrical licenses.
- **Current Records**: 4 legal compliance documents.

#### 12. `worker_certifications` (The Artisan Diplomas & Trade Licenses)
- **What it is in simple words**: Verifies that an electrician or welder is properly trained.
- **Examples**: National Trade Certificate (NCVT), Government ITI Diploma, or Skill India (NSDC) certificate.
- **Current Records**: 4 verified trade diplomas.

#### 13. `worker_task_checklists` (Step-by-Step Quality & Safety Checklists)
- **What it is in simple words**: A safety checklist the artisan checks off on their phone while doing the work.
- **Examples**:
  - Step 1: Turn off the main electric switch before touching wires.
  - Step 2: Use voltage tester to verify power is cut.
  - Step 3: Install genuine branded fuse switch and tighten screws.
- **Current Records**: 6 completed safety checklists.

---

### Group 5: Smart AI Helpers (Predictive Analytics)

#### 14. `ai_estimates` (The Instant Price Helper)
- **What it is in simple words**: A smart computer assistant that looks at the customer's problem (e.g., "sparking switchboard") and tells them roughly what it should cost and how many hours it will take before an artisan even visits.
- **Current Records**: 4 estimates.

#### 15. `ai_delay_predictions` (The Weather & Delay Warning Helper)
- **What it is in simple words**: Warns managers if a job might take longer than usual. For example, if heavy monsoon rains in Mumbai slow down outdoor wall painting.
- **Current Records**: 3 delay risk alerts.

#### 16. `ai_material_forecasts` (The Raw Materials Warning Helper)
- **What it is in simple words**: Looks at upcoming jobs and warns the cooperative: *"You only have 4 days worth of copper wire or waterproof paint left in the local depot. Please reorder."*
- **Current Records**: 3 trade material forecast alerts.

---

### Group 6: Communications, Notice Board & Security

#### 17. `support_tickets` (Customer Help Desk & Dispute Arbitration)
- **What it is in simple words**: The central complaint and help box.
- **Dual Function**:
  - Handles regular questions (like requesting a stamped tax receipt).
  - Handles **Apex Escalations / Disputes** (if a customer and worker disagree on work quality, the State Federation Super Admin reviews the evidence and arbitrates a fair decision).
- **Current Records**: 5 support & dispute tickets.

#### 18. `system_announcements` (The Notice Board)
- **What it is in simple words**: Official messages posted by the Federation for all workers, society admins, or customers (like monsoon safety rules or annual meeting dates).
- **Current Records**: 3 announcements.

#### 19. `notifications` (Instant Alert Bells)
- **What it is in simple words**: The little notification bell on top of the screen that rings when:
  - An emergency job is broadcasted nearby.
  - A customer's OTP is confirmed.
  - A worker receives money into their welfare fund.
- **Current Records**: 5 notifications.

#### 20. `activity_logs` (The Security Diary)
- **What it is in simple words**: An automatic diary that writes down every single important action on the website (who approved which society, who verified which OTP, who paid which bill). Nobody can erase this diary.
- **Current Records**: 5 security logs.

#### 21. `login_histories` (The Sign-In Register)
- **What it is in simple words**: Writes down every time someone logs into the website, the time, their computer/phone type, and if their password worked.
- **Current Records**: 6 login history logs.

#### 22. `system_settings` (The Main Control Switchboard)
- **What it is in simple words**: The master setting switches for the whole platform.
- **What is controlled here?**:
  - Platform name, contact phone, and helpline email.
  - Welfare fund percentage (4.0%).
  - Worker fair wage percentage (88.0%).
  - Minimum hourly floor wage (₹250.00/hour).
  - Instant emergency dispatch radius (7.5 km).
  - Emergency maintenance switches (allows locking out access if repairs are needed).
- **Current Records**: 30 master configuration settings.

---

## 📊 Summary Table of the 22 Clean Tables

| # | Table Name | Everyday Purpose | Records |
| :--- | :--- | :--- | :--- |
| 1 | `users` | Logins and passwords for all accounts | 21 |
| 2 | `contractors` | Primary Labour Cooperative Societies | 4 |
| 3 | `customers` | Household and society customers | 5 |
| 4 | `workers` | Skilled cooperative artisans (electricians, plumbers, etc.) | 10 |
| 5 | `service_requests` | Service job bookings across full lifecycle | 8 |
| 6 | `quotations` | Upfront cost estimates and part breakdowns | 3 |
| 7 | `attendance` | Daily check-in verified by GPS and QR code | 6 |
| 8 | `payments` | Customer payments split 88% / 8% / 4% | 4 |
| 9 | `welfare_transactions` | Suraksha Nidhi worker pension & insurance passbook | 6 |
| 10 | `contractor_reviews` | Customer ratings and star reviews | 3 |
| 11 | `contractor_documents` | Safe online locker for government cooperative certificates | 4 |
| 12 | `worker_certifications` | Verified trade licenses and ITI diplomas | 4 |
| 13 | `worker_task_checklists` | Safety and quality checklist for field work | 6 |
| 14 | `ai_estimates` | Smart computer tool that predicts job costs and hours | 4 |
| 15 | `ai_delay_predictions` | Smart computer tool that warns of rain or transit delays | 3 |
| 16 | `ai_material_forecasts` | Smart computer tool that warns of low supplies | 3 |
| 17 | `support_tickets` | Customer helpdesk and dispute arbitration | 5 |
| 18 | `system_announcements` | Official federation circulars and notice board | 3 |
| 19 | `notifications` | Alert bells for workers, customers, and admins | 5 |
| 20 | `activity_logs` | Tamper-proof security diary of important actions | 5 |
| 21 | `login_histories` | Sign-in records with device information | 6 |
| 22 | `system_settings` | Master control switches, percentages, and phone numbers | 30 |

---

## 🛠️ How to Reseed the Database at Any Time
If you ever want to wipe and repopulate the database with clean, perfect sample data:
```bash
# 1. Activate the virtual environment
.\.venv\Scripts\activate

# 2. Run the clean seeder
python seed_db.py --clean

# 3. Export the fresh backup dump
python export_db.py
```
Both commands take less than 10 seconds and guarantee 100% data integrity with zero bloat!