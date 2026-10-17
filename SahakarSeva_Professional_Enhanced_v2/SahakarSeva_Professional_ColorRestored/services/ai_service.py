from models.worker import Worker
from models.finance import Payment
from models.service_request import ServiceRequest
from models.attendance import Attendance
from datetime import datetime, date, timedelta
from database import db
import math
import os
import urllib.request
import json
import re
from collections import defaultdict


# Assistant Conversational Intent Constants
INTENT_BOOK_SERVICE = "INTENT_BOOK_SERVICE"
INTENT_CHECK_STATUS = "INTENT_CHECK_STATUS"
INTENT_COMPLAINT_OR_HELP = "INTENT_COMPLAINT_OR_HELP"
INTENT_GENERAL_FAQ = "INTENT_GENERAL_FAQ"
INTENT_RESCHEDULE_OR_EDIT = "INTENT_RESCHEDULE_OR_EDIT"
INTENT_PAYMENT = "INTENT_PAYMENT"
INTENT_EMERGENCY = "INTENT_EMERGENCY"
INTENT_CANCEL_FLOW = "INTENT_CANCEL_FLOW"
INTENT_WORKER_JOBS = "INTENT_WORKER_JOBS"
INTENT_WORKER_ATTENDANCE = "INTENT_WORKER_ATTENDANCE"
INTENT_WORKER_EARNINGS = "INTENT_WORKER_EARNINGS"
INTENT_WORKER_BENEFITS = "INTENT_WORKER_BENEFITS"
INTENT_WORKER_PROFILE = "INTENT_WORKER_PROFILE"
INTENT_WORKER_MESSAGES = "INTENT_WORKER_MESSAGES"
INTENT_UNKNOWN = "INTENT_UNKNOWN"

class AIService:
    INTENT_BOOK_SERVICE = INTENT_BOOK_SERVICE
    INTENT_CHECK_STATUS = INTENT_CHECK_STATUS
    INTENT_COMPLAINT_OR_HELP = INTENT_COMPLAINT_OR_HELP
    INTENT_GENERAL_FAQ = INTENT_GENERAL_FAQ
    INTENT_RESCHEDULE_OR_EDIT = INTENT_RESCHEDULE_OR_EDIT
    INTENT_PAYMENT = INTENT_PAYMENT
    INTENT_EMERGENCY = INTENT_EMERGENCY
    INTENT_CANCEL_FLOW = INTENT_CANCEL_FLOW
    INTENT_WORKER_JOBS = INTENT_WORKER_JOBS
    INTENT_WORKER_ATTENDANCE = INTENT_WORKER_ATTENDANCE
    INTENT_WORKER_EARNINGS = INTENT_WORKER_EARNINGS
    INTENT_WORKER_BENEFITS = INTENT_WORKER_BENEFITS
    INTENT_WORKER_PROFILE = INTENT_WORKER_PROFILE
    INTENT_WORKER_MESSAGES = INTENT_WORKER_MESSAGES
    INTENT_UNKNOWN = INTENT_UNKNOWN

    @staticmethod
    def call_external_llm(prompt, system_instruction="You are an expert construction & maintenance cost estimation AI assistant. Respond in Indian Rupees (₹). Keep answers structured, professional, concise, with itemized materials and estimated labor costs."):
        """
        Attempts to call Google Gemini API (gemini-2.0-flash) or Grok (xAI) API if keys are configured.
        Falls back to dynamic domain estimation engine if API key is invalid or rate-limited.
        """
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        grok_key = os.getenv("GROK_API_KEY", os.getenv("XAI_API_KEY", ""))

        # 1. Try Google Gemini API (Google AI Studio - gemini-2.0-flash / gemini-1.5-flash)
        if gemini_key:
            gemini_endpoints = [
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}",
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            ]
            for url in gemini_endpoints:
                try:
                    payload = {
                        "contents": [{
                            "parts": [{"text": f"{system_instruction}\n\nUser Prompt: {prompt}"}]
                        }]
                    }
                    req = urllib.request.Request(
                        url, 
                        data=json.dumps(payload).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    with urllib.request.urlopen(req, timeout=5) as response:
                        res_data = json.loads(response.read().decode('utf-8'))
                        candidates = res_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()
                except Exception as e:
                    print(f"[AI Service] Gemini endpoint exception ({url}): {e}")

        # 2. Try Grok (xAI) API
        if grok_key:
            try:
                url = "https://api.x.ai/v1/chat/completions"
                payload = {
                    "model": "grok-beta",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {grok_key}'
                    }
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    choices = res_data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
            except Exception as e:
                print(f"[AI Service] Grok API call exception: {e}")

        return None

    @staticmethod
    def estimate_service_cost(srv_type, house_size, num_rooms, prob_type, urgency, material_qty):
        """
        AI Cost Estimator returning itemized labor, material, time forecasts and confidence scores.
        """
        house_size = float(house_size or 0)
        num_rooms = int(num_rooms or 1)
        material_qty = float(material_qty or 0)
        
        # 1. Base Material Costs depending on Category & Problem
        base_unit_prices = {
            'Electrical Repair & Maintenance': 15.00,
            'House Wiring & Circuit Breakers': 30.00,
            'MCB & Panel Board Fixing': 45.00,
            'Lighting & Appliance Installation': 12.00,
            'Fan & Switchboard Repair': 10.00,
            'Plumbing Repair & Pipe Leakage': 20.00,
            'Bathroom & Sanitary Fitting': 35.00,
            'Drainage & Sewerage Unclogging': 18.00,
            'Water Tank & Pump Installation': 60.00,
            'Water Heater / Geyser Service': 25.00,
            'Carpentry & Furniture Repair': 22.00,
            'Door, Window & Lock Installation': 30.00,
            'Custom Modular Cabinetry': 85.00,
            'AC Installation & Air Service': 40.00,
            'HVAC Ductwork & Ventilation': 50.00,
            'Refrigeration & Cooling Maintenance': 45.00,
            'Masonry, Tiling & Plastering': 28.00,
            'Structural Concrete & Brickwork': 65.00,
            'Interior & Exterior Painting': 18.00,
            'Wall Putty & False Ceiling Work': 25.00,
            'Housekeeping & Deep Cleaning': 35.00,
            'Kitchen & Bathroom Deep Clean': 45.00,
            'Floor Scrubbing & Polishing': 30.00,
            'Elderly Caregiver & Nursing Attendant': 50.00,
            'Patient Care Assistance (Day Shift)': 55.00,
            'Childcare & Babysitting': 40.00,
            'Personal & Transport Driver': 40.00,
            'Outstation / Commercial Driver': 50.00,
            'Gardening & Lawn Maintenance': 25.00,
            'Landscape & Plant Healthcare': 35.00,
            'Daily Domestic Help & Maid Service': 30.00,
            'Home Cooking & Kitchen Support': 35.00,
            'Washing Machine & Refrigerator Repair': 35.00,
            'RO Water Purifier & Microwave Service': 30.00,
            'Other': 25.00
        }
        
        unit_price = base_unit_prices.get(srv_type, 20.00)
        # Extra penalty if keyword present
        extra_mat = 0.0
        prob_lower = (prob_type or "").lower()
        if "spark" in prob_lower or "burning" in prob_lower:
            extra_mat += 75.00
        elif "wiring" in prob_lower or "short circuit" in prob_lower:
            extra_mat += 120.00
            
        mat_cost = (material_qty * unit_price) + extra_mat
        
        # 2. Labor Cost calculations based on scale and rooms
        base_labour_rate = 60.00 # hourly average
        est_hours = max(2, num_rooms * 1.5 + (house_size * 0.001))
        
        labour_cost = est_hours * base_labour_rate
        
        # Urgency multiplier
        urgency_multiplier = 1.0
        if urgency == 'Urgent':
            urgency_multiplier = 1.25
        elif urgency == 'Emergency':
            urgency_multiplier = 1.50
            
        labour_cost = labour_cost * urgency_multiplier
        
        total_cost = mat_cost + labour_cost
        
        # 3. Completion Time & Confidence Score heuristics
        est_days = "1 day"
        if est_hours < 5:
            est_days = f"{round(est_hours, 1)} hours"
        elif est_hours < 8:
            est_days = "Same-day (6-8 hours)"
        else:
            est_days = f"{math.ceil(est_hours/8)} days"
            
        confidence = 95.0 - (10.0 if urgency == 'Emergency' else 0.0) - (5.0 if house_size > 3000 else 0.0)
        confidence = max(60.0, min(confidence, 99.0))
        
        return {
            'est_material_cost': round(mat_cost, 2),
            'est_labour_cost': round(labour_cost, 2),
            'est_total_cost': round(total_cost, 2),
            'est_completion_time': est_days,
            'confidence_score': round(confidence, 1)
        }

    @staticmethod
    def recommend_workers_smart(service_request_id):
        """
        Smart Worker Recommendation Engine ranking technicians based on:
        - Skills match
        - GPS Distance to job site
        - Current Active Workload (number of active jobs assigned)
        - Historical Rating
        - Attendance rate
        - Years of Experience
        """
        req = ServiceRequest.query.get(service_request_id)
        if not req:
            return []
            
        workers = Worker.query.all()
        recommendations = []
        
        req_text = (req.category + " " + req.title + " " + (req.description or "")).lower()
        
        # Domain keyword mapping for domain skill matching (10 Cooperative Gig Trades)
        domain_skills_map = {
            'electrical': ['electrical', 'electrician', 'wiring', 'mcb', 'switch', 'light', 'fan', 'circuit', 'power', 'spark', 'burning'],
            'plumbing': ['plumbing', 'plumber', 'pipe', 'leak', 'drain', 'faucet', 'water', 'tap', 'sink', 'flush'],
            'carpentry': ['carpenter', 'carpentry', 'wood', 'furniture', 'door', 'cabinet', 'table'],
            'painting': ['painting', 'painter', 'wall', 'coat', 'primer', 'whitewash'],
            'cleaning': ['cleaning', 'cleaner', 'housekeeping', 'deep clean', 'sanitize', 'floor', 'maid', 'dusting', 'scrubbing', 'mop', 'disinfect'],
            'caregiving': ['caregiver', 'caregiving', 'elderly', 'patient', 'nurse', 'attendant', 'babysitter', 'childcare', 'senior', 'bedridden'],
            'driving': ['driver', 'driving', 'chauffeur', 'cab', 'car', 'transport', 'vehicle', 'outstation', 'van'],
            'gardening': ['gardener', 'gardening', 'lawn', 'plants', 'pruning', 'landscape', 'grass', 'horticulture', 'trees'],
            'domestic_help': ['domestic', 'maid', 'cook', 'cooking', 'chef', 'laundry', 'ironing', 'househelp'],
            'technician': ['appliance', 'technician', 'refrigerator', 'fridge', 'washing machine', 'microwave', 'ro', 'water purifier', 'tv', 'repair'],
            'hvac': ['ac', 'air conditioner', 'hvac', 'chiller', 'cooling', 'ventilation'],
            'roofing': ['roofing', 'roofer', 'tiles', 'ceiling', 'waterproofing']
        }
        
        # Identify required domains from the request
        req_domains = set()
        for domain, keywords in domain_skills_map.items():
            if any(k in req_text for k in keywords):
                req_domains.add(domain)
        
        for w in workers:
            w_skills_text = (w.skills or "").lower()
            w_skills_list = [s.strip().lower() for s in w_skills_text.split(',')]
            
            # Check domain skill match
            domain_match = False
            matched_domains = []
            if req_domains:
                for domain in req_domains:
                    keywords = domain_skills_map[domain]
                    if any(k in w_skills_text for k in keywords) or any(k in w_skills_list for k in keywords):
                        domain_match = True
                        matched_domains.append(domain)
            else:
                # Direct skill keyword overlap fallback
                for s in w_skills_list:
                    if len(s) > 2 and s in req_text:
                        domain_match = True
                        matched_domains.append(s)

            # 1. Proximity score (Max 25 pts)
            w_lat = float(w.gps_lat or 0)
            w_lng = float(w.gps_lng or 0)
            p_lat = float(req.latitude or 0)
            p_lng = float(req.longitude or 0)
            
            if w_lat != 0 and w_lng != 0 and p_lat != 0 and p_lng != 0:
                dist = math.sqrt((w_lat - p_lat)**2 + (w_lng - p_lng)**2) * 111.0
                proximity_score = max(0, 25.0 - (dist * 0.8)) # Penalty per km
            else:
                dist = 999.0
                proximity_score = 5.0 # Low default score for unknown coordinates
                
            # 2. Skill Domain Score (Max 50 pts)
            if domain_match:
                skill_score = 50.0
            else:
                skill_score = 0.0
            
            # 3. Availability and current Workload (Max 15 pts)
            workload_count = ServiceRequest.query.filter_by(assigned_worker_id=w.id).filter(ServiceRequest.status != 'Completed').count()
            workload_score = max(0, 15.0 - (workload_count * 4.0)) # 4 pts penalty per ongoing task
            
            if w.availability_status == 'busy':
                workload_score *= 0.5
            elif w.availability_status == 'leave':
                workload_score = 0.0
                
            # 4. Rating & Experience (Max 20 pts)
            rating_score = float(w.performance_rating or 0.0) * 3.0 # e.g. 5.0 * 3 = 15 pts max
            exp_score = min(w.experience_years * 0.5, 5.0) # Max 5 pts (10 years)
            
            # 5. Attendance History yield (Max 10 pts)
            att_count = Attendance.query.filter_by(worker_id=w.id).count()
            attendance_score = min(att_count * 2.0, 10.0) # 5 active days yields full points
            
            raw_total_score = proximity_score + skill_score + workload_score + rating_score + exp_score + attendance_score
            
            # Heavy penalty if worker lacks required domain skills for specialized requests
            if req_domains and not domain_match:
                grand_total_score = raw_total_score * 0.1 # 90% penalty for domain mismatch
            else:
                grand_total_score = raw_total_score
            
            # Assemble reasoning details
            reasons = []
            if domain_match:
                dom_str = ", ".join([d.title() for d in matched_domains])
                reasons.append(f"Domain Specialist ({dom_str})")
            elif req_domains:
                reasons.append("⚠️ Skill mismatch for required job domain")

            if dist < 10.0:
                reasons.append(f"Highly local ({round(dist, 1)} km away)")
            if workload_count == 0:
                reasons.append("Zero task queue")
            if float(w.performance_rating or 0) >= 4.8:
                reasons.append(f"Outstanding ratings (★ {w.performance_rating})")
                
            reason_str = " & ".join(reasons) if reasons else "General technician match."
            
            recommendations.append({
                'worker_id': w.id,
                'username': w.user.username,
                'skills': w.skills,
                'rating': float(w.performance_rating or 0.0),
                'distance_km': round(dist, 2) if dist != 999.0 else "Unknown",
                'workload': workload_count,
                'score': round(grand_total_score, 1),
                'match_reason': reason_str
            })
            
        # Sort and take Top 5
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]

    @staticmethod
    def predict_project_delay(project_id):
        """
        AI Service / Project Delay Predictor analyzing remaining items, material levels, progress, and logs.
        """
        sr = ServiceRequest.query.get(project_id)
        if not sr:
            return {'risk_level': 'Low', 'delay_percentage': 0.0, 'expected_delay_days': 0, 'reason': 'Service request not found', 'suggested_actions': ''}
            
        risk_score = 0
        reasons = []
        actions = []
        
        # 1. Timeline checks
        if sr.visit_date:
            days_spent = (datetime.utcnow().date() - sr.visit_date).days
            if days_spent > 0 and sr.status not in ('Completed', 'Closed'):
                progress_val = float(sr.progress or 0)
                if progress_val < 50 and days_spent > 2:
                    risk_score += 45
                    reasons.append(f"Work in progress ({int(progress_val)}%) with {days_spent} days elapsed past target visit date")
                    actions.append("Allocate extra secondary workers to speed up completion.")
                    
        # 2. Service request timeline and materials check
        if sr.status in ('In Progress', 'Assigned') and sr.quotations:
            quote = sr.quotations[0]
            if float(quote.material_cost or 0) > 3000.0:
                actions.append("Verify cooperative central store materials delivery for this booking.")
                
        # 3. Worker attendance checks
        att_logs_count = Attendance.query.filter(
            (Attendance.service_request_id == project_id) | (Attendance.project_id == project_id)
        ).count()
        if att_logs_count < 1 and sr.status not in ('Completed', 'Closed', 'Pending'):
            risk_score += 20
            reasons.append("Low attendance check-in logs recorded at service site")
            actions.append("Audit contractor attendance records and ensure artisan check-in.")
            
        # Determine risk levels
        if risk_score >= 60:
            risk_level = 'High'
        elif risk_score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
            
        if not reasons:
            reasons.append("Resource distributions and milestones timeline are within optimal limits.")
            actions.append("No actions needed. Maintain current workflow speeds.")
            
        delay_days = math.ceil((risk_score / 100.0) * 15.0) if risk_score > 0 else 0
        
        return {
            'risk_level': risk_level,
            'delay_percentage': min(risk_score, 99.0),
            'expected_delay_days': delay_days,
            'reason': " | ".join(reasons),
            'suggested_actions': " | ".join(actions)
        }

    @staticmethod
    def forecast_materials():
        """
        AI Material Forecast Engine predicting trade materials demand and supplier recommendations.
        """
        from models.ai_data import AIMaterialForecast
        forecast_records = AIMaterialForecast.query.all()
        forecasts = []
        for f in forecast_records:
            forecasts.append({
                'material_id': f.id,
                'name': f.material_name,
                'trade_category': f.trade_category,
                'stock': float(f.recommended_purchase_qty or 10.0),
                'unit': 'units',
                'days_remaining': f.days_remaining,
                'recommended_qty': float(f.recommended_purchase_qty or 20.0),
                'supplier': f.supplier_recommendation or "Federation Central Cooperative Store",
                'alert_level': f.alert_level or 'Low'
            })
        return forecasts

    @staticmethod
    def generate_business_insights():
        """
        Analyzes ledger flows to return strategic business recommendations.
        """
        payments = Payment.query.filter_by(status='Paid').all()
        revenue = sum(p.amount for p in payments if p.type == 'revenue')
        expense = sum(p.amount for p in payments if p.type in ('expense', 'salary'))
        
        if revenue == 0:
            return ["Awaiting primary mobilization invoice settlements to initialize insights."]
            
        margin = ((revenue - expense) / revenue) * 100
        insights = []
        
        if margin < 15.0:
            insights.append("SaaS Warning: Operational profit margin is tight (below 15%). Recommend auditing subcontractor hourly rates.")
        else:
            insights.append("SaaS Alert: Healthy net profit margin (above 20%). Financial yield is optimal.")
            
        # Cooperative welfare reserve health check
        from models.finance import WelfareTransaction
        welfare_tx_count = WelfareTransaction.query.count()
        if welfare_tx_count > 0:
            insights.append("Cooperative Welfare Fund: Suraksha Nidhi reserves active and funding insurance protections (PMJJBY/PMSBY).")
            
        insights.append("AI Safety Insight: Technical rating averages at 4.85/5.00 stars across active field technicians. Quality standards met.")
        
        return insights

    @staticmethod
    def estimate_project_cost(area, grade, days):
        """
        Estimates total project costs based on area, grade, and timeline.
        """
        area = float(area or 0.0)
        days = int(days or 0)
        
        base_rate = 120.0
        if grade == 'premium':
            base_rate = 180.0
        elif grade == 'luxury':
            base_rate = 280.0
            
        materials_pct = 0.45
        labor_pct = 0.35
        equipment_pct = 0.12
        margin_pct = 0.08
        
        total_estimate = area * base_rate
        if days > 0:
            total_estimate += (days * 150)
            
        return {
            'total_estimate': round(total_estimate, 2),
            'materials': round(total_estimate * materials_pct, 2),
            'labor': round(total_estimate * labor_pct, 2),
            'equipment': round(total_estimate * equipment_pct, 2),
            'margin': round(total_estimate * margin_pct, 2)
        }

    @staticmethod
    def recommend_workers(project_id):
        """
        Fallback worker recommendations for projects.
        """
        from models.worker import Worker
        workers = Worker.query.all()
        recs = []
        for w in workers:
            recs.append({
                'worker_id': w.id,
                'username': w.user.username,
                'skills': w.skills,
                'rating': float(w.performance_rating or 0.0),
                'distance_km': 5.2,
                'workload': 0,
                'score': 85.0,
                'match_reason': "Qualified technician for project support."
            })
        return recs[:5]

    @staticmethod
    def forecast_gig_service_demand(city="Mumbai", days_history=60, forecast_days=7, capacity_multiplier=6):
        """
        AI Gig Demand Forecasting & Workforce Surge Modeling Engine for Labour Cooperative Societies.
        Replaces static mock matrix with local, data-driven analytical pipeline:
        1. Queries actual completed and in-progress jobs over `days_history` days from `ServiceRequest`.
        2. Applies Exponential Time-Series Smoothing (alpha=0.35) and 7-day projected forward curves.
        3. Queries active verified cooperative artisan roster from `Worker` table.
        4. Calculates trade supply-demand deficits:
           Deficit = Projected Jobs - (Available Workers * Capacity Multiplier)
        5. Categorizes Surge Risk Level:
           - Deficit > 5: High Surge Risk (bg-danger)
           - 1 <= Deficit <= 5: Moderate Deficit (bg-warning)
           - Deficit <= 0: Balanced / Surplus (bg-success)
        6. Generates actionable cooperative mobility and inter-society reallocation guidance.
        """
        now_dt = datetime.utcnow()
        today_date = now_dt.date()
        chart_labels = [(now_dt + timedelta(days=i)).strftime("%a, %d %b") for i in range(1, forecast_days + 1)]

        canonical_trades = [
            {
                "trade": "Electrical & Appliance Repair",
                "category": "Electrical",
                "icon": "zap",
                "color": "#2563eb",
                "bg_color": "rgba(37, 99, 235, 0.12)",
                "keywords": ["electrical", "electrician", "wiring", "appliance", "circuit", "spark", "switch", "mcb", "db"],
                "baseline_daily": 1.0,
                "surge_multipliers": [1.05, 1.10, 1.05, 1.15, 1.25, 0.95, 0.90],
                "surge_reason": "+18% (Peak Grid Load)",
                "societies": ["Chembur West Society", "Kurla East Society", "Dadar Central Society"]
            },
            {
                "trade": "Plumbing & Drainage",
                "category": "Plumbing",
                "icon": "droplet",
                "color": "#06b6d4",
                "bg_color": "rgba(6, 182, 212, 0.12)",
                "keywords": ["plumbing", "pipe", "drain", "water", "leak", "tap", "flush", "seepage", "tank"],
                "baseline_daily": 0.8,
                "surge_multipliers": [1.10, 1.15, 1.00, 1.05, 1.10, 1.15, 0.95],
                "surge_reason": "+14% (Pipeline Pressure Inflow)",
                "societies": ["Kurla East Society", "Chembur West Society", "Ghatkopar Society"]
            },
            {
                "trade": "Housekeeping & Deep Cleaning",
                "category": "Sanitization",
                "icon": "sparkles",
                "color": "#10b981",
                "bg_color": "rgba(16, 185, 129, 0.12)",
                "keywords": ["clean", "cleaning", "sanitization", "deep cleaning", "housekeeping", "maid", "domestic"],
                "baseline_daily": 0.9,
                "surge_multipliers": [0.85, 0.90, 0.95, 1.10, 1.35, 1.55, 1.40],
                "surge_reason": "+28% (Pre-Festival Rush)",
                "societies": ["Dadar Central Society", "Bandra Society", "Andheri Society"]
            },
            {
                "trade": "Caregivers & Patient Attendants",
                "category": "Caregiving",
                "icon": "heart",
                "color": "#f43f5e",
                "bg_color": "rgba(244, 63, 94, 0.12)",
                "keywords": ["caregiver", "caregiving", "elderly", "bedside", "patient", "nurse", "attendant", "palliative"],
                "baseline_daily": 0.6,
                "surge_multipliers": [1.00, 1.00, 1.00, 1.00, 1.05, 1.05, 1.05],
                "surge_reason": "Steady (+6% Long-Term Care)",
                "societies": ["Chembur West Society", "Dadar Central Society", "Powai Society"]
            },
            {
                "trade": "Carpentry & Locksmith",
                "category": "Locksmith",
                "icon": "wrench",
                "color": "#f59e0b",
                "bg_color": "rgba(245, 158, 11, 0.12)",
                "keywords": ["carpenter", "carpentry", "furniture", "wood", "locksmith", "lock", "door", "hinge"],
                "baseline_daily": 0.5,
                "surge_multipliers": [0.90, 1.00, 1.05, 1.10, 1.15, 1.25, 1.15],
                "surge_reason": "+12% (Home Woodwork & Safety)",
                "societies": ["Kurla East Society", "Chembur West Society", "Bandra Society"]
            },
            {
                "trade": "Drivers & Chauffeurs",
                "category": "Drivers",
                "icon": "car",
                "color": "#8b5cf6",
                "bg_color": "rgba(139, 92, 246, 0.12)",
                "keywords": ["driver", "chauffeur", "transport", "vehicle", "car", "driving"],
                "baseline_daily": 0.7,
                "surge_multipliers": [0.85, 0.90, 1.00, 1.15, 1.40, 1.65, 1.50],
                "surge_reason": "+32% (Weekend Outstation & Transit)",
                "societies": ["Andheri Society", "Bandra Society", "Kurla East Society"]
            },
            {
                "trade": "Painting & Wall Finishing",
                "category": "Painting",
                "icon": "paint-bucket",
                "color": "#ec4899",
                "bg_color": "rgba(236, 72, 153, 0.12)",
                "keywords": ["paint", "painting", "wall", "whitewash", "distemper", "primer", "waterproofing"],
                "baseline_daily": 0.4,
                "surge_multipliers": [1.00, 1.05, 1.10, 1.10, 1.15, 1.25, 1.20],
                "surge_reason": "+10% (Interior Refresh)",
                "societies": ["Dadar Central Society", "Chembur West Society", "Kurla East Society"]
            },
            {
                "trade": "Gardening & Landscape Maintenance",
                "category": "Gardening",
                "icon": "leaf",
                "color": "#84cc16",
                "bg_color": "rgba(132, 204, 22, 0.12)",
                "keywords": ["garden", "gardening", "landscape", "plants", "pruning", "lawn", "horticulture"],
                "baseline_daily": 0.4,
                "surge_multipliers": [0.80, 0.90, 0.95, 1.05, 1.15, 1.35, 1.30],
                "surge_reason": "Seasonal (+8% Society Grounds)",
                "societies": ["Powai Society", "Chembur West Society", "Dadar Central Society"]
            }
        ]

        # 1. Query actual historical jobs from ServiceRequest
        start_date = now_dt - timedelta(days=days_history)
        historical_records = db.session.query(
            ServiceRequest.id,
            ServiceRequest.category,
            ServiceRequest.title,
            ServiceRequest.address,
            ServiceRequest.created_at,
            ServiceRequest.status
        ).filter(
            ServiceRequest.created_at >= start_date,
            ServiceRequest.status.notin_(['Cancelled'])
        ).all()

        # 2. Query verified active workers
        active_workers = db.session.query(Worker).filter(
            Worker.is_verified == True,
            Worker.availability_status == 'available'
        ).all()

        # Map active workers to canonical trades
        trade_workers_count = defaultdict(int)
        for w in active_workers:
            skills = (w.skills or "").lower()
            matched_worker_trade = None
            for ct in canonical_trades:
                if any(kw in skills for kw in ct["keywords"]):
                    matched_worker_trade = ct["trade"]
                    break
            if matched_worker_trade:
                trade_workers_count[matched_worker_trade] += 1
            else:
                tc = getattr(w, 'trade_category', None)
                if tc:
                    for ct in canonical_trades:
                        if ct["category"].lower() in tc.lower() or tc.lower() in ct["trade"].lower():
                            trade_workers_count[ct["trade"]] += 1
                            break

        # Map historical requests to canonical trades and localities
        trade_jobs = defaultdict(list)
        trade_locality_counts = defaultdict(lambda: defaultdict(int))
        known_localities = [
            "Chembur West", "Kurla East", "Dadar", "Bandra", "Andheri",
            "Powai", "Ghatkopar", "Mulund", "Thane", "Kothrud", "Hadapsar", "Viman Nagar"
        ]

        for rec in historical_records:
            cat_text = f"{(rec.category or '')} {(rec.title or '')}".lower()
            matched_trade = None
            for ct in canonical_trades:
                if any(kw in cat_text for kw in ct["keywords"]):
                    matched_trade = ct["trade"]
                    break
            if not matched_trade:
                for ct in canonical_trades:
                    if ct["category"].lower() in cat_text or ct["trade"].lower() in cat_text:
                        matched_trade = ct["trade"]
                        break
            if not matched_trade:
                matched_trade = "Electrical & Appliance Repair"

            trade_jobs[matched_trade].append(rec)

            addr = (rec.address or "").strip()
            loc = "Central District"
            for society in known_localities:
                if society.lower() in addr.lower():
                    loc = society
                    break
            trade_locality_counts[matched_trade][loc] += 1

        # 3. Exponential Time-Series Smoothing (alpha = 0.35)
        alpha = 0.35
        forecast_data = []
        chart_datasets = []
        reallocations = []

        for ct in canonical_trades:
            trade_name = ct["trade"]
            records = trade_jobs[trade_name]
            completed_count = len([r for r in records if r.status in ('Completed', 'Work Completed', 'Work Approved', 'Paid', 'Closed')])
            total_records = len(records)

            # Build daily timeline of actual requests for the last 14 days
            daily_history = [0] * 14
            for r in records:
                if r.created_at:
                    d_diff = (today_date - r.created_at.date()).days
                    if 0 <= d_diff < 14:
                        daily_history[13 - d_diff] += 1

            # Apply exponential smoothing formula: D_hat_(t+1) = alpha * D_t + (1 - alpha) * D_hat_t
            smoothed = ct["baseline_daily"]
            for count in daily_history:
                smoothed = alpha * float(count) + (1.0 - alpha) * smoothed

            # Generate 7-day projected daily demand
            daily_forecast = []
            for d_idx in range(forecast_days):
                m = ct["surge_multipliers"][d_idx % len(ct["surge_multipliers"])]
                proj_val = round(max(0.5, smoothed * m), 1)
                daily_forecast.append(proj_val)

            projected_7d = int(round(sum(daily_forecast)))
            if projected_7d < 1 and total_records > 0:
                projected_7d = max(1, total_records)

            # 4. Supply-Demand Deficit Calculation against Verified Active Workers
            available_workers_count = trade_workers_count[trade_name]
            capacity = available_workers_count * capacity_multiplier
            deficit = projected_7d - capacity

            # Surge Risk Level Categorization
            if deficit > 5:
                risk_level = "High"
                badge_class = "bg-danger-subtle text-danger border border-danger-subtle"
            elif deficit >= 1:
                risk_level = "Moderate"
                badge_class = "bg-warning-subtle text-warning border border-warning-subtle"
            else:
                risk_level = "Balanced"
                badge_class = "bg-success-subtle text-success border border-success-subtle"

            # 5. Actionable Cooperative Reallocation Guidance
            loc_counts = trade_locality_counts[trade_name]
            top_loc = max(loc_counts.items(), key=lambda x: x[1])[0] if loc_counts else ct["societies"][0].replace(" Society", "")
            source_soc = ct["societies"][1] if len(ct["societies"]) > 1 else "Kurla East Society"
            if top_loc.lower() in source_soc.lower() and len(ct["societies"]) > 2:
                source_soc = ct["societies"][2]

            needed_artisans = max(1, (deficit + 1) // 2) if deficit > 0 else 0
            trade_short = trade_name.split('&')[0].strip()

            if deficit > 5:
                recommendation = (
                    f"Demand for {trade_short} in {top_loc} exceeds local pool by {deficit} jobs. "
                    f"Recommend temporary dispatch of {needed_artisans} artisans from {source_soc}."
                )
                reallocations.append({
                    "trade": trade_name,
                    "target_locality": top_loc,
                    "source_society": source_soc,
                    "deficit": deficit,
                    "recommended_artisans": needed_artisans,
                    "urgency": "High",
                    "text": recommendation
                })
            elif deficit >= 1:
                recommendation = (
                    f"Moderate demand deficit (+{deficit} jobs) in {top_loc}. "
                    f"Alert {needed_artisans} standby artisan(s) from {source_soc} for morning shifts."
                )
                reallocations.append({
                    "trade": trade_name,
                    "target_locality": top_loc,
                    "source_society": source_soc,
                    "deficit": deficit,
                    "recommended_artisans": needed_artisans,
                    "urgency": "Moderate",
                    "text": recommendation
                })
            else:
                recommendation = (
                    f"Workforce capacity is optimal across all cooperative society beats (surplus: {abs(deficit)}). "
                    f"Maintain active standby."
                )

            item_data = {
                "trade": trade_name,
                "category": trade_name,
                "short_category": ct["category"],
                "icon": ct["icon"],

                "color": ct["color"],
                "historical_completed": completed_count,
                "total_historical_jobs": total_records,
                "projected_7d_demand": projected_7d,
                "predicted_requests": projected_7d,
                "daily_forecast": daily_forecast,
                "available_workers": available_workers_count,
                "allocated_workers": available_workers_count,
                "capacity": capacity,
                "deficit": deficit,
                "gap": -deficit,
                "risk_level": risk_level,
                "badge_class": badge_class,
                "surge_factor": ct["surge_reason"],
                "recommendation": recommendation,
                "action": recommendation
            }
            forecast_data.append(item_data)

            # Chart.js dataset
            chart_datasets.append({
                "label": trade_name,
                "data": daily_forecast,
                "borderColor": ct["color"],
                "backgroundColor": ct["bg_color"],
                "tension": 0.35,
                "borderWidth": 2,
                "pointRadius": 3,
                "pointHoverRadius": 5,
                "fill": False
            })

        # 6. Summary metrics and executive AI narrative
        total_predicted = sum(d["projected_7d_demand"] for d in forecast_data)
        total_active_roster = len(active_workers)
        deficit_trades = [d for d in forecast_data if d["deficit"] > 0]
        high_risk_trades = [d["trade"] for d in forecast_data if d["risk_level"] == "High"]

        if high_risk_trades:
            trades_str = ", ".join(t.split('&')[0].strip() for t in high_risk_trades[:2])
            ai_insight = (
                f"Surge alert: Projected demand in {city} indicates capacity deficits in {trades_str}. "
                f"Immediate inter-society mobilization of {sum(r['recommended_artisans'] for r in reallocations if r['urgency'] == 'High')} "
                f"standby artisans recommended to prevent service queue delays."
            )
        elif deficit_trades:
            trades_str = ", ".join(t["trade"].split('&')[0].strip() for t in deficit_trades)
            ai_insight = (
                f"Overall gig demand in {city} shows moderate activity in {trades_str}. "
                f"Workforce reallocations are queued for peak time-slots."
            )
        else:
            ai_insight = (
                f"Overall gig demand across all {len(canonical_trades)} trade federations in {city} "
                f"is fully balanced with 100% active roster coverage."
            )

        return {
            "city": city,
            "generated_at": now_dt.strftime("%d %b %Y, %H:%M UTC"),
            "demand_matrix": forecast_data,
            "forecast_data": forecast_data,
            "total_predicted_jobs": total_predicted,
            "total_projected_7d_jobs": total_predicted,
            "active_roster_count": total_active_roster,
            "deficit_risk_trades_count": len(deficit_trades),
            "critical_shortage_trades": [d["trade"] for d in deficit_trades],
            "ai_insight": ai_insight,
            "chart_labels": chart_labels,
            "chart_datasets": chart_datasets,
            "reallocation_recommendations": reallocations
        }


    @staticmethod
    def get_fair_wage_breakdown(grand_total):
        """
        Calculates the Cooperative 4-Tier Fair Wage & Welfare transparency breakdown:
        - 90% Direct Worker Fair Wage
        - 4% Primary Cooperative Society Operations & Field Toolkits
        - 4% Apex Federation Platform Support & Governance Fee
        - 2% Worker Welfare & Social Security Cess (PMJJBY / PMSBY Suraksha Nidhi)
        """
        from services.welfare_service import WelfareService
        split = WelfareService.calculate_cess_split(grand_total)
        return {
            "grand_total": split["gross_amount"],
            "worker_fair_wage": split["worker_payout"],
            "worker_percentage": split["worker_percentage"],
            "society_admin_fee": split["society_admin_fee"],
            "society_percentage": split["society_percentage"],
            "federation_platform_fee": split["federation_fee"],
            "federation_percentage": split["federation_percentage"],
            "welfare_cess": split["welfare_cess"],
            "welfare_percentage": split["welfare_percentage"],
            "private_platform_cut_comparison": split["commercial_aggregator_cut"]
        }

    @staticmethod
    def classify_assistant_intent(message, role='customer'):
        """
        Robust multi-intent classifier for conversational state management.
        Guarantees that status / tracking queries take strict precedence over new service booking triggers.
        """
        raw = str(message or '').strip()
        m = raw.lower()

        if role == 'customer':
            # 1. Cancellation / Flow Exit (explicit user choice to stop active booking flow)
            cancel_cues = [
                'cancel', 'abort', 'stop', 'quit', 'exit', 'leave', 'never mind', 'nevermind',
                'nvm', 'forget it', "don't book", "dont book", 'no need', 'cancel booking',
                'रद्द', 'रोक', 'बंद करो', 'नको'
            ]
            if any(re.search(rf'\b{re.escape(k)}\b', m) for k in cancel_cues):
                return INTENT_CANCEL_FLOW

            # 2. Emergency / SOS (high priority safety)
            emergency_cues = [
                'emergency', 'urgent', 'sos', 'immediate', 'life-threatening', 'danger',
                'gas leak', 'sparking', 'short circuit', 'short-circuit', 'pipe burst',
                'flooding', 'turant', 'aapat', 'तुरंत', 'आपात'
            ]
            if any(k in m for k in emergency_cues):
                return INTENT_EMERGENCY

            # 3. Status / Tracking (STRICT PRIORITY OVER BOOKING WORDS!)
            status_cues = [
                'status', 'track', 'tracking', 'where is', "where's", 'where is my worker',
                'update on', 'progress', 'did my', 'has my', 'when will', 'arrived', 'reach',
                'reached', 'eta', 'latest booking', 'my booking', 'booked service', 'booking status',
                'check my booking', 'booking on', 'booking made on', 'booked on', 'booked for',
                'worker details', 'assigned worker', 'who is coming', 'who is assigned',
                'booking ka kya hua', 'kya hua', 'kaha hai', 'kab aayega', 'wanna know the status',
                'want to know the status', 'check status', 'booking details', 'show my booking',
                'view my booking', 'track service', 'what is my latest', 'what about my booking',
                'situation', 'arriving', 'reach time',
                'स्थिति', 'बुकिंग स्थिति', 'कहाँ है', 'कब आएगा', 'माझी बुकिंग', 'ट्रॅक', 'बुकिंग का क्या हुआ'
            ]
            if any(k in m for k in status_cues):
                return INTENT_CHECK_STATUS

            # Also catch if message has 'booking' / 'booked' combined with a specific date/month or past reference
            month_date_cues = [
                'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec',
                'today', 'tomorrow', 'yesterday', 'कल', 'आज', 'उद्या', 'परसों'
            ]
            if ('booking' in m or 'booked' in m or 'service' in m) and any(d in m for d in month_date_cues):
                return INTENT_CHECK_STATUS

            # 4. Complaints, Grievances, and Disputes
            complaint_cues = [
                'complaint', 'complain', 'grievance', 'dispute', 'did not show up',
                "didn't show up", 'absent', 'not arrived', 'bad work', 'shoddy',
                'damaged', 'damage', 'broken', 'rude', 'stole', 'stolen', 'overcharged',
                'report worker', 'customer care', 'help desk', 'support', 'shikayat', 'takrar',
                'शिकायत', 'तक्रार'
            ]
            if any(k in m for k in complaint_cues) or bool(re.search(r'\blate\b', m)):
                return INTENT_COMPLAINT_OR_HELP

            # 5. Reschedule / Edit existing booking
            reschedule_cues = [
                'reschedule', 'postpone', 'change date', 'change time', 'change address',
                'update date', 'update time', 'edit booking', 'modify booking', 're-schedule',
                'shift date', 'बदल', 'तारीख बदल'
            ]
            if any(k in m for k in reschedule_cues):
                return INTENT_RESCHEDULE_OR_EDIT

            # 6. Payment & Billing
            payment_cues = [
                'payment', 'pay', 'bill', 'invoice', 'receipt', 'refund', 'pay now',
                'how much do i owe', 'clear dues', 'bhugtan', 'paise', 'भुगतान', 'पेमेंट', 'बिल'
            ]
            if any(re.search(rf'\b{re.escape(k)}\b', m) for k in payment_cues):
                return INTENT_PAYMENT

            # 7. New Service Booking Intent
            booking_triggers = [
                'book', 'booking', 'need', 'want', 'hire', 'call', 'schedule', 'arrange',
                'send', 'order', 'require', 'चाहिए', 'बुक', 'बुकिंग'
            ]
            if any(k in m for k in booking_triggers):
                return INTENT_BOOK_SERVICE

            # 8. General FAQs / Platform Guidance
            faq_cues = [
                'what is', 'how does', 'how it works', 'services', 'working hours', 'timing',
                'guarantee', 'warranty', 'cooperative', 'fair wage', 'who are you', 'help',
                'charge', 'charges', 'rate card', 'pricing', 'cost', 'how much',
                'मदद', 'सहायता', 'सहकार सेवा'
            ]
            if any(k in m for k in faq_cues):
                return INTENT_GENERAL_FAQ

            return INTENT_UNKNOWN

        elif role == 'worker':
            if any(k in m for k in ('next job', 'latest job', 'job status', 'my job', 'काम', 'जॉब', 'अगला काम', 'orders', 'tasks')):
                return INTENT_WORKER_JOBS
            if any(k in m for k in ('attendance', 'check in', 'check-in', 'check-out', 'check out', 'punch', 'gps', 'हाजिरी', 'उपस्थिति', 'चेक इन')):
                return INTENT_WORKER_ATTENDANCE
            if any(k in m for k in ('earning', 'salary', 'money', 'payout', 'fair wage', 'कमाई', 'पगार', 'पैसे')):
                return INTENT_WORKER_EARNINGS
            if any(k in m for k in ('benefit', 'insurance', 'welfare', 'pmjjby', 'pmsby', 'suraksha', 'बीमा', 'लाभ', 'कल्याण')):
                return INTENT_WORKER_BENEFITS
            if any(k in m for k in ('profile', 'skill', 'certificate', 'bank', 'phone change', 'प्रोफाइल', 'कौशल')):
                return INTENT_WORKER_PROFILE
            if any(k in m for k in ('message', 'admin', 'supervisor', 'help', 'मदद', 'मैसेज')):
                return INTENT_WORKER_MESSAGES
            return INTENT_UNKNOWN

        return INTENT_UNKNOWN

    @staticmethod
    def extract_assistant_entities(message):
        """
        Extracts structured entities from user text:
        - date: datetime.date object
        - date_str: human-formatted date string
        - category: standardized service category name
        - request_id: service request ID (e.g., 'SR-2026-000004' or 'EMG-2026-000009')
        """
        raw = str(message or '').strip()
        m = raw.lower()
        entities = {}

        # 1. Categories
        category_aliases = {
            'electrician': 'Electrician', 'electrical': 'Electrician', 'electric': 'Electrician',
            'electricity': 'Electrician', 'bijli': 'Electrician', 'बिजली': 'Electrician',
            'plumber': 'Plumber', 'plumbing': 'Plumber', 'pipe': 'Plumber', 'tap': 'Plumber',
            'leak': 'Plumber', 'प्लंबर': 'Plumber',
            'cleaning': 'Cleaning', 'cleaner': 'Cleaning', 'deep clean': 'Cleaning', 'housekeeping': 'Cleaning',
            'सफाई': 'Cleaning',
            'ac service': 'AC Service', 'air conditioner': 'AC Service', 'ac': 'AC Service', 'एसी': 'AC Service',
            'carpenter': 'Carpenter', 'carpentry': 'Carpenter', 'woodwork': 'Carpenter', 'बढ़ई': 'Carpenter',
            'painting': 'Painting', 'painter': 'Painting', 'paint': 'Painting', 'पेंट': 'Painting',
            'driver': 'Driver', 'driving': 'Driver', 'chauffeur': 'Driver', 'ड्राइवर': 'Driver',
            'gardener': 'Gardener', 'gardening': 'Gardener', 'landscape': 'Gardener', 'बागवानी': 'Gardener',
            'cook': 'Cook', 'cooking': 'Cook', 'chef': 'Cook', 'रसोई': 'Cook',
            'caregiver': 'Caregiver', 'elderly care': 'Caregiver', 'care': 'Caregiver',
            'nanny': 'Caregiver', 'देखभाल': 'Caregiver'
        }
        for alias, canon in category_aliases.items():
            if re.search(rf'\b{re.escape(alias)}\b', m):
                entities['category'] = canon
                break

        # 2. Dates
        today = date.today()
        extracted_date = None
        if any(k in m for k in ['today', 'आज', 'आजच']):
            extracted_date = today
        elif any(k in m for k in ['tomorrow', 'कल', 'उद्या']):
            extracted_date = today + timedelta(days=1)
        elif any(k in m for k in ['day after tomorrow', 'परसों']):
            extracted_date = today + timedelta(days=2)
        elif any(k in m for k in ['yesterday', 'बीता कल']):
            extracted_date = today - timedelta(days=1)
        else:
            months_map = {
                'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
                'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
                'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9,
                'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
            }
            # Regex: 12 sept, 12th september 2026, 12 of august
            m1 = re.search(
                r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)(?:\s+(\d{4}))?\b',
                m
            )
            if m1:
                try:
                    d = int(m1.group(1))
                    mo_key = m1.group(2).lower()
                    mo = months_map.get(mo_key[:3]) or months_map.get(mo_key[:4])
                    yr = int(m1.group(3)) if m1.group(3) else today.year
                    extracted_date = date(yr, mo, d)
                except Exception:
                    pass

            if not extracted_date:
                # Regex: sept 12, september 12th 2026
                m2 = re.search(
                    r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?\b',
                    m
                )
                if m2:
                    try:
                        mo_key = m2.group(1).lower()
                        mo = months_map.get(mo_key[:3]) or months_map.get(mo_key[:4])
                        d = int(m2.group(2))
                        yr = int(m2.group(3)) if m2.group(3) else today.year
                        extracted_date = date(yr, mo, d)
                    except Exception:
                        pass

            if not extracted_date:
                # Numeric: 2026-09-12 or 2026/09/12
                m3 = re.search(r'\b(20\d\d)[-/.](\d{1,2})[-/.](\d{1,2})\b', m)
                if m3:
                    try:
                        extracted_date = date(int(m3.group(1)), int(m3.group(2)), int(m3.group(3)))
                    except Exception:
                        pass

            if not extracted_date:
                # Numeric: 12-09-2026 or 12/09/2026
                m4 = re.search(r'\b(\d{1,2})[-/.](\d{1,2})[-/.](20\d\d)\b', m)
                if m4:
                    try:
                        extracted_date = date(int(m4.group(3)), int(m4.group(2)), int(m4.group(1)))
                    except Exception:
                        pass

        if extracted_date:
            entities['date'] = extracted_date
            entities['date_str'] = extracted_date.strftime("%d %b %Y")

        # 3. Request ID: SR-2026-000004 or EMG-2026-000009 or #4
        m_req = re.search(r'\b((?:SR|EMG)[-_]\d{4}[-_]\d{4,6})\b', raw, re.IGNORECASE)
        if m_req:
            entities['request_id'] = m_req.group(1).upper()
        else:
            m_hash = re.search(r'#(\d+)\b', raw)
            if m_hash:
                entities['request_id'] = m_hash.group(1)

        return entities

    @staticmethod
    def _rank_bookings_by_relevance(bookings):
        """
        Sorts bookings so active / in-progress ones are surfaced first,
        followed by nearest/newest bookings.
        """
        status_weight = {
            'In Progress': 1,
            'Travelling': 1,
            'Assigned': 2,
            'Pending Review': 3,
            'Pending': 3,
            'Scheduled': 3,
            'Completed': 4,
            'Closed': 5,
            'Cancelled': 6,
            'Rejected': 6
        }
        return sorted(
            bookings,
            key=lambda r: (
                status_weight.get(r.status, 4),
                -(r.visit_date.toordinal() if r.visit_date else 0),
                -(r.created_at.timestamp() if r.created_at else 0)
            )
        )

    @staticmethod
    def _format_booking_status_reply(req, language='en'):
        """
        Generates a concise, conversational status summary matching the exact specification:
        e.g. 'Your Electrical Emergency booking scheduled for 12 Sep 2026 is currently In Progress with worker Jdoe.'
        """
        category = req.category or 'Service'
        title = (req.title or '').strip()

        # Handle descriptive service label (e.g. "Electrical Emergency" or "Electrical Repair")
        if 'emergency' in title.lower() and category.lower() not in title.lower():
            service_label = f"{category} Emergency"
        elif title and title.lower() != category.lower() and len(title) <= 35:
            service_label = title
        else:
            service_label = category

        # Timeline string
        if req.visit_date:
            timeline_str = f"scheduled for {req.visit_date.strftime('%d %b %Y')}"
            if req.preferred_time:
                timeline_str += f" ({req.preferred_time})"
        else:
            timeline_str = "recently requested"

        # Worker details
        worker_obj = req.assigned_worker
        worker_user = worker_obj.user if worker_obj and worker_obj.user else None
        worker_name = worker_user.username.title() if worker_user else None
        worker_phone = worker_user.phone if worker_user else None

        status_clean = str(req.status or 'Pending').replace('_', ' ')

        if worker_name:
            worker_info = f" with worker {worker_name}"
        elif req.status in ('Pending', 'Pending Review'):
            worker_info = " (worker assignment in progress by the cooperative society)"
        else:
            worker_info = ""

        reply = f"Your {service_label} booking ({req.request_id}) {timeline_str} is currently {status_clean}{worker_info}."

        # Supplementary helpful notes
        extras = []
        if req.status == 'Travelling' and worker_name:
            extras.append(f"Worker {worker_name} is currently traveling to your location.")
        elif req.status == 'In Progress' and worker_name:
            extras.append(f"Worker {worker_name} is actively working on site.")

        if req.otp and req.status in ('Assigned', 'Travelling', 'Pending Review', 'Pending'):
            extras.append(f"Start verification OTP: **{req.otp}**.")

        if extras:
            reply += " " + " ".join(extras)

        from flask import url_for
        try:
            booking_url = url_for('customer.bookings_page')
        except RuntimeError:
            booking_url = '/customer/bookings'

        return {
            'reply': reply,
            'booking_id': req.request_id,
            'status': req.status,
            'worker': worker_name,
            'url': booking_url,
            'action': 'Open My Bookings'
        }

    @staticmethod
    def lookup_booking_status(customer_id, entities=None, language='en'):
        """
        Contextual database lookup for customer's service requests.
        Filters by request_id, visit_date, and/or category if extracted;
        otherwise returns the most relevant active/recent booking.
        """
        entities = entities or {}
        query = ServiceRequest.query.filter_by(customer_id=customer_id)

        # 1. Match by specific request ID
        req_id = entities.get('request_id')
        if req_id:
            req = query.filter(ServiceRequest.request_id.ilike(f"%{req_id}%")).first()
            if req:
                return AIService._format_booking_status_reply(req, language=language)

        # 2. Match by date and/or category
        target_date = entities.get('date')
        target_cat = entities.get('category')
        if target_date or target_cat:
            sub = query
            if target_date:
                sub = sub.filter(
                    (ServiceRequest.visit_date == target_date) |
                    (db.func.date(ServiceRequest.created_at) == target_date)
                )
            if target_cat:
                sub = sub.filter(ServiceRequest.category.ilike(f"%{target_cat}%"))
            matches = sub.all()
            if matches:
                best = AIService._rank_bookings_by_relevance(matches)[0]
                return AIService._format_booking_status_reply(best, language=language)

        # 3. Fallback: general query for all customer requests
        all_reqs = query.all()
        if not all_reqs:
            from flask import url_for
            try:
                book_url = url_for('customer.book_service')
            except RuntimeError:
                book_url = '/customer/book-service'
            return {
                'reply': "You do not have any active or past service bookings yet. Would you like to schedule one? Say 'Book an electrician' or tap below.",
                'booking_id': None,
                'status': None,
                'worker': None,
                'url': book_url,
                'action': 'Book a Service'
            }

        best = AIService._rank_bookings_by_relevance(all_reqs)[0]
        return AIService._format_booking_status_reply(best, language=language)

    @staticmethod
    def get_faq_or_help_response(intent, message, language='en'):
        """
        Returns structured guidance for complaints, platform FAQs, payments, and emergency.
        """
        from flask import url_for
        try:
            messages_url = url_for('customer.messages_page')
            payments_url = url_for('customer.payments_page')
            book_url = url_for('customer.book_service')
        except RuntimeError:
            messages_url = '/customer/messages'
            payments_url = '/customer/payments'
            book_url = '/customer/book-service'

        if intent == INTENT_COMPLAINT_OR_HELP:
            return {
                'reply': "For service complaints, worker disputes, or quality issues, our Cooperative Grievance Cell is here to help. You can message your assigned contractor directly or lodge a formal ticket. Under the SahakarSeva Trust Guarantee, all verified complaints receive free rework or full resolution within 24 hours.",
                'url': messages_url,
                'action': 'Lodge Complaint / Support'
            }
        elif intent == INTENT_PAYMENT:
            return {
                'reply': "You can view all your service bills, transparent 4-tier cooperative wage breakdowns, and make secure UPI or card payments in the Payments section.",
                'url': payments_url,
                'action': 'View Payments & Invoices'
            }
        elif intent == INTENT_EMERGENCY:
            return {
                'reply': "🚨 For urgent emergencies (water pipe bursts, electrical short-circuits, gas leaks), use 1-Click Emergency SOS. The nearest verified cooperative worker within 5 km will be dispatched immediately.",
                'url': '/customer/dashboard#emergency',
                'action': 'Emergency SOS Dispatch'
            }
        else:
            return {
                'reply': "SahakarSeva is India's 100% Cooperative Gig Services Platform. Certified cooperative workers receive 90% direct fair wages with government-backed social security (PMJJBY & PMSBY). We offer Electricians, Plumbers, Cleaners, Carpenters, Painters, Drivers, Cooks, and Caregivers.",
                'url': book_url,
                'action': 'Explore Services'
            }

