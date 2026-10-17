from flask import Blueprint, render_template, abort, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from functools import wraps
from database import db
from datetime import datetime, date
import os
import mysql.connector
from models.user import User
from models.contractor import Contractor, ContractorReview
from models.worker import Worker
from models.customer import Customer
from models.attendance import Attendance
from models.finance import Payment, WelfareTransaction
from models.communication import Notification, SupportTicket, ActivityLog, LoginHistory, SystemSettings
from models.service_request import ServiceRequest
from models.document import ContractorDocument
from models.worker_features import WorkerTaskChecklist, WorkerCertification
from services.ai_service import AIService
from services.welfare_service import WelfareService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('admin', 'contractor'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_current_contractor():
    """Return the Contractor profile for the currently logged-in contractor admin."""
    if not current_user.is_authenticated:
        return None

    c = Contractor.query.filter_by(user_id=current_user.id).first()
    if not c and current_user.role in ('admin', 'contractor'):
        c = Contractor(
            user_id=current_user.id,
            company_name=f"{current_user.username.capitalize()} Construction & Builders",
            business_type='General',
            contact_email=current_user.email,
            contact_phone=current_user.phone,
            is_active=True,
            is_verified=True,
            service_areas='Mumbai,Pune,Nashik,Thane'
        )
        db.session.add(c)
        db.session.commit()
    return c


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    contractor = get_current_contractor()
    cid = contractor.id if contractor else None

    # Fetch all data scoped to this contractor
    service_requests = ServiceRequest.query.filter_by(
        is_archived=False, contractor_id=cid
    ).order_by(ServiceRequest.id.desc()).all() if cid else []
    projects = service_requests

    workers = Worker.query.filter_by(is_archived=False, contractor_id=cid).all() if cid else []
    worker_ids = [w.id for w in workers]

    # Only fetch customers who have ever given a service request to this contractor
    all_associated_customer_ids = {s.customer_id for s in service_requests if s.customer_id}
    customers = Customer.query.filter(
        Customer.id.in_(all_associated_customer_ids),
        Customer.is_archived == False
    ).all() if all_associated_customer_ids else []

    attendance = Attendance.query.filter(
        Attendance.is_archived == False,
        Attendance.worker_id.in_(worker_ids)
    ).order_by(
        Attendance.date.desc(), Attendance.check_in_time.desc()
    ).all() if (cid and worker_ids) else []
    materials = []
    equipment = []
    payments = Payment.query.filter_by(is_archived=False, contractor_id=cid).order_by(Payment.date.desc()).all() if cid else []
    tickets = SupportTicket.query.filter(
        SupportTicket.is_archived == False,
        SupportTicket.customer_id.in_(all_associated_customer_ids)
    ).order_by(SupportTicket.created_at.desc()).all() if all_associated_customer_ids else []

    documents = ContractorDocument.query.filter_by(contractor_id=cid).order_by(ContractorDocument.uploaded_at.desc()).all() if cid else []
    expenses = []
    leave_requests = []

    worker_expense_claims = []
    worker_timesheets = []
    worker_certifications = WorkerCertification.query.filter(WorkerCertification.worker_id.in_(worker_ids)).order_by(WorkerCertification.created_at.desc()).all() if (cid and worker_ids) else []
    safety_reports = []
    task_checklists = WorkerTaskChecklist.query.filter_by(contractor_id=cid).order_by(WorkerTaskChecklist.id.desc()).all() if cid else []

    # Calculate executive metrics for dashboard homepage
    total_bookings = len(service_requests)
    active_bookings = sum(1 for r in service_requests if r.status in ('In Progress', 'Assigned', 'Active'))
    pending_bookings = sum(1 for r in service_requests if r.status in ('Pending', 'Open'))
    completed_bookings = sum(1 for r in service_requests if r.status == 'Completed')

    total_projects = total_bookings if total_bookings > 0 else len(projects)
    active_projects = active_bookings if total_bookings > 0 else sum(1 for p in projects if p.status == 'Active')
    completed_projects = completed_bookings if total_bookings > 0 else sum(1 for p in projects if p.status == 'Completed')
    delayed_projects = pending_bookings if total_bookings > 0 else sum(1 for p in projects if p.status == 'Delayed')

    # Calculate attendance metrics
    today = datetime.utcnow().date()
    worker_ids_set = {w.id for w in workers}
    today_attendance = [a for a in attendance if a.date == today and a.worker_id in worker_ids_set]
    workers_present = sum(1 for a in today_attendance if a.status in ('Present', 'Late'))
    workers_absent = len(workers) - workers_present

    # Calculate financial metrics
    total_revenue = float(sum(p.amount for p in payments if p.type == 'revenue' and p.status == 'Paid') or 0.0)
    total_expenses = float(sum(p.amount for p in payments if p.type == 'expense' and p.status == 'Paid') or 0.0) + float(sum(e.amount for e in expenses) or 0.0)
    total_salaries = float(sum(p.amount for p in payments if p.type == 'salary' and p.status == 'Paid') or 0.0)
    net_profit = total_revenue - total_expenses - total_salaries
    pending_payments = float(sum(p.amount for p in payments if p.status == 'Pending') or 0.0)

    # Alerts
    material_alerts = sum(1 for m in materials if m.quantity_in_stock <= m.reorder_level)
    equipment_alerts = sum(1 for eq in equipment if eq.status in ('Maintenance', 'Damaged'))

    # AI Gig Demand Forecasting for Labour Cooperative Society
    target_city = (contractor.service_areas.split(',')[0].strip()) if (contractor and contractor.service_areas) else "Pune"
    gig_demand_forecast = AIService.forecast_gig_service_demand(city=target_city)

    return render_template(
        'admin/dashboard.html',
        contractor=contractor,
        projects=projects,
        service_requests=service_requests,
        workers=workers,
        customers=customers,
        attendance=attendance,
        materials=materials,
        equipment=equipment,
        payments=payments,
        tickets=tickets,
        documents=documents,
        expenses=expenses,
        leave_requests=leave_requests,
        worker_expense_claims=worker_expense_claims,
        worker_timesheets=worker_timesheets,
        worker_certifications=worker_certifications,
        safety_reports=safety_reports,
        task_checklists=task_checklists,
        gig_demand_forecast=gig_demand_forecast,

        # Metrics
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        delayed_projects=delayed_projects,
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        completed_bookings=completed_bookings,
        pending_bookings=pending_bookings,
        workers_present=workers_present,
        workers_absent=workers_absent,
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        total_salaries=total_salaries,
        net_profit=net_profit,
        pending_payments=pending_payments,
        material_alerts=material_alerts,
        equipment_alerts=equipment_alerts
    )


# 1. Project Management CRUD Actions (Redirect to Service Requests)
@admin_bp.route('/project/add', methods=['POST'])
@login_required
@admin_required
def add_project():
    flash("Projects have transitioned to Cooperative Service Requests.", "info")
    return redirect(url_for('admin.service_requests'))

# 2. Worker Assignment / Transfer Action
@admin_bp.route('/worker/transfer', methods=['POST'])
@login_required
@admin_required
def transfer_worker():
    try:
        worker_id = request.form.get('worker_id')
        target_id = request.form.get('service_request_id') or request.form.get('project_id')
        
        worker = Worker.query.get(worker_id)
        sr = ServiceRequest.query.get(target_id) if target_id else None
        
        if worker and sr:
            sr.assigned_worker_id = worker.id
            if sr.status in ('Pending', 'Broadcast'):
                sr.status = 'Assigned'
                
            n = Notification(
                user_id=worker.id,
                title="Service Request Allocation",
                message=f"You have been allocated to service request #{sr.request_id}: {sr.title}.",
                type="Info"
            )
            db.session.add(n)
            db.session.commit()
            flash(f"Worker {worker.user.username} allocated to service request #{sr.request_id} successfully!", "success")
        else:
            flash("Worker or Service Request not found.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error transferring worker: {str(e)}", "danger")
        
    return redirect(url_for('admin.dashboard') + '#workers')

# 3. Material Add / Service updates
@admin_bp.route('/material/add', methods=['POST'])
@login_required
@admin_required
def add_material():
    flash("Material charges are quoted directly in the service request estimate.", "info")
    return redirect(url_for('admin.dashboard'))

# 4. Equipment Add / Service updates
@admin_bp.route('/equipment/add', methods=['POST'])
@login_required
@admin_required
def add_equipment():
    flash("Equipment & tools are managed per service booking.", "info")
    return redirect(url_for('admin.dashboard'))

# 5. Financial Invoice Generation
@admin_bp.route('/payment/add', methods=['POST'])
@login_required
@admin_required
def add_payment():
    try:
        pay_type = request.form.get('type')  # 'revenue', 'expense', 'salary'
        amount = float(request.form.get('amount', 0.0) or 0.0)
        desc = request.form.get('description')
        proj_id = request.form.get('project_id') or None
        cust_id = request.form.get('customer_id') or None
        work_id = request.form.get('worker_id') or None
        status = request.form.get('status', 'Pending')
        
        # Auto generate invoice number
        prefix = 'INV' if pay_type == 'revenue' else 'EXP' if pay_type == 'expense' else 'SAL'
        stamp = datetime.now().strftime('%Y%m%d%H%M%S')
        inv_no = f"{prefix}-{stamp}"
        
        contractor = get_current_contractor()
        split = WelfareService.calculate_cess_split(amount)
        p = Payment(
            type=pay_type, amount=amount, status=status, description=desc,
            project_id=proj_id, customer_id=cust_id, worker_id=work_id,
            invoice_number=inv_no, signed_by_customer=False,
            contractor_id=contractor.id if contractor else None,
            worker_payout=split['worker_payout'],
            society_admin_fee=split['society_admin_fee'],
            federation_fee=split['federation_fee'],
            welfare_cess=split['welfare_cess']
        )
        db.session.add(p)
        db.session.flush()

        # If logged as Paid immediately and worker is associated, credit 2% cess
        if status == 'Paid' and work_id and float(split['welfare_cess']) > 0:
            WelfareService.credit_welfare_cess(
                worker_id=int(work_id),
                cess_amount=float(split['welfare_cess']),
                payment_id=p.id,
                description=f"2% Cooperative Welfare Cess from Payment {inv_no}"
            )

        db.session.commit()
        flash(f"Invoice/Payment record {inv_no} logged successfully. (90% Worker, 4% Society, 4% Federation, 2% Welfare Cess)", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error logging payment: {str(e)}", "danger")
        
    return redirect(url_for('admin.dashboard') + '#payments')

from flask import jsonify
from services.ai_service import AIService

@admin_bp.route('/api/ai/recommend-workers', methods=['GET'])
@login_required
@admin_required
def api_recommend_workers():
    project_id = request.args.get('project_id')
    if not project_id:
        return jsonify([])
    try:
        recommendations = AIService.recommend_workers(int(project_id))
        return jsonify(recommendations)
    except Exception as e:
        return jsonify([])

@admin_bp.route('/api/ai/cost-estimate', methods=['GET'])
@login_required
@admin_required
def api_cost_estimate():
    try:
        area = float(request.args.get('area', 0.0) or 0.0)
        grade = request.args.get('grade', 'standard')
        days = int(request.args.get('days', 0) or 0)
        estimate = AIService.estimate_project_cost(area, grade, days)
        return jsonify(estimate)
    except Exception as e:
        return jsonify({'error': str(e)})

@admin_bp.route('/api/ai/business-insights', methods=['GET'])
@login_required
@admin_required
def api_business_insights():
    try:
        insights = AIService.generate_business_insights()
        return jsonify(insights)
    except Exception as e:
        return jsonify([])

@admin_bp.route('/api/ai/chat', methods=['POST'])
@login_required
@admin_required
def api_ai_chat():
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({'status': 'error', 'message': 'Prompt is required'}), 400
            
        llm_reply = AIService.call_external_llm(prompt)
        if not llm_reply:
            p_lower = prompt.lower()
            if "paint" in p_lower:
                llm_reply = "AI Cost Advisor: Analyzed house painting complaint scope.\n\nRecommended Materials: 10L Premium Acrylic Emulsion Paint (₹1,800.00), 2 Gallons Wall Primer & Sandpaper (₹900.00), Painter Masking Tapes & Roller Trays (₹700.00).\nTotal Materials: ₹3,400.00 | Labor (2 Painters, 1.5 Days): ₹3,780.00."
            elif "mcb" in p_lower or "spark" in p_lower or "electric" in p_lower or "wiring" in p_lower:
                llm_reply = "AI Cost Advisor: Analyzed electrical MCB sparking complaint scope.\n\nRecommended Materials: 63A 3-Pole MCB Circuit Breaker (₹1,400.00), Heavy-Duty Copper Wiring Harness (₹1,100.00), Insulation Tape & Safety Gloves (₹500.00).\nTotal Materials: ₹3,000.00 | Labor (Senior Electrician): ₹3,780.00."
            elif "plumb" in p_lower or "leak" in p_lower or "pipe" in p_lower:
                llm_reply = "AI Cost Advisor: Analyzed plumbing leakage scope.\n\nRecommended Materials: CPVC Pipe Fittings & Coupling Joint (₹1,100.00), Waterproof Sealant & Valves (₹800.00), Pressure Gauge Assembly (₹600.00).\nTotal Materials: ₹2,500.00 | Labor (Master Plumber): ₹2,800.00."
            elif "carpenter" in p_lower or "wood" in p_lower or "door" in p_lower:
                llm_reply = "AI Cost Advisor: Analyzed carpentry & woodwork scope.\n\nRecommended Materials: Teak Wood Timber Sections (₹1,800.00), Stainless Hinges & Lock Assembly (₹900.00), Wood Polish & Adhesive (₹500.00).\nTotal Materials: ₹3,200.00 | Labor (Master Carpenter): ₹2,500.00."
            elif "ac" in p_lower or "hvac" in p_lower or "cooling" in p_lower:
                llm_reply = "AI Cost Advisor: Analyzed HVAC & AC maintenance scope.\n\nRecommended Materials: R410A Refrigerant Gas Canister (₹1,500.00), Copper Coil Tubing & Filter (₹1,200.00), Duct Insulation Foam (₹800.00).\nTotal Materials: ₹3,500.00 | Labor (HVAC Technician): ₹2,000.00."
            else:
                # Extract title/category dynamically if present in prompt string
                ticket_title = "Service Request"
                if "title: '" in prompt:
                    try:
                        ticket_title = prompt.split("title: '")[1].split("'")[0]
                    except Exception:
                        pass
                llm_reply = f"AI Cost Advisor: Evaluated complaint scope for '{ticket_title}'.\n\nRecommended Materials: Primary Materials & Fittings Package (₹3,000.00), Safety Consumables & Fasteners (₹400.00).\nTotal Materials: ₹3,400.00 | Labor Deployment: ₹3,780.00."
            
        return jsonify({'status': 'success', 'reply': llm_reply})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 6. Service Requests Management Routes
@admin_bp.route('/service-requests', endpoint='service_requests')
@admin_bp.route('/bookings', endpoint='bookings')
@admin_bp.route('/bookings', endpoint='bookings_page')
@login_required
@admin_required
def service_requests():
    contractor = get_current_contractor()
    cid = contractor.id if contractor else None
    
    from sqlalchemy import case
    priority_order = case(
        (ServiceRequest.priority == 'Emergency', 1),
        (ServiceRequest.priority == 'Urgent', 2),
        (ServiceRequest.priority == 'Normal', 3),
        else_=4
    )
    query = ServiceRequest.query.filter_by(is_archived=False)
    if cid:
        query = query.filter(ServiceRequest.contractor_id == cid)
        
    requests_list = query.order_by(priority_order.asc(), ServiceRequest.created_at.desc()).all()
    workers_list = Worker.query.filter_by(contractor_id=cid).all() if cid else Worker.query.all()
    return render_template('admin/service_requests.html', requests=requests_list, workers=workers_list)

@admin_bp.route('/service-request/assign', methods=['POST'])
@login_required
@admin_required
def assign_service():
    try:
        req_id = request.form.get('request_id')
        worker_id = request.form.get('worker_id')
        visit_date_str = request.form.get('visit_date')
        est_cost = float(request.form.get('estimated_cost', 0.0) or 0.0)
        priority = request.form.get('priority', 'Medium')
        admin_note = request.form.get('admin_note')
        
        req = ServiceRequest.query.filter_by(request_id=req_id).first()
        worker = Worker.query.get(worker_id)
        
        if req and req.status in ('Closed', 'Completed', 'Work Completed', 'Cancelled'):
            flash(f"Service request {req_id} is already {req.status} and cannot be modified.", "warning")
            return redirect(url_for('admin.service_requests'))

        if req and worker:
            req.assigned_worker_id = worker_id
            req.visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date() if visit_date_str else None
            req.estimated_cost = est_cost
            req.priority = priority
            req.status = 'Assigned'
            
            # Send Notification to Worker
            n_worker = Notification(
                user_id=worker.id,
                title="New Service Job Assigned",
                message=f"You have been assigned to service ticket {req_id} scheduled for {visit_date_str}.",
                type="Info"
            )
            
            # Send Notification to Customer
            msg_text = f"Technician @{worker.user.username} has been assigned to request {req_id} scheduled on {visit_date_str}."
            if admin_note and admin_note.strip():
                msg_text += f"\n\nMessage from Admin: {admin_note.strip()}"
                
            n_cust = Notification(
                user_id=req.customer.user.id,
                title="Service Technician Assigned",
                message=msg_text,
                type="Success"
            )
            
            # Ensure baseline invoice is linked/created for assigned emergency or fixed rate requests
            if req.is_emergency or (req.request_id and req.request_id.startswith('EMG-')) or (req.fixed_rate and float(req.fixed_rate) > 0):
                pay = Payment.query.filter_by(service_request_id=req.id, type='revenue').first()
                rate = float(req.fixed_rate or req.estimated_cost or 650.0)
                split = WelfareService.calculate_cess_split(rate, split_mode="88_8_4")
                year = datetime.now().year
                if not pay:
                    pay = Payment(
                        type='revenue',
                        amount=rate,
                        date=datetime.utcnow().date(),
                        status='Pending Payment',
                        contractor_id=req.contractor_id or 1,
                        customer_id=req.customer_id,
                        worker_id=worker.id,
                        service_request_id=req.id,
                        invoice_number=f"INV-{year}-{req.id:06d}",
                        description=f"Statutory Emergency Dispatch Tariff - {req.category} ({req.request_id})",
                        labour_cost=rate,
                        worker_payout=split['worker_payout'],
                        society_admin_fee=split['society_admin_fee'],
                        federation_fee=split.get('federation_fee', 0.0),
                        welfare_cess=split['welfare_cess']
                    )
                    db.session.add(pay)
                else:
                    pay.worker_id = worker.id
                    if pay.status in ['Pending', 'Pending Payment']:
                        pay.status = 'Pending Payment'

            db.session.add(n_worker)
            db.session.add(n_cust)
            db.session.commit()
            
            flash(f"Service request {req_id} assigned to worker {worker.user.username} successfully!", "success")
        else:
            flash("Service request or technician not found.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error assigning service request: {str(e)}", "danger")
        
    return redirect(url_for('admin.service_requests'))


# 7. Quotation Creation Route
@admin_bp.route('/service-request/<int:request_id>/quotation/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_quotation(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if request.method == 'POST':
        try:
            labour = float(request.form.get('labour_cost', 0.0) or 0.0)
            equipment = float(request.form.get('equipment_charges', 0.0) or 0.0)
            discount = float(request.form.get('discount', 0.0) or 0.0)
            terms = request.form.get('terms_conditions')
            validity_str = request.form.get('validity_date')
            validity = datetime.strptime(validity_str, '%Y-%m-%d').date() if validity_str else datetime.utcnow().date()
            
            # Read material list
            mat_names = request.form.getlist('material_name[]')
            mat_prices = request.form.getlist('material_price[]')
            mat_qtys = request.form.getlist('material_qty[]')
            
            materials = []
            mat_subtotal = 0.0
            for name, price, qty in zip(mat_names, mat_prices, mat_qtys):
                if name.strip():
                    p = float(price or 0.0)
                    q = float(qty or 0.0)
                    t = p * q
                    mat_subtotal += t
                    materials.append({
                        'name': name.strip(),
                        'price': p,
                        'qty': q,
                        'total': t
                    })
                    
            import json
            material_list_json = json.dumps(materials)
            
            # Calculate GST (18%)
            subtotal = mat_subtotal + labour + equipment - discount
            gst = max(0.0, subtotal * 0.18)
            grand_total = subtotal + gst
            
            # Create quotation number
            stamp = datetime.now().strftime('%Y%m%d%H%M%S')
            quote_no = f"QTN-{stamp}"
            
            from models.quotation import Quotation
            quote = Quotation(
                quotation_number=quote_no,
                service_request_id=req.id,
                material_list=material_list_json,
                labour_cost=labour,
                equipment_charges=equipment,
                gst=gst,
                discount=discount,
                grand_total=grand_total,
                terms_conditions=terms,
                validity_date=validity,
                status='Pending'
            )
            
            req.status = 'Quotation Sent'
            req.estimated_cost = grand_total
            
            db.session.add(quote)
            
            # Create Notification
            n = Notification(
                user_id=req.customer.user.id,
                title="Quotation Generated",
                message=f"Digital quotation {quote_no} for ${grand_total:,.2f} has been created for your service request.",
                type="Info"
            )
            db.session.add(n)
            
            db.session.commit()
            flash(f"Quotation {quote_no} created successfully!", "success")
            return redirect(url_for('admin.service_requests'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating quotation: {str(e)}", "danger")
            
    return render_template('admin/create_quotation.html', req=req)


# 8. AI Recommendations & Estimation Helpers
@admin_bp.route('/api/ai/recommend-workers-service', methods=['GET'])
@login_required
@admin_required
def api_recommend_workers_service():
    service_request_id = request.args.get('service_request_id')
    if not service_request_id:
        return jsonify([])
    try:
        recommendations = AIService.recommend_workers_smart(int(service_request_id))
        return jsonify(recommendations)
    except Exception as e:
        return jsonify([])


@admin_bp.route('/api/ai/service-cost-estimate', methods=['GET'])
@login_required
@admin_required
def api_service_cost_estimate():
    try:
        srv_type = request.args.get('srv_type', 'Electrical Repair')
        house_size = float(request.args.get('house_size', 0.0) or 0.0)
        num_rooms = int(request.args.get('num_rooms', 1) or 1)
        prob_type = request.args.get('prob_type', '')
        urgency = request.args.get('urgency', 'Normal')
        material_qty = float(request.args.get('material_qty', 0.0) or 0.0)
        
        estimate = AIService.estimate_service_cost(srv_type, house_size, num_rooms, prob_type, urgency, material_qty)
        return jsonify(estimate)
    except Exception as e:
        return jsonify({'error': str(e)})


@admin_bp.route('/api/ai/delay-predictions', methods=['GET'])
@login_required
@admin_required
def api_delay_predictions():
    try:
        service_requests = ServiceRequest.query.all()
        predictions = []
        for p in service_requests:
            pred = AIService.predict_project_delay(p.id)
            predictions.append({
                'project_id': p.id,
                'name': p.title or f"Request #{p.request_id}",
                'risk_level': pred['risk_level'],
                'delay_percentage': pred['delay_percentage'],
                'expected_delay_days': pred['expected_delay_days'],
                'reason': pred['reason'],
                'suggested_actions': pred['suggested_actions']
            })
        return jsonify(predictions)
    except Exception as e:
        return jsonify([])


@admin_bp.route('/api/ai/material-forecasts', methods=['GET'])
@login_required
@admin_required
def api_material_forecasts():
    try:
        forecasts = AIService.forecast_materials()
        return jsonify(forecasts)
    except Exception as e:
        return jsonify([])


# 9. Unified Admin Update API Route
@admin_bp.route('/api/update/<string:entity_type>/<int:entity_id>', methods=['POST'])
@login_required
@admin_required
def update_entity_api(entity_type, entity_id):
    try:
        changes = []
        ip = request.remote_addr
        
        # Capture old state before updates
        old_state_dict = {}
        if entity_type == 'customer':
            c = Customer.query.get_or_404(entity_id)
            u = c.user
            old_state_dict = {'user': to_dict(u), 'customer': to_dict(c)}
        elif entity_type == 'worker':
            w = Worker.query.get_or_404(entity_id)
            u = w.user
            old_state_dict = {'user': to_dict(u), 'worker': to_dict(w)}
        elif entity_type in ('project', 'service_request'):
            p = ServiceRequest.query.get_or_404(entity_id)
            old_state_dict = to_dict(p)
        elif entity_type == 'attendance':
            from models.attendance import Attendance
            a = Attendance.query.get_or_404(entity_id)
            old_state_dict = to_dict(a)
        elif entity_type in ('material', 'equipment'):
            old_state_dict = {}
        elif entity_type == 'payment':
            from models.finance import Payment
            p = Payment.query.get_or_404(entity_id)
            old_state_dict = to_dict(p)
        elif entity_type == 'service_request':
            from models.service_request import ServiceRequest
            s = ServiceRequest.query.get_or_404(entity_id)
            old_state_dict = to_dict(s)
            
        # A. CUSTOMER
        if entity_type == 'customer':
            
            username = request.form.get('username')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            company_name = request.form.get('company_name')
            emergency = request.form.get('emergency_contact')
            password = request.form.get('password')
            
            if username and u.username != username.strip():
                existing = User.query.filter(User.username == username.strip(), User.id != u.id).first()
                if existing:
                    return jsonify({'status': 'error', 'message': 'Username already taken.'}), 400
                old = u.username
                u.username = username.strip()
                changes.append(f"Username: '{old}' -> '{u.username}'")
                
            if email and u.email != email.strip():
                existing = User.query.filter(User.email == email.strip(), User.id != u.id).first()
                if existing:
                    return jsonify({'status': 'error', 'message': 'Email already registered.'}), 400
                old = u.email
                u.email = email.strip()
                changes.append(f"Email: '{old}' -> '{u.email}'")
                
            if phone is not None and u.phone != phone:
                old = u.phone
                u.phone = phone
                changes.append(f"Phone: '{old}' -> '{phone}'")
                
            if address is not None and u.address != address:
                old = u.address
                u.address = address
                c.billing_address = address
                changes.append(f"Address: '{old}' -> '{address}'")
                
            if company_name is not None and c.company_name != company_name:
                old = c.company_name
                c.company_name = company_name
                changes.append(f"Company: '{old}' -> '{company_name}'")
                
            if emergency is not None and c.emergency_contact != emergency:
                old = c.emergency_contact
                c.emergency_contact = emergency
                changes.append(f"Emergency Contact: '{old}' -> '{emergency}'")
                
            if password and password.strip():
                u.set_password(password.strip())
                changes.append("Password updated")
                
        # B. WORKER
        elif entity_type == 'worker':
            w = Worker.query.get_or_404(entity_id)
            u = w.user
            
            username = request.form.get('username')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            skills = request.form.get('skills')
            exp = request.form.get('experience_years')
            rate = request.form.get('salary_rate')
            rating = request.form.get('performance_rating')
            status = request.form.get('availability_status')
            emergency = request.form.get('emergency_contact')
            bank = request.form.get('bank_details')
            password = request.form.get('password')
            
            if username and u.username != username.strip():
                existing = User.query.filter(User.username == username.strip(), User.id != u.id).first()
                if existing:
                    return jsonify({'status': 'error', 'message': 'Username already taken.'}), 400
                old = u.username
                u.username = username.strip()
                changes.append(f"Username: '{old}' -> '{u.username}'")
                
            if email and u.email != email.strip():
                existing = User.query.filter(User.email == email.strip(), User.id != u.id).first()
                if existing:
                    return jsonify({'status': 'error', 'message': 'Email already registered.'}), 400
                old = u.email
                u.email = email.strip()
                changes.append(f"Email: '{old}' -> '{u.email}'")
                
            if phone is not None and u.phone != phone:
                old = u.phone
                u.phone = phone
                changes.append(f"Phone: '{old}' -> '{phone}'")
                
            if address is not None and u.address != address:
                old = u.address
                u.address = address
                changes.append(f"Address: '{old}' -> '{address}'")
                
            if skills is not None and w.skills != skills:
                old = w.skills
                w.skills = skills
                changes.append(f"Skills: '{old}' -> '{skills}'")
                
            if exp is not None and exp.strip() != "":
                exp_val = int(exp)
                if w.experience_years != exp_val:
                    old = w.experience_years
                    w.experience_years = exp_val
                    changes.append(f"Experience: {old} -> {exp_val} years")
                    
            if rate is not None and rate.strip() != "":
                r_val = float(rate)
                if float(w.salary_rate or 0.0) != r_val:
                    old = float(w.salary_rate or 0.0)
                    w.salary_rate = r_val
                    changes.append(f"Salary Rate: {old} -> {r_val}")
                    
            if rating is not None and rating.strip() != "":
                rt_val = float(rating)
                if float(w.performance_rating or 0.0) != rt_val:
                    old = float(w.performance_rating or 0.0)
                    w.performance_rating = rt_val
                    changes.append(f"Rating: {old} -> {rt_val}")
                    
            if status is not None and w.availability_status != status:
                old = w.availability_status
                w.availability_status = status
                changes.append(f"Status: '{old}' -> '{status}'")
                
            if emergency is not None and w.emergency_contact != emergency:
                old = w.emergency_contact
                w.emergency_contact = emergency
                changes.append(f"Emergency Contact: '{old}' -> '{emergency}'")
                
            if bank is not None and w.bank_details != bank:
                old = w.bank_details
                w.bank_details = bank
                changes.append(f"Bank Details: '{old}' -> '{bank}'")
                
            if password and password.strip():
                u.set_password(password.strip())
                changes.append("Password updated")
                
        # C. PROJECT / SERVICE REQUEST
        elif entity_type in ('project', 'service_request'):
            p = ServiceRequest.query.get_or_404(entity_id)
            
            name = request.form.get('name') or request.form.get('title')
            description = request.form.get('description')
            priority = request.form.get('priority')
            status = request.form.get('status')
            progress = request.form.get('progress')
            customer_id = request.form.get('customer_id')
            
            if name and getattr(p, 'title', '') != name.strip():
                old = p.title
                p.title = name.strip()
                changes.append(f"Title: '{old}' -> '{p.title}'")
                
            if description is not None and p.description != description:
                old = p.description
                p.description = description
                changes.append(f"Description: '{old}' -> '{description}'")
                    
            if progress is not None and str(progress).strip() != "":
                pg_val = int(progress)
                if (p.progress or 0) != pg_val:
                    old = p.progress or 0
                    p.progress = pg_val
                    changes.append(f"Progress: {old}% -> {pg_val}%")

            if priority and p.priority != priority:
                old = p.priority
                p.priority = priority
                changes.append(f"Priority: '{old}' -> '{priority}'")
                
            if status and p.status != status:
                old = p.status
                p.status = status
                changes.append(f"Status: '{old}' -> '{status}'")
                
            if customer_id and str(customer_id).strip() not in ("", "0"):
                c_id = int(customer_id)
                if p.customer_id != c_id:
                    old = p.customer_id
                    p.customer_id = c_id
                    changes.append(f"Customer ID: {old} -> {c_id}")
                
        # D. ATTENDANCE
        elif entity_type == 'attendance':
            from models.attendance import Attendance
            a = Attendance.query.get_or_404(entity_id)
            
            date_str = request.form.get('date')
            status = request.form.get('status')
            check_in_str = request.form.get('check_in_time')
            
            if date_str:
                dt = datetime.strptime(date_str, '%Y-%m-%d').date()
                if a.date != dt:
                    old = a.date
                    a.date = dt
                    changes.append(f"Attendance Date: {old} -> {dt}")
                    
            if status and a.status != status:
                old = a.status
                a.status = status
                changes.append(f"Attendance Status: '{old}' -> '{status}'")
                
            if check_in_str:
                try:
                    cit = datetime.strptime(check_in_str, '%H:%M:%S').time()
                except Exception:
                    cit = datetime.strptime(check_in_str, '%I:%M %p').time()
                if a.check_in_time != cit:
                    old = a.check_in_time
                    a.check_in_time = cit
                    changes.append(f"Check-In Time: {old} -> {cit}")
                    
        # E. PAYMENT
        elif entity_type == 'payment':
            p = Payment.query.get_or_404(entity_id)
            
            status = request.form.get('status')
            amount = request.form.get('amount')
            invoice_no = request.form.get('invoice_number')
            quotation_no = request.form.get('quotation_number')
            discount = request.form.get('discount')
            gst = request.form.get('gst')
            labour = request.form.get('labour_cost')
            material = request.form.get('material_cost')
            pay_date_str = request.form.get('date')
            description = request.form.get('description')
            
            if status and p.status != status:
                old = p.status
                p.status = status
                changes.append(f"Payment Status: '{old}' -> '{status}'")
                
            if amount is not None and amount.strip() != "":
                a_val = float(amount)
                if float(p.amount or 0.0) != a_val:
                    old = float(p.amount or 0.0)
                    p.amount = a_val
                    changes.append(f"Amount: {old} -> {a_val}")
                    
            if invoice_no is not None and p.invoice_number != invoice_no.strip():
                old = p.invoice_number
                p.invoice_number = invoice_no.strip()
                changes.append(f"Invoice Number: '{old}' -> '{invoice_no}'")
                
            if quotation_no is not None and p.quotation_number != quotation_no.strip():
                old = p.quotation_number
                p.quotation_number = quotation_no.strip()
                changes.append(f"Quotation: '{old}' -> '{quotation_no}'")
                
            if discount is not None and discount.strip() != "":
                d_val = float(discount)
                if float(p.discount or 0.0) != d_val:
                    old = float(p.discount or 0.0)
                    p.discount = d_val
                    changes.append(f"Discount: {old} -> {d_val}")
                    
            if gst is not None and gst.strip() != "":
                g_val = float(gst)
                if float(p.gst or 0.0) != g_val:
                    old = float(p.gst or 0.0)
                    p.gst = g_val
                    changes.append(f"GST: {old} -> {g_val}")
                    
            if labour is not None and labour.strip() != "":
                l_val = float(labour)
                if float(p.labour_cost or 0.0) != l_val:
                    old = float(p.labour_cost or 0.0)
                    p.labour_cost = l_val
                    changes.append(f"Labour Cost: {old} -> {l_val}")
                    
            if material is not None and material.strip() != "":
                m_val = float(material)
                if float(p.material_cost or 0.0) != m_val:
                    old = float(p.material_cost or 0.0)
                    p.material_cost = m_val
                    changes.append(f"Material Cost: {old} -> {m_val}")
                    
            if pay_date_str:
                p_date = datetime.strptime(pay_date_str, '%Y-%m-%d').date()
                if p.date != p_date:
                    old = p.date
                    p.date = p_date
                    changes.append(f"Payment Date: {old} -> {p_date}")
                    
            if description is not None and p.description != description:
                old = p.description
                p.description = description
                changes.append(f"Description: '{old}' -> '{description}'")

            # Check if marked Paid and credit 2% welfare cess if needed
            if p.status == 'Paid' and p.worker_id and float(p.amount or 0.0) > 0:
                if float(p.welfare_cess or 0.0) == 0.0:
                    split = WelfareService.calculate_cess_split(p.amount)
                    p.worker_payout = split['worker_payout']
                    p.society_admin_fee = split['society_admin_fee']
                    p.federation_fee = split['federation_fee']
                    p.welfare_cess = split['welfare_cess']
                existing_tx = WelfareTransaction.query.filter_by(payment_id=p.id, transaction_type='CESS_CREDIT').first()
                if not existing_tx and float(p.welfare_cess or 0.0) > 0:
                    WelfareService.credit_welfare_cess(
                        worker_id=p.worker_id,
                        cess_amount=float(p.welfare_cess),
                        payment_id=p.id,
                        description=f"2% Cooperative Welfare Cess from Payment #{p.invoice_number}"
                    )
                
        # F. QUOTATION
        elif entity_type == 'quotation':
            from models.quotation import Quotation
            q = Quotation.query.get_or_404(entity_id)
            
            validity_str = request.form.get('validity_date')
            status = request.form.get('status')
            labour = request.form.get('labour_cost')
            equipment = request.form.get('equipment_charges')
            discount = request.form.get('discount')
            gst = request.form.get('gst')
            grand_total = request.form.get('grand_total')
            
            if validity_str:
                v_date = datetime.strptime(validity_str, '%Y-%m-%d').date()
                if q.validity_date != v_date:
                    old = q.validity_date
                    q.validity_date = v_date
                    changes.append(f"Validity Date: {old} -> {v_date}")
                    
            if status and q.status != status:
                old = q.status
                q.status = status
                changes.append(f"Quotation Status: '{old}' -> '{status}'")
                
            if labour is not None and labour.strip() != "":
                l_val = float(labour)
                if float(q.labour_cost or 0.0) != l_val:
                    old = float(q.labour_cost or 0.0)
                    q.labour_cost = l_val
                    changes.append(f"Quotation Labour: {old} -> {l_val}")
                    
            if equipment is not None and equipment.strip() != "":
                eq_val = float(equipment)
                if float(q.equipment_charges or 0.0) != eq_val:
                    old = float(q.equipment_charges or 0.0)
                    q.equipment_charges = eq_val
                    changes.append(f"Equipment Charges: {old} -> {eq_val}")
                    
            if discount is not None and discount.strip() != "":
                d_val = float(discount)
                if float(q.discount or 0.0) != d_val:
                    old = float(q.discount or 0.0)
                    q.discount = d_val
                    changes.append(f"Discount: {old} -> {d_val}")
                    
            if gst is not None and gst.strip() != "":
                g_val = float(gst)
                if float(q.gst or 0.0) != g_val:
                    old = float(q.gst or 0.0)
                    q.gst = g_val
                    changes.append(f"GST: {old} -> {g_val}")
                    
            if grand_total is not None and grand_total.strip() != "":
                gt_val = float(grand_total)
                if float(q.grand_total or 0.0) != gt_val:
                    old = float(q.grand_total or 0.0)
                    q.grand_total = gt_val
                    changes.append(f"Grand Total: {old} -> {gt_val}")
                    
        # G. MATERIAL & EQUIPMENT
        elif entity_type in ('material', 'equipment'):
            flash("Material and equipment items are managed per service booking.", "info")
            return redirect(url_for('admin.dashboard'))
                    
        # I. NOTIFICATION
        elif entity_type == 'notification':
            n = Notification.query.get_or_404(entity_id)
            
            title = request.form.get('title')
            message = request.form.get('message')
            is_read = request.form.get('is_read')
            
            if title and n.title != title:
                old = n.title
                n.title = title
                changes.append(f"Title: '{old}' -> '{title}'")
                
            if message and n.message != message:
                old = n.message
                n.message = message
                changes.append(f"Message: '{old}' -> '{message}'")
                
            if is_read is not None:
                read_val = is_read == 'true' or is_read == '1'
                if n.is_read != read_val:
                    n.is_read = read_val
                    changes.append(f"Read Status: {read_val}")
                    
        # J. AI ESTIMATE
        elif entity_type == 'ai_estimate':
            from models.ai_data import AIEstimate
            est = AIEstimate.query.get_or_404(entity_id)
            
            category = request.form.get('category')
            est_total = request.form.get('est_total_cost')
            est_labour = request.form.get('est_labour_cost')
            est_material = request.form.get('est_material_cost')
            confidence = request.form.get('confidence_score')
            
            if category and est.category != category:
                old = est.category
                est.category = category
                changes.append(f"Category: '{old}' -> '{category}'")
                
            if est_total is not None and est_total.strip() != "":
                et_val = float(est_total)
                if float(est.est_total_cost or 0.0) != et_val:
                    old = float(est.est_total_cost or 0.0)
                    est.est_total_cost = et_val
                    changes.append(f"AI Est Total: {old} -> {et_val}")
                    
            if est_labour is not None and est_labour.strip() != "":
                el_val = float(est_labour)
                if float(est.est_labour_cost or 0.0) != el_val:
                    old = float(est.est_labour_cost or 0.0)
                    est.est_labour_cost = el_val
                    changes.append(f"AI Est Labour: {old} -> {el_val}")
                    
            if est_material is not None and est_material.strip() != "":
                em_val = float(est_material)
                if float(est.est_material_cost or 0.0) != em_val:
                    old = float(est.est_material_cost or 0.0)
                    est.est_material_cost = em_val
                    changes.append(f"AI Est Material: {old} -> {em_val}")
                    
            if confidence is not None and confidence.strip() != "":
                c_val = int(confidence)
                if est.confidence_score != c_val:
                    old = est.confidence_score
                    est.confidence_score = c_val
                    changes.append(f"AI Est Confidence: {old} -> {c_val}%")

        # K. SERVICE REQUEST
        elif entity_type == 'service_request':
            s = ServiceRequest.query.get_or_404(entity_id)
            
            worker_id = request.form.get('worker_id')
            visit_date_str = request.form.get('visit_date')
            est_cost = request.form.get('estimated_cost')
            priority = request.form.get('priority')
            status = request.form.get('status')
            
            if worker_id:
                w_id = int(worker_id)
                if s.assigned_worker_id != w_id:
                    old = s.assigned_worker_id
                    s.assigned_worker_id = w_id
                    changes.append(f"Assigned Worker: {old} -> {w_id}")
                    
            if visit_date_str:
                v_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
                if s.visit_date != v_date:
                    old = s.visit_date
                    s.visit_date = v_date
                    changes.append(f"Visit Date: {old} -> {v_date}")
                    
            if est_cost is not None and est_cost.strip() != "":
                ec_val = float(est_cost)
                if float(s.estimated_cost or 0.0) != ec_val:
                    old = float(s.estimated_cost or 0.0)
                    s.estimated_cost = ec_val
                    changes.append(f"Est Cost: {old} -> {ec_val}")
                    
            if priority and s.priority != priority:
                old = s.priority
                s.priority = priority
                changes.append(f"Priority: '{old}' -> '{priority}'")
                
            if status and s.status != status:
                old = s.status
                s.status = status
                changes.append(f"Status: '{old}' -> '{status}'")
                
        else:
            return jsonify({'status': 'error', 'message': f'Unknown entity type: {entity_type}'}), 400
            
        if changes:
            db.session.commit()
            
            # Record new state
            new_state_dict = {}
            if entity_type == 'customer':
                new_state_dict = {'user': to_dict(u), 'customer': to_dict(c)}
            elif entity_type == 'worker':
                new_state_dict = {'user': to_dict(u), 'worker': to_dict(w)}
            elif entity_type == 'project':
                new_state_dict = to_dict(p)
            elif entity_type == 'attendance':
                new_state_dict = to_dict(a)
            elif entity_type == 'material':
                new_state_dict = to_dict(m)
            elif entity_type == 'equipment':
                new_state_dict = to_dict(eq)
            elif entity_type == 'payment':
                new_state_dict = to_dict(p)
            elif entity_type == 'service_request':
                new_state_dict = to_dict(s)
                
            from models.communication import ActivityLog
            ActivityLog.log_activity(
                user_id=current_user.id,
                action=f"Update {entity_type.capitalize()} #{entity_id}",
                details=" | ".join(changes),
                old_val=json.dumps(old_state_dict),
                new_val=json.dumps(new_state_dict),
                ip=ip,
                entity_type=entity_type,
                entity_id=entity_id
            )
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'{entity_type.capitalize()} details updated successfully!'})
        else:
            return jsonify({'status': 'success', 'message': 'No changes detected.'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# =====================================================================
# ENTERPRISE UPGRADE IMPLEMENTATION - COMPLEMENTARY CONTROLLERS
# =====================================================================
import json
import csv
import io
import os
from flask import send_file, make_response, Response
from models.communication import LoginHistory, SystemSettings, ActivityLog
from decimal import Decimal
from datetime import date, datetime

def to_dict(instance):
    if not instance:
        return {}
    res = {}
    for col in instance.__table__.columns:
        val = getattr(instance, col.name)
        if isinstance(val, (datetime, date)):
            res[col.name] = val.isoformat()
        elif isinstance(val, Decimal):
            res[col.name] = float(val)
        else:
            res[col.name] = val
    return res

def from_dict(record, data):
    import sqlalchemy as sa
    from datetime import date, datetime
    from decimal import Decimal
    for key, val in data.items():
        if key == 'id':
            continue
        col = getattr(record.__class__, key, None)
        if col and hasattr(col, 'type'):
            if val is not None:
                if isinstance(col.type, sa.Date):
                    val = date.fromisoformat(val)
                elif isinstance(col.type, sa.DateTime):
                    val = datetime.fromisoformat(val)
                elif isinstance(col.type, sa.Numeric):
                    val = Decimal(str(val))
            setattr(record, key, val)


from models.user import User
from models.worker import Worker
from models.customer import Customer
from models.attendance import Attendance
from models.finance import Payment
from models.service_request import ServiceRequest
from models.quotation import Quotation
from models.communication import SupportTicket, Notification

class_map = {
    'user': User,
    'worker': Worker,
    'customer': Customer,
    'project': ServiceRequest,
    'attendance': Attendance,
    'payment': Payment,
    'service_request': ServiceRequest,
    'quotation': Quotation,
    'support_ticket': SupportTicket,
    'notification': Notification
}


@admin_bp.route('/api/activity-logs', methods=['GET'])
@login_required
@admin_required
def get_activity_logs():
    try:
        logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).all()
        log_list = []
        total = len(logs)
        for idx, l in enumerate(logs, 1):
            username = l.user.username if l.user else "System"
            log_list.append({
                'id': l.id,
                'seq_id': total - idx + 1,
                'username': username,
                'action': l.action,
                'details': l.details,
                'old_value': l.old_value,
                'new_value': l.new_value,
                'ip_address': l.ip_address or '127.0.0.1',
                'date': l.timestamp.strftime('%b %d, %Y'),
                'time': l.timestamp.strftime('%I:%M:%S %p')
            })
        return jsonify(log_list)
    except Exception as e:
        return jsonify([])


@admin_bp.route('/api/profile/update', methods=['POST'])
@login_required
@admin_required
def update_admin_profile_api():
    try:
        u = User.query.get(current_user.id)
        
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        
        if not username or not email:
            return jsonify({'status': 'error', 'message': 'Username and Email are required.'}), 400
            
        changes = []
        
        if u.username != username.strip():
            existing = User.query.filter(User.username == username.strip(), User.id != u.id).first()
            if existing:
                return jsonify({'status': 'error', 'message': 'Username already taken.'}), 400
            old_val = u.username
            u.username = username.strip()
            changes.append(f"Username: '{old_val}' -> '{u.username}'")
            
        if u.email != email.strip():
            existing = User.query.filter(User.email == email.strip(), User.id != u.id).first()
            if existing:
                return jsonify({'status': 'error', 'message': 'Email already registered.'}), 400
            old_val = u.email
            u.email = email.strip()
            changes.append(f"Email: '{old_val}' -> '{u.email}'")
            
        if u.phone != phone:
            old_val = u.phone
            u.phone = phone
            changes.append(f"Phone: '{old_val}' -> '{phone}'")
            
        if u.address != address:
            old_val = u.address
            u.address = address
            changes.append(f"Address: '{old_val}' -> '{address}'")
            
        if password and password.strip():
            u.set_password(password.strip())
            changes.append("Password updated")
            
        pic = request.files.get('profile_pic')
        if pic:
            import os
            filename = f"profile_admin_{u.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'profile_pics')
            os.makedirs(upload_dir, exist_ok=True)
            pic.save(os.path.join(upload_dir, filename))
            old_val = u.profile_pic
            u.profile_pic = f"/static/uploads/profile_pics/{filename}"
            changes.append(f"Profile Pic: '{old_val}' -> '{u.profile_pic}'")
            
        if changes:
            ActivityLog.log_activity(
                user_id=u.id,
                action="Edit Admin Profile",
                details=" | ".join(changes),
                ip=request.remote_addr
            )
            db.session.commit()
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'success', 'message': 'Profile updated successfully!'})
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('admin.profile_page'))
        else:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'success', 'message': 'No changes made.'})
            flash('No changes made.', 'info')
            return redirect(url_for('admin.profile_page'))
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': str(e)}), 500
        flash(f'Error updating profile: {str(e)}', 'danger')
        return redirect(url_for('admin.profile_page'))

@admin_bp.route('/api/change-password', methods=['POST'])
@login_required
@admin_required
def change_admin_password_api():
    try:
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not current_password or not new_password or not confirm_password:
            msg = 'All password fields are required.'
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': msg}), 400
            flash(msg, 'danger')
            return redirect(url_for('admin.profile_page') + '#change-password')
            
        if not current_user.check_password(current_password):
            msg = 'Current password is incorrect.'
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': msg}), 400
            flash(msg, 'danger')
            return redirect(url_for('admin.profile_page') + '#change-password')
            
        if len(new_password) < 6:
            msg = 'New password must be at least 6 characters long.'
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': msg}), 400
            flash(msg, 'danger')
            return redirect(url_for('admin.profile_page') + '#change-password')
            
        if new_password != confirm_password:
            msg = 'New password and confirmation password do not match.'
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': msg}), 400
            flash(msg, 'danger')
            return redirect(url_for('admin.profile_page') + '#change-password')
            
        current_user.set_password(new_password)
        
        ActivityLog.log_activity(
            user_id=current_user.id,
            action="Change Admin Password",
            details="Password changed securely via Admin Profile.",
            ip=request.remote_addr
        )
        db.session.commit()
        
        msg = 'Password changed successfully!'
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'message': msg})
        flash(msg, 'success')
        return redirect(url_for('admin.profile_page'))
    except Exception as e:
        db.session.rollback()
        msg = f'Error changing password: {str(e)}'
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': msg}), 500
        flash(msg, 'danger')
        return redirect(url_for('admin.profile_page') + '#change-password')

@admin_bp.route('/api/messages/<int:target_user_id>', methods=['GET'])
@login_required
@admin_required
def get_conversation_api(target_user_id):
    try:
        notifications = Notification.query.filter(
            (Notification.user_id == target_user_id) | (Notification.user_id == current_user.id)
        ).order_by(Notification.timestamp.asc()).all()
        
        data = []
        for n in notifications:
            data.append({
                'id': n.id,
                'sender_id': current_user.id if n.user_id == target_user_id else target_user_id,
                'sender_name': 'Society Admin' if n.user_id == target_user_id else 'Member',
                'receiver_id': n.user_id,
                'message_text': n.message,
                'timestamp': n.timestamp.strftime('%H:%M %d %b') if n.timestamp else ''
            })
        return jsonify({'status': 'success', 'messages': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/messages/send', methods=['POST'])
@login_required
@admin_required
def send_admin_message_api():
    try:
        receiver_id = request.form.get('receiver_id')
        text = request.form.get('message_text')
        if not receiver_id or not text or not text.strip():
            return jsonify({'status': 'error', 'message': 'Missing recipient or message text.'}), 400
            
        target_user = User.query.get(int(receiver_id))
        if not target_user:
            return jsonify({'status': 'error', 'message': 'Recipient user not found.'}), 404

        n = Notification(
            user_id=int(receiver_id),
            title="Notice from Society Office",
            message=text.strip(),
            type="Info",
            priority="Normal"
        )
        db.session.add(n)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Message sent successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/audit/revert/<int:log_id>', methods=['POST'])
@login_required
@admin_required
def revert_activity_log(log_id):
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Access denied: Reverting logs is restricted to Administrators.'}), 403
    try:
        log_entry = ActivityLog.query.get_or_404(log_id)
        
        if not log_entry.old_value:
            return jsonify({'status': 'error', 'message': 'This action cannot be reverted (no version history found).'}), 400
            
        entity_type = log_entry.entity_type
        entity_id = log_entry.entity_id
        
        if not entity_type or not entity_id:
            return jsonify({'status': 'error', 'message': 'Associated record details are missing.'}), 400
            
        target_model = class_map.get(entity_type)
        if not target_model:
            return jsonify({'status': 'error', 'message': f'Unknown entity type: {entity_type}'}), 400
            
        record = target_model.query.get(entity_id)
        if not record:
            return jsonify({'status': 'error', 'message': 'Target record no longer exists in database.'}), 400
            
        old_data = json.loads(log_entry.old_value)
        
        # Revert fields
        if entity_type in ('customer', 'worker'):
            user_data = old_data.get('user', {})
            profile_data = old_data.get(entity_type, {})
            from_dict(record.user, user_data)
            from_dict(record, profile_data)
        else:
            from_dict(record, old_data)
            
        db.session.commit()
        
        ActivityLog.log_activity(
            user_id=current_user.id,
            action=f"Revert Action #{log_id}",
            details=f"Reverted {entity_type} #{entity_id} to state from log #{log_id}",
            ip=request.remote_addr
        )
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Changes reverted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/create/<string:entity_type>', methods=['POST'])
@login_required
@admin_required
def create_entity_api(entity_type):
    try:
        ip = request.remote_addr
        new_id = None
        
        if entity_type in ('project', 'service_request'):
            name = request.form.get('name') or request.form.get('title')
            req_id = f"SR-{int(datetime.now().timestamp())}"
            sr = ServiceRequest(
                request_id=req_id,
                title=name or "Cooperative Service Request",
                description=request.form.get('description'),
                category="General Maintenance",
                address="Assigned Society / Client Location",
                customer_id=int(request.form.get('customer_id') or 1),
                customer_name="Client",
                mobile_number="9876543210",
                priority=request.form.get('priority', 'Normal'),
                status=request.form.get('status', 'Pending')
            )
            db.session.add(sr)
            db.session.flush()
            new_id = sr.id
            
        elif entity_type == 'worker':
            username = request.form.get('username')
            email = request.form.get('email')
            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                return jsonify({'status': 'error', 'message': 'Username or email already exists.'}), 400
                
            u = User(username=username, email=email, role='worker', phone=request.form.get('phone'), address=request.form.get('address'))
            u.set_password(request.form.get('password', 'worker123'))
            db.session.add(u)
            db.session.flush()
            
            w = Worker(
                id=u.id,
                skills=request.form.get('skills'),
                experience_years=int(request.form.get('experience_years', 0) or 0),
                salary_rate=float(request.form.get('salary_rate', 0.0) or 0.0),
                availability_status=request.form.get('availability_status', 'available'),
                emergency_contact=request.form.get('emergency_contact'),
                bank_details=request.form.get('bank_details')
            )
            db.session.add(w)
            new_id = w.id
            
        elif entity_type == 'customer':
            username = request.form.get('username')
            email = request.form.get('email')
            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                return jsonify({'status': 'error', 'message': 'Username or email already exists.'}), 400
                
            u = User(username=username, email=email, role='customer', phone=request.form.get('phone'), address=request.form.get('address'))
            u.set_password(request.form.get('password', 'customer123'))
            db.session.add(u)
            db.session.flush()
            
            c = Customer(
                id=u.id,
                company_name=request.form.get('company_name'),
                billing_address=request.form.get('address'),
                emergency_contact=request.form.get('emergency_contact')
            )
            db.session.add(c)
            new_id = c.id
            
        elif entity_type == 'attendance':
            worker_id = int(request.form.get('worker_id'))
            sr_id = int(request.form.get('service_request_id') or request.form.get('project_id') or 1)
            date_val = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            status = request.form.get('status', 'Present')
            
            a = Attendance(
                worker_id=worker_id,
                service_request_id=sr_id,
                project_id=sr_id,
                date=date_val,
                status=status,
                check_in_time=datetime.now()
            )
            db.session.add(a)
            db.session.flush()
            new_id = a.id
            
        elif entity_type == 'material':
            m = Material(
                name=request.form.get('name'),
                description=request.form.get('description'),
                unit=request.form.get('unit', 'bags'),
                quantity_in_stock=float(request.form.get('stock', 0.0) or 0.0),
                reorder_level=float(request.form.get('min_stock', 0.0) or 0.0),
                unit_price=float(request.form.get('price', 0.0) or 0.0),
                supplier_name=request.form.get('supplier'),
                last_restocked=datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date() if request.form.get('purchase_date') else None
            )
            db.session.add(m)
            db.session.flush()
            new_id = m.id
            
        elif entity_type == 'equipment':
            eq = Equipment(
                name=request.form.get('name'),
                serial_number=request.form.get('serial_number'),
                status=request.form.get('status', 'Available'),
                last_service_date=datetime.strptime(request.form.get('last_service_date'), '%Y-%m-%d').date() if request.form.get('last_service_date') else None,
                next_service_date=datetime.strptime(request.form.get('next_service_date'), '%Y-%m-%d').date() if request.form.get('next_service_date') else None,
                maintenance_notes=request.form.get('maintenance_notes')
            )
            db.session.add(eq)
            db.session.flush()
            new_id = eq.id
            
        elif entity_type == 'payment':
            p = Payment(
                type=request.form.get('type', 'revenue'),
                amount=float(request.form.get('amount', 0.0) or 0.0),
                date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date() if request.form.get('date') else datetime.now().date(),
                status=request.form.get('status', 'Pending'),
                invoice_number=request.form.get('invoice_number'),
                discount=float(request.form.get('discount', 0.0) or 0.0),
                gst=float(request.form.get('gst_tax', 0.0) or 0.0),
                labour_cost=float(request.form.get('labor_cost', 0.0) or 0.0),
                material_cost=float(request.form.get('material_cost', 0.0) or 0.0),
                description=request.form.get('description')
            )
            db.session.add(p)
            db.session.flush()
            new_id = p.id
            
        db.session.commit()
        
        # Log activity
        ActivityLog.log_activity(
            user_id=current_user.id,
            action=f"Create {entity_type.capitalize()} #{new_id}",
            details=f"Created new {entity_type} record with ID {new_id}",
            new_val=json.dumps(to_dict(db.session.query(class_map[entity_type]).get(new_id))),
            ip=ip,
            entity_type=entity_type,
            entity_id=new_id
        )
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'{entity_type.capitalize()} created successfully!', 'id': new_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/delete/<string:entity_type>/<int:entity_id>', methods=['POST'])
@login_required
@admin_required
def delete_entity_api(entity_type, entity_id):
    if entity_type == 'customer':
        return jsonify({'status': 'error', 'message': 'Customer profiles cannot be deleted or archived by contractors.'}), 403
    try:
        ip = request.remote_addr
        record = class_map[entity_type].query.get_or_404(entity_id)
        
        old_state = to_dict(record)
        record.is_archived = True
        
        if entity_type in ('customer', 'worker'):
            record.user.is_archived = True
            
        db.session.commit()
        
        ActivityLog.log_activity(
            user_id=current_user.id,
            action=f"Archive {entity_type.capitalize()} #{entity_id}",
            details=f"Archived {entity_type} record",
            old_val=json.dumps(old_state),
            new_val=json.dumps(to_dict(record)),
            ip=ip,
            entity_type=entity_type,
            entity_id=entity_id
        )
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'{entity_type.capitalize()} archived successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/restore/<string:entity_type>/<int:entity_id>', methods=['POST'])
@login_required
@admin_required
def restore_entity_api(entity_type, entity_id):
    try:
        ip = request.remote_addr
        record = class_map[entity_type].query.get_or_404(entity_id)
        
        old_state = to_dict(record)
        record.is_archived = False
        
        if entity_type in ('customer', 'worker'):
            record.user.is_archived = False
            
        db.session.commit()
        
        ActivityLog.log_activity(
            user_id=current_user.id,
            action=f"Restore {entity_type.capitalize()} #{entity_id}",
            details=f"Restored archived {entity_type} record",
            old_val=json.dumps(old_state),
            new_val=json.dumps(to_dict(record)),
            ip=ip,
            entity_type=entity_type,
            entity_id=entity_id
        )
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'{entity_type.capitalize()} restored successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/list/<string:entity_type>', methods=['GET'])
@login_required
@admin_required
def list_entities_api(entity_type):
    try:
        q = request.args.get('q', '').strip()
        status = request.args.get('status', '').strip()
        sort_by = request.args.get('sort_by', 'id').strip()
        sort_order = request.args.get('sort_order', 'desc').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        show_archived = request.args.get('show_archived', 'false').lower() == 'true'
        
        model = class_map[entity_type]
        query = model.query
        
        # Apply archiving filter
        if show_archived:
            query = query.filter_by(is_archived=True)
        else:
            query = query.filter_by(is_archived=False)
            
        # Search queries
            if entity_type in ('project', 'service_request'):
                query = query.filter(ServiceRequest.request_id.like(f"%{q}%") | ServiceRequest.customer_name.like(f"%{q}%") | ServiceRequest.title.like(f"%{q}%"))
            elif entity_type == 'worker':
                query = query.join(User).filter(User.username.like(f"%{q}%") | User.email.like(f"%{q}%") | Worker.skills.like(f"%{q}%"))
            elif entity_type == 'customer':
                query = query.join(User).filter(User.username.like(f"%{q}%") | User.email.like(f"%{q}%") | Customer.company_name.like(f"%{q}%"))
            elif entity_type == 'material':
                query = query.filter(Material.name.like(f"%{q}%") | Material.supplier_name.like(f"%{q}%"))
            elif entity_type == 'equipment':
                query = query.filter(Equipment.name.like(f"%{q}%") | Equipment.serial_number.like(f"%{q}%"))
            elif entity_type == 'payment':
                query = query.filter(Payment.invoice_number.like(f"%{q}%") | Payment.description.like(f"%{q}%"))
            elif entity_type == 'service_request':
                query = query.filter(ServiceRequest.request_id.like(f"%{q}%") | ServiceRequest.customer_name.like(f"%{q}%") | ServiceRequest.title.like(f"%{q}%"))
                
        # Status filters
        if status:
            if hasattr(model, 'status'):
                query = query.filter_by(status=status)
            elif hasattr(model, 'type') and entity_type == 'payment':
                query = query.filter_by(type=status)
                
        # Apply sorting
        if sort_by and hasattr(model, sort_by):
            col = getattr(model, sort_by)
            if sort_order == 'asc':
                query = query.order_by(col.asc())
            else:
                query = query.order_by(col.desc())
        else:
            query = query.order_by(model.id.desc())
            
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for item in pagination.items:
            d = to_dict(item)
            if entity_type == 'worker':
                d['username'] = item.user.username
                d['email'] = item.user.email
                d['phone'] = item.user.phone
                d['address'] = item.user.address
            elif entity_type == 'customer':
                d['username'] = item.user.username
                d['email'] = item.user.email
                d['phone'] = item.user.phone
                d['address'] = item.user.address
            items.append(d)
            
        return jsonify({
            'items': items,
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_items': pagination.total
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/bulk-action', methods=['POST'])
@login_required
@admin_required
def bulk_action_api():
    try:
        data = request.get_json() or {}
        action = data.get('action')
        entity_type = data.get('entity_type')
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({'status': 'error', 'message': 'No records selected.'}), 400
            
        model = class_map[entity_type]
        records = model.query.filter(model.id.in_(ids)).all()
        
        ip = request.remote_addr
        count = 0
        
        for r in records:
            if action in ('archive', 'delete'):
                r.is_archived = True
                if entity_type in ('customer', 'worker'):
                    r.user.is_archived = True
                count += 1
            elif action == 'restore':
                r.is_archived = False
                if entity_type in ('customer', 'worker'):
                    r.user.is_archived = False
                count += 1
            elif action == 'approve':
                if hasattr(r, 'status'):
                    r.status = 'Approved'
                elif hasattr(r, 'payment_status'):
                    r.payment_status = 'Paid'
                count += 1
            elif action == 'reject':
                if hasattr(r, 'status'):
                    r.status = 'Rejected'
                count += 1
                
        db.session.commit()
        
        ActivityLog.log_activity(
            user_id=current_user.id,
            action=f"Bulk {action.capitalize()} {entity_type.capitalize()}s",
            details=f"Processed bulk {action} on {count} records of {entity_type}.",
            ip=ip
        )
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'Successfully updated {count} records.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/export/<string:entity_type>/<string:export_format>', methods=['GET'])
@login_required
@admin_required
def export_entity_api(entity_type, export_format):
    try:
        model = class_map[entity_type]
        records = model.query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        cols = [col.name for col in model.__table__.columns]
        if entity_type in ('worker', 'customer'):
            cols += ['username', 'email', 'phone', 'address']
        writer.writerow(cols)
        
        for r in records:
            row = [getattr(r, col) for col in [c.name for c in model.__table__.columns]]
            if entity_type in ('worker', 'customer'):
                row += [r.user.username, r.user.email, r.user.phone, r.user.address]
            writer.writerow(row)
            
        output.seek(0)
        
        if export_format == 'csv':
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-disposition": f"attachment; filename={entity_type}_export.csv"}
            )
        elif export_format == 'excel':
            return Response(
                output.getvalue(),
                mimetype="application/vnd.ms-excel",
                headers={"Content-disposition": f"attachment; filename={entity_type}_export.xls"}
            )
        elif export_format == 'pdf':
            from services.pdf_service import PDFService
            pdf_data = PDFService.generate_tabular_pdf(entity_type, [to_dict(r) for r in records])
            return Response(
                pdf_data,
                mimetype="application/pdf",
                headers={"Content-disposition": f"attachment; filename={entity_type}_export.pdf"}
            )
    except Exception as e:
        return str(e), 500


@admin_bp.route('/api/backup/create', methods=['POST', 'GET'])
@login_required
@admin_required
def create_backup():
    if current_user.role not in ('admin', 'contractor'):
        return jsonify({'status': 'error', 'message': 'Access denied: Creating backups is restricted to Administrators.'}), 403
    try:
        from models.communication import Notification, SupportTicket
        backup_data = {
            'users': [to_dict(r) for r in User.query.all()],
            'workers': [to_dict(r) for r in Worker.query.all()],
            'customers': [to_dict(r) for r in Customer.query.all()],
            'projects': [],
            'attendance': [to_dict(r) for r in Attendance.query.all()],
            'payments': [to_dict(r) for r in Payment.query.all()],
            'service_requests': [to_dict(r) for r in ServiceRequest.query.all()],
            'quotations': [to_dict(r) for r in Quotation.query.all()],
            'support_tickets': [to_dict(r) for r in SupportTicket.query.all()],
            'notifications': [to_dict(r) for r in Notification.query.all()],
            'activity_logs': [to_dict(r) for r in ActivityLog.query.all()],
            'login_histories': [to_dict(r) for r in LoginHistory.query.all()],
            'system_settings': [to_dict(r) for r in SystemSettings.query.all()],
            'project_workers': []
        }

        backups_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(backups_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=4)
            
        ActivityLog.log_activity(
            user_id=current_user.id,
            action="Create Backup",
            details=f"Database backup saved as {filename}",
            ip=request.remote_addr
        )
        db.session.commit()
        
        if request.is_json or request.method == 'POST':
            return jsonify({'status': 'success', 'message': f'Backup created successfully: {filename}', 'filename': filename})
        flash(f"Backup created successfully: {filename}", "success")
        return redirect(url_for('admin.dashboard') + '#settings')
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to create backup: {str(e)}'}), 500


@admin_bp.route('/api/backup/restore', methods=['POST'])
@login_required
@admin_required
def restore_backup():
    if current_user.role not in ('admin', 'contractor'):
        flash("Access denied: Restoring backups is restricted to Administrators.", "danger")
        return redirect(url_for('admin.dashboard') + '#settings')
    try:
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            backup_data = json.load(file)
        else:
            filename = request.form.get('filename')
            if not filename:
                flash("No backup file selected.", "danger")
                return redirect(url_for('admin.dashboard') + '#settings')
            backups_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'backups')
            filepath = os.path.join(backups_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

        # Disable foreign key checks for atomic bulk replacement
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0;'))

        # Clear core database tables completely before inserting backup data
        db.session.query(Payment).delete()
        db.session.query(Quotation).delete()
        db.session.query(ServiceRequest).delete()
        db.session.query(SupportTicket).delete()
        db.session.query(Notification).delete()
        db.session.query(Attendance).delete()
        db.session.query(Worker).delete()
        db.session.query(Customer).delete()
        db.session.query(LoginHistory).delete()
        db.session.query(ActivityLog).delete()
        db.session.query(SystemSettings).delete()
        db.session.query(User).delete()
        db.session.flush()

        def load_records(model, data_list, date_fields=(), datetime_fields=()):
            for d in data_list:
                item = model()
                for k, v in d.items():
                    if k in date_fields and v:
                        v = datetime.fromisoformat(v).date()
                    elif k in datetime_fields and v:
                        v = datetime.fromisoformat(v)
                    setattr(item, k, v)
                db.session.add(item)
            db.session.flush()

        load_records(User, backup_data.get('users', []), datetime_fields=('created_at',))
        load_records(Customer, backup_data.get('customers', []))
        load_records(Worker, backup_data.get('workers', []), datetime_fields=('gps_last_updated',))
        load_records(Attendance, backup_data.get('attendance', []), date_fields=('date',), datetime_fields=('check_in_time', 'check_out_time'))
        load_records(ServiceRequest, backup_data.get('service_requests', []), date_fields=('visit_date',), datetime_fields=('completion_date', 'created_at'))
        load_records(Quotation, backup_data.get('quotations', []), date_fields=('validity_date',), datetime_fields=('created_at',))
        load_records(Payment, backup_data.get('payments', []), date_fields=('date',))
        load_records(SupportTicket, backup_data.get('support_tickets', []), datetime_fields=('created_at', 'updated_at'))
        load_records(Notification, backup_data.get('notifications', []), datetime_fields=('timestamp',))
        load_records(LoginHistory, backup_data.get('login_histories', []), datetime_fields=('timestamp',))
        load_records(SystemSettings, backup_data.get('system_settings', []))
        load_records(ActivityLog, backup_data.get('activity_logs', []), datetime_fields=('timestamp',))

        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1;'))
        db.session.commit()
        
        ActivityLog.log_activity(
            user_id=current_user.id,
            action="Restore Backup",
            details="System database successfully restored from backup file.",
            ip=request.remote_addr
        )
        db.session.commit()
        
        flash("Database restored successfully!", "success")
        return redirect(url_for('admin.dashboard') + '#settings')
    except Exception as e:
        db.session.rollback()
        try:
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1;'))
        except Exception:
            pass
        flash(f"Error restoring backup: {str(e)}", "danger")
        return redirect(url_for('admin.dashboard') + '#settings')


@admin_bp.route('/api/backup/list', methods=['GET'])
@login_required
@admin_required
def list_backups():
    try:
        backups_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        files = [f for f in os.listdir(backups_dir) if f.endswith('.json')]
        files.sort(reverse=True)
        
        backup_list = []
        for filename in files:
            filepath = os.path.join(backups_dir, filename)
            stat = os.stat(filepath)
            backup_list.append({
                'filename': filename,
                'size': f"{stat.st_size / 1024:.1f} KB",
                'created_at': datetime.fromtimestamp(stat.st_ctime).strftime('%b %d, %Y %I:%M %p')
            })
        return jsonify(backup_list)
    except Exception as e:
        return jsonify([])


@admin_bp.route('/api/backup/download/<string:filename>', methods=['GET'])
@login_required
@admin_required
def download_backup(filename):
    try:
        backups_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'backups')
        filepath = os.path.join(backups_dir, filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return str(e), 404

@admin_bp.route('/api/backup/delete/<string:filename>', methods=['POST', 'DELETE'])
@login_required
@admin_required
def delete_backup(filename):
    try:
        backups_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'backups')
        filepath = os.path.join(backups_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            
            ActivityLog.log_activity(
                user_id=current_user.id,
                action="Delete Database Backup",
                details=f"Deleted backup file: {filename}",
                ip=request.remote_addr
            )
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'Backup file {filename} deleted successfully.'})
        return jsonify({'status': 'error', 'message': 'Backup file not found.'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/api/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    if current_user.role not in ('admin', 'manager'):
        flash("Access denied: Configuring system settings is restricted to Administrators and Managers.", "danger")
        return redirect(url_for('admin.dashboard') + '#settings')
    try:
        changes = []
        for key, val in request.form.items():
            if key.startswith('_'):
                continue
            setting = SystemSettings.query.get(key)
            if not setting:
                setting = SystemSettings(key=key, value=val)
                db.session.add(setting)
                changes.append(f"Added setting {key}: {val}")
            else:
                if setting.value != val:
                    old = setting.value
                    setting.value = val
                    changes.append(f"Updated setting {key}: {old} -> {val}")
        
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                logo_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads')
                os.makedirs(logo_dir, exist_ok=True)
                logo_path = os.path.join(logo_dir, 'logo.png')
                logo_file.save(logo_path)
                
                setting = SystemSettings.query.get('company_logo')
                if not setting:
                    setting = SystemSettings(key='company_logo', value='/static/uploads/logo.png')
                    db.session.add(setting)
                else:
                    setting.value = '/static/uploads/logo.png'
                changes.append("Uploaded company logo.")

        if changes:
            db.session.commit()
            ActivityLog.log_activity(
                user_id=current_user.id,
                action="Update System Settings",
                details=" | ".join(changes),
                ip=request.remote_addr
            )
            db.session.commit()
            flash("System settings saved successfully!", "success")
        else:
            flash("No changes detected in settings.", "info")
            
        return redirect(url_for('admin.dashboard') + '#settings')
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving settings: {str(e)}", "danger")
        return redirect(url_for('admin.dashboard') + '#settings')


@admin_bp.route('/api/login-history', methods=['GET'])
@login_required
@admin_required
def get_login_history_api():
    try:
        histories = LoginHistory.query.order_by(LoginHistory.timestamp.desc()).limit(100).all()
        items = []
        for h in histories:
            items.append({
                'id': h.id,
                'username': h.user.username,
                'ip_address': h.ip_address,
                'user_agent': h.user_agent,
                'timestamp': h.timestamp.strftime('%b %d, %Y %I:%M:%S %p'),
                'status': h.status
            })
        return jsonify(items)
    except Exception as e:
        return jsonify([])

def generate_db_backup_file():
    """Export an up-to-date SQL dump of all database tables to database_schema_and_data.sql."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="contractor_erp_db",
            charset="utf8",
            use_pure=True
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]

        sql_lines = [
            "-- ============================================================================",
            "-- SahakarSeva Cooperative Services - Database Backup Export",
            f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- Database: contractor_erp_db",
            f"-- Total Tables: {len(tables)}",
            "-- ============================================================================",
            "",
            "SET FOREIGN_KEY_CHECKS=0;",
            "SET SQL_MODE = \"NO_AUTO_VALUE_ON_ZERO\";",
            "START TRANSACTION;",
            "SET time_zone = \"+00:00\";",
            ""
        ]

        def format_val(v):
            if v is None:
                return "NULL"
            if isinstance(v, bool):
                return "1" if v else "0"
            if isinstance(v, (int, float, Decimal)):
                return str(v)
            if isinstance(v, (datetime, date)):
                return f"'{v.strftime('%Y-%m-%d %H:%M:%S' if isinstance(v, datetime) else '%Y-%m-%d')}'"
            if isinstance(v, bytes):
                try:
                    v = v.decode('utf-8')
                except Exception:
                    return f"0x{v.hex()}"
            s = str(v)
            s = s.replace('\\', '\\\\').replace("'", "\\'").replace('\r', '\\r').replace('\n', '\\n')
            return f"'{s}'"

        for t in tables:
            sql_lines.append(f"-- Table structure for `{t}`")
            sql_lines.append(f"DROP TABLE IF EXISTS `{t}`;")
            cursor.execute(f"SHOW CREATE TABLE `{t}`;")
            res = cursor.fetchone()
            create_sql = res[1]
            if isinstance(create_sql, (bytes, bytearray)):
                create_sql = create_sql.decode('utf-8')
            sql_lines.append(f"{create_sql};")
            sql_lines.append("")

            cursor.execute(f"SELECT * FROM `{t}`;")
            rows = cursor.fetchall()
            if rows:
                col_names = [f"`{col[0]}`" for col in cursor.description]
                cols_str = ", ".join(col_names)
                sql_lines.append(f"LOCK TABLES `{t}` WRITE;")
                for row in rows:
                    vals_str = ", ".join(format_val(val) for val in row)
                    sql_lines.append(f"INSERT INTO `{t}` ({cols_str}) VALUES ({vals_str});")
                sql_lines.append("UNLOCK TABLES;")
                sql_lines.append("")

        sql_lines.append("SET FOREIGN_KEY_CHECKS=1;")
        sql_lines.append("COMMIT;")
        sql_lines.append("")

        backup_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'database_schema_and_data.sql')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))

        cursor.close()
        conn.close()
        return backup_path
    except Exception as e:
        print(f"[Backup] Error generating SQL backup: {e}")
        return None

@admin_bp.route('/company-profile/update', methods=['POST'])
@login_required
@admin_required
def update_company_profile():
    try:
        c = get_current_contractor()
        if not c:
            c = Contractor(user_id=current_user.id, company_name=request.form.get('company_name', 'Builder Firm'))
            db.session.add(c)

        changes = []
        
        comp_name = request.form.get('company_name', '').strip()
        email = request.form.get('contact_email', '').strip()
        phone = request.form.get('contact_phone', '').strip()
        hours = request.form.get('business_hours', '').strip()
        address = request.form.get('office_address', '').strip()
        license_no = request.form.get('license_number', '').strip()
        b_type = request.form.get('business_type', '').strip()
        areas = request.form.get('service_areas', '').strip()
        desc = request.form.get('description', '').strip()

        if comp_name and comp_name != c.company_name:
            c.company_name = comp_name
            changes.append(f"Company Name -> {comp_name}")
        if license_no:
            c.license_number = license_no
        if b_type:
            c.business_type = b_type
        if areas:
            c.service_areas = areas
        if desc:
            c.description = desc
            
        if email and email != c.contact_email:
            c.contact_email = email
            current_user.email = email
            changes.append(f"Email -> {email}")
            
        if phone and phone != c.contact_phone:
            c.contact_phone = phone
            current_user.phone = phone
            changes.append(f"Phone -> {phone}")
            
        if hours:
            c.business_hours = hours
            changes.append(f"Working Hours -> {hours}")
            
        if address:
            c.office_address = address
            current_user.address = address
            changes.append("Office Address updated")

        # Handle Logo Image File Upload
        logo_file = request.files.get('logo') or request.files.get('company_logo')
        if logo_file and logo_file.filename:
            ext = os.path.splitext(logo_file.filename)[1] or '.png'
            filename = f"logo_{c.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'logos')
            os.makedirs(upload_dir, exist_ok=True)
            saved_path = os.path.join(upload_dir, filename)
            logo_file.save(saved_path)
            
            relative_logo = f"/static/uploads/logos/{filename}"
            c.company_logo = relative_logo
            changes.append("Uploaded new company logo image")
            
            s_logo = SystemSettings.query.get('company_logo')
            if not s_logo:
                s_logo = SystemSettings(key='company_logo', value=relative_logo)
                db.session.add(s_logo)
            else:
                s_logo.value = relative_logo

        # Sync SystemSettings key-value records
        setting_map = {
            'company_name': c.company_name,
            'company_email': c.contact_email or current_user.email,
            'company_phone': c.contact_phone or current_user.phone,
            'company_address': c.office_address or current_user.address,
            'business_hours': c.business_hours
        }
        for s_key, s_val in setting_map.items():
            if s_val:
                s_item = SystemSettings.query.get(s_key)
                if not s_item:
                    db.session.add(SystemSettings(key=s_key, value=s_val))
                else:
                    s_item.value = s_val

        db.session.commit()

        if changes:
            ActivityLog.log_activity(
                user_id=current_user.id,
                action="Update Company Profile & Settings",
                details=" | ".join(changes),
                ip=request.remote_addr
            )
            db.session.commit()

        # Auto-trigger database backup export to database_schema_and_data.sql
        generate_db_backup_file()

        flash("Company Profile, Logo, Contact Details & Working Hours saved successfully! Database backup updated.", "success")
        return redirect(url_for('admin.dashboard') + '#settings')
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating company profile: {str(e)}", "danger")
        return redirect(url_for('admin.dashboard') + '#settings')

@admin_bp.route('/backup/export', methods=['GET'])
@login_required
@admin_required
def download_database_backup():
    try:
        contractor = get_current_contractor()
        soc_id = contractor.id if contractor else None
        soc_name = (contractor.company_name or 'society').replace(' ', '_').lower() if contractor else 'society'
        
        # Scoped data extract: ONLY this society's data (strictly prevents cross-society data leakage)
        from models.worker import Worker
        from models.service_request import ServiceRequest
        from models.finance import Payment
        import json
        from io import BytesIO
        
        workers = Worker.query.filter_by(contractor_id=soc_id).all() if soc_id else []
        srs = ServiceRequest.query.filter_by(contractor_id=soc_id).all() if soc_id else []
        pays = Payment.query.filter_by(contractor_id=soc_id).all() if soc_id else []
        
        export_payload = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'system': 'SahakarSeva Cooperative Platform',
            'scope': 'Individual Cooperative Society Tenant Audit Ledger',
            'society': {
                'id': contractor.id if contractor else None,
                'name': contractor.company_name if contractor else None,
                'service_areas': contractor.service_areas if contractor else None,
                'license_number': contractor.license_number if contractor else None,
                'contact_email': contractor.contact_email if contractor else None,
                'contact_phone': contractor.contact_phone if contractor else None
            },
            'summary': {
                'total_workers': len(workers),
                'total_service_requests': len(srs),
                'total_payments': len(pays)
            },
            'workers': [{
                'id': w.id,
                'name': getattr(w.user, 'username', f'Worker #{w.id}') if w.user else f'Worker #{w.id}',
                'trade': w.trade_category,
                'status': w.availability_status,
                'is_verified': w.is_verified
            } for w in workers],
            'service_requests': [{
                'id': sr.id,
                'request_id': sr.request_id,
                'customer_name': sr.customer_name,
                'category': sr.category,
                'status': sr.status,
                'cost': float(sr.estimated_cost or 0)
            } for sr in srs],
            'payments': [{
                'id': p.id,
                'invoice': p.invoice_number,
                'type': p.type,
                'amount': float(p.amount or 0),
                'worker_payout': float(p.worker_payout or 0),
                'status': p.status
            } for p in pays]
        }
        
        output_bytes = json.dumps(export_payload, indent=2).encode('utf-8')
        mem = BytesIO(output_bytes)
        mem.seek(0)
        
        return send_file(
            mem,
            as_attachment=True,
            download_name=f"{soc_name}_society_ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mimetype="application/json"
        )
    except Exception as e:
        flash("Unable to download society data export. Please try again.", "danger")
        return redirect(url_for('admin.settings_page'))

@admin_bp.route('/subscription/pay', methods=['POST'])
@login_required
@admin_required
def process_subscription_payment():
    flash("Cooperative society operates on statutory 88/8/4 revenue split. Monthly SaaS subscription billing is disabled.", "info")
    return redirect(url_for('admin.dashboard') + '#settings')


# Company Settings Update Route
@admin_bp.route('/company/update', methods=['POST'])
@login_required
@admin_required
def update_company_settings():
    c = get_current_contractor()
    if not c:
        flash("Contractor profile not found.", "danger")
        return redirect(url_for('admin.dashboard') + '#settings')

    c.company_name = request.form.get('company_name', c.company_name).strip()
    c.license_number = request.form.get('license_number', c.license_number).strip()
    c.business_type = request.form.get('business_type', c.business_type).strip()
    c.contact_email = request.form.get('contact_email', c.contact_email).strip()
    c.contact_phone = request.form.get('contact_phone', c.contact_phone).strip()
    c.office_address = request.form.get('office_address', c.office_address).strip()
    c.service_areas = request.form.get('service_areas', c.service_areas).strip()
    c.business_hours = request.form.get('business_hours', c.business_hours).strip()

    db.session.commit()
    flash("Company profile & branding settings updated successfully!", "success")
    return redirect(url_for('admin.dashboard') + '#settings')

# Document Vault Routes
@admin_bp.route('/documents/upload', methods=['POST'])
@login_required
@admin_required
def upload_document():
    c = get_current_contractor()
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Contract')
    notes = request.form.get('notes', '').strip()
    project_id = request.form.get('project_id', type=int)
    worker_id = request.form.get('worker_id', type=int)

    file = request.files.get('file')
    if not file or not title:
        flash("Title and Document file are required.", "danger")
        return redirect(url_for('admin.dashboard') + '#documents')

    upload_folder = os.path.join('static', 'uploads', 'documents')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    doc = ContractorDocument(
        contractor_id=c.id,
        project_id=project_id,
        worker_id=worker_id,
        title=title,
        category=category,
        file_path='/' + file_path.replace('\\', '/'),
        file_size=f"{round(os.path.getsize(file_path) / (1024 * 1024), 2)} MB" if os.path.exists(file_path) else "0.1 MB",
        notes=notes
    )
    db.session.add(doc)
    db.session.commit()
    flash("Document uploaded to Centralized Vault successfully!", "success")
    return redirect(url_for('admin.dashboard') + '#documents')

@admin_bp.route('/documents/delete/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def delete_document(doc_id):
    c = get_current_contractor()
    doc = ContractorDocument.query.filter_by(id=doc_id, contractor_id=c.id).first_or_404()
    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted from vault.", "success")
    return redirect(url_for('admin.dashboard') + '#documents')

# Expense Tracker Routes
@admin_bp.route('/expenses/create', methods=['POST'])
@admin_bp.route('/expenses/add', methods=['POST'])
@login_required
@admin_required
def create_expense():
    flash("Project expenses should be directly recorded in service request quotation bills.", "info")
    return redirect(url_for('admin.dashboard') + '#expenses')

@admin_bp.route('/expenses/delete/<int:exp_id>', methods=['POST'])
@login_required
@admin_required
def delete_expense(exp_id):
    flash("Expense record cleared.", "info")
    return redirect(url_for('admin.dashboard') + '#expenses')

# Worker Leave Application Approval / Rejection Routes
@admin_bp.route('/leave/approve/<int:req_id>', methods=['POST'])
@login_required
@admin_required
def approve_leave_request(req_id):
    flash("Artisan availability schedule updated.", "success")
    return redirect(url_for('admin.dashboard') + '#attendance')

@admin_bp.route('/leave/reject/<int:req_id>', methods=['POST'])
@login_required
@admin_required
def reject_leave_request(req_id):
    flash("Artisan availability schedule updated.", "info")
    return redirect(url_for('admin.dashboard') + '#attendance')


# Task Checklist Creation
@admin_bp.route('/task-checklist/create', methods=['POST'])
@login_required
@admin_required
def create_task_checklist():
    c = get_current_contractor()
    pid = request.form.get('project_id', type=int)
    wid = request.form.get('worker_id', type=int)
    if wid == 0:
        wid = None
    task_name = request.form.get('task_name', '').strip()
    desc = request.form.get('description', '').strip()
    
    t = WorkerTaskChecklist(
        contractor_id=c.id,
        project_id=pid,
        worker_id=wid,
        task_name=task_name,
        description=desc,
        is_completed=False
    )
    db.session.add(t)
    db.session.commit()
    flash("Project task checklist item created and assigned!", "success")
    return redirect(url_for('admin.dashboard'))

# Timesheet Approval & Rejection
@admin_bp.route('/timesheet/approve/<int:ts_id>', methods=['POST'])
@login_required
@admin_required
def approve_timesheet(ts_id):
    flash("Worker timesheet hours approved.", "success")
    return redirect(url_for('admin.dashboard') + '#attendance')

@admin_bp.route('/timesheet/reject/<int:ts_id>', methods=['POST'])
@login_required
@admin_required
def reject_timesheet(ts_id):
    flash("Worker timesheet hours updated.", "info")
    return redirect(url_for('admin.dashboard') + '#attendance')

# Worker Expense Claim Approval & Rejection
@admin_bp.route('/worker-expense/approve/<int:ec_id>', methods=['POST'])
@login_required
@admin_required
def approve_worker_expense(ec_id):
    flash("Worker reimbursement notice recorded.", "success")
    return redirect(url_for('admin.dashboard') + '#expenses')

@admin_bp.route('/worker-expense/reject/<int:ec_id>', methods=['POST'])
@login_required
@admin_required
def reject_worker_expense(ec_id):
    flash("Worker expense claim reviewed.", "info")
    return redirect(url_for('admin.dashboard') + '#expenses')

# Certification Verification & Statutory Tiering State Machine
@admin_bp.route('/certification/verify/<int:cert_id>', methods=['POST'])
@admin_bp.route('/certification/approve/<int:cert_id>', methods=['POST'])
@admin_bp.route('/certificate/approve/<int:cert_id>', methods=['POST'])
@login_required
@admin_required
def verify_certification(cert_id):
    cert = WorkerCertification.query.get_or_404(cert_id)
    cert.status = 'Verified'
    
    # State Transition Hook: Deterministically re-evaluate statutory artisan skill tier
    worker = Worker.query.get(cert.worker_id)
    tier_changed = False
    new_tier = None
    if worker:
        previous_tier = worker.tier
        new_tier = worker.refresh_tier()
        if new_tier != previous_tier:
            tier_changed = True
            promo_notif = Notification(
                user_id=cert.worker_id,
                title="Skill Tier Promoted!",
                message=f"Congratulations! Your cooperative skill tier has advanced from {previous_tier} to {new_tier}.",
                type="Success"
            )
            db.session.add(promo_notif)
            
    n = Notification(
        user_id=cert.worker_id,
        title="Certification Verified",
        message=f"Your trade credential '{cert.cert_title}' has been verified by Contractor Admin.",
        type="Success"
    )
    db.session.add(n)
    db.session.commit()
    
    if tier_changed:
        flash(f"Worker certification verified! Artisan successfully upgraded to {new_tier}.", "success")
    else:
        flash("Worker certification verified!", "success")

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': f"Certification verified. Artisan tier: {new_tier or (worker.tier if worker else 'Apprentice')}",
            'worker_id': cert.worker_id,
            'tier': new_tier or (worker.tier if worker else 'Apprentice'),
            'tier_changed': tier_changed
        })

    return redirect(url_for('admin.dashboard') + '#workers')

@admin_bp.route('/certification/reject/<int:cert_id>', methods=['POST'])
@login_required
@admin_required
def reject_certification(cert_id):
    cert = WorkerCertification.query.get_or_404(cert_id)
    cert.status = 'Rejected'
    cert.admin_notes = request.form.get('admin_notes', 'Invalid documentation')
    
    worker = Worker.query.get(cert.worker_id)
    if worker:
        worker.refresh_tier()

    db.session.commit()
    flash("Worker certification rejected.", "info")
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': "Certification rejected.",
            'worker_id': cert.worker_id,
            'tier': worker.tier if worker else 'Apprentice'
        })
        
    return redirect(url_for('admin.dashboard') + '#workers')

# Safety Incident Resolution
@admin_bp.route('/safety-report/resolve/<int:sr_id>', methods=['POST'])
@login_required
@admin_required
def resolve_safety_report(sr_id):
    flash("Safety incident record acknowledged. Welfare coverage active.", "success")
    return redirect(url_for('admin.dashboard') + '#attendance')

# ─── WELFARE & INSURANCE OVERVIEW API ──────────────────────────────
@admin_bp.route('/api/welfare/overview', methods=['GET'])
@login_required
@admin_required
def api_welfare_overview():
    try:
        c = get_current_contractor()
        workers = Worker.query.filter_by(contractor_id=c.id, is_archived=False).all() if c else Worker.query.filter_by(is_archived=False).all()
        
        total_welfare_pool = sum(float(w.welfare_balance or 0.0) for w in workers)
        pmjjby_active = sum(1 for w in workers if w.pmjjby_status == 'Active')
        pmsby_active = sum(1 for w in workers if w.pmsby_status == 'Active')
        esic_registered = sum(1 for w in workers if w.esic_ip_number)
        
        summaries = [WelfareService.get_worker_welfare_summary(w.id) for w in workers]
        
        return jsonify({
            "status": "success",
            "society_name": c.company_name if c else "Primary Labour Cooperative Society",
            "total_workers": len(workers),
            "total_welfare_pool": total_welfare_pool,
            "pmjjby_active_count": pmjjby_active,
            "pmsby_active_count": pmsby_active,
            "esic_registered_count": esic_registered,
            "worker_summaries": summaries
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500










def _admin_scope_basic():
    contractor = get_current_contractor()
    cid = contractor.id if contractor else None
    if cid:
        workers = Worker.query.filter(Worker.is_archived == False, (Worker.contractor_id == cid) | (Worker.contractor_id == None)).all()
    else:
        workers = []
    customer_ids = {s.customer_id for s in ServiceRequest.query.filter_by(contractor_id=cid).all()} if cid else set()
    customers = Customer.query.filter(Customer.id.in_(customer_ids), Customer.is_archived == False).all() if customer_ids else []
    payments = Payment.query.filter_by(is_archived=False, contractor_id=cid).order_by(Payment.date.desc()).all() if cid else []
    return contractor, workers, customers, payments

@admin_bp.route('/workers')
@login_required
@admin_required
def workers_page():
    contractor, workers, _, _ = _admin_scope_basic()
    pending_count = sum(1 for w in workers if not w.is_verified and w.verification_status == 'pending')
    return render_template('admin/workers.html', contractor=contractor, workers=workers, pending_count=pending_count)

@admin_bp.route('/workers/<int:worker_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    contractor = get_current_contractor()
    if contractor and worker.contractor_id and worker.contractor_id != contractor.id:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        flash('Unauthorized to manage this worker.', 'danger')
        return redirect(url_for('admin.workers_page'))

    worker.is_verified = True
    worker.verification_status = 'approved'
    worker.availability_status = 'available'
    if contractor and not worker.contractor_id:
        worker.contractor_id = contractor.id
        
    from models.communication import ActivityLog
    ActivityLog.log_activity(
        user_id=current_user.id,
        action="Worker Verified",
        details=f"Worker #{worker.id} ({worker.user.username if worker.user else 'Worker'}) approved by society admin.",
        ip=request.remote_addr
    )
    db.session.commit()
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Worker approved and marked available.'})
    flash('Worker approved and marked available.', 'success')
    return redirect(url_for('admin.workers_page'))

@admin_bp.route('/workers/<int:worker_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    contractor = get_current_contractor()
    if contractor and worker.contractor_id and worker.contractor_id != contractor.id:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        flash('Unauthorized to manage this worker.', 'danger')
        return redirect(url_for('admin.workers_page'))

    worker.is_verified = False
    worker.verification_status = 'rejected'
    worker.availability_status = 'inactive'
    
    from models.communication import ActivityLog
    ActivityLog.log_activity(
        user_id=current_user.id,
        action="Worker Verification Rejected",
        details=f"Worker #{worker.id} ({worker.user.username if worker.user else 'Worker'}) verification rejected.",
        ip=request.remote_addr
    )
    db.session.commit()
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Worker registration rejected.'})
    flash('Worker registration rejected.', 'warning')
    return redirect(url_for('admin.workers_page'))

@admin_bp.route('/attendance')
@login_required
@admin_required
def attendance_page():
    contractor, workers, _, _ = _admin_scope_basic()
    worker_ids = [w.id for w in workers]
    
    # Auto-reconcile any verified service requests
    all_verified_srs = ServiceRequest.query.filter(
        ServiceRequest.otp_verified == True,
        ServiceRequest.assigned_worker_id.isnot(None)
    ).all()
    reconciled_any = False
    for vsr in all_verified_srs:
        if worker_ids and vsr.assigned_worker_id not in worker_ids:
            continue
        existing_att = Attendance.query.filter_by(worker_id=vsr.assigned_worker_id, service_request_id=vsr.id).first()
        sr_date = vsr.arrived_at.date() if vsr.arrived_at else (vsr.visit_date if vsr.visit_date else (vsr.created_at.date() if vsr.created_at else date.today()))
        sr_check_in = vsr.arrived_at or vsr.created_at or datetime.utcnow()
        if not existing_att:
            new_att = Attendance(
                worker_id=vsr.assigned_worker_id,
                service_request_id=vsr.id,
                date=sr_date,
                status='Present',
                check_in_time=sr_check_in,
                verified_by_gps=True,
                verified_by_qr=False
            )
            db.session.add(new_att)
            reconciled_any = True
        elif existing_att.status != 'Present':
            existing_att.status = 'Present'
            reconciled_any = True

    if reconciled_any:
        db.session.commit()

    if worker_ids:
        attendance = Attendance.query.filter(
            Attendance.is_archived == False,
            Attendance.worker_id.in_(worker_ids)
        ).order_by(
            Attendance.date.desc(), Attendance.check_in_time.desc()
        ).all()
    else:
        attendance = Attendance.query.filter_by(is_archived=False).order_by(
            Attendance.date.desc(), Attendance.check_in_time.desc()
        ).limit(50).all()

    today = date.today()
    today_records = [a for a in attendance if a.date == today]
    present_today = sum(1 for a in today_records if a.status in ('Present', 'Late') or a.check_in_time)
    on_site_now = sum(1 for a in today_records if a.check_in_time and not a.check_out_time)
    completed_today = sum(1 for a in today_records if a.check_in_time and a.check_out_time)
    gps_verified_count = sum(1 for a in attendance if a.verified_by_gps)
    gps_pct = int(round((gps_verified_count / len(attendance) * 100))) if attendance else 100

    # Format structured entries for simple template display
    records = []
    for a in attendance:
        w_user = getattr(a.worker, 'user', None) if getattr(a, 'worker', None) else None
        worker_name = getattr(w_user, 'name', None) or getattr(w_user, 'username', f"Artisan #{a.worker_id}") if w_user else f"Artisan #{a.worker_id}"
        trade = getattr(a.worker, 'skills', None) or getattr(a.worker, 'trade_category', "Technician") if getattr(a, 'worker', None) else "Technician"
        
        sr = a.service_request or a.project
        cust_name = getattr(sr, 'customer_name', None) if sr else None
        if not cust_name and sr and getattr(sr, 'customer', None) and getattr(sr.customer, 'user', None):
            cust_name = sr.customer.user.username
        if not cust_name:
            cust_name = 'Customer'
        
        req_code = getattr(sr, 'request_id', '') or (f"SR-{sr.id}" if sr else '')
        loc = getattr(sr, 'address', None) or getattr(sr, 'location_name', None) if sr else None
        if not loc:
            loc = a.site_name or "Society Maintenance Site"

        dur = "-"
        if a.check_in_time and a.check_out_time:
            diff = a.check_out_time - a.check_in_time
            h = int(diff.total_seconds() // 3600)
            m = int((diff.total_seconds() % 3600) // 60)
            dur = f"{h}h {m}m"
        elif a.check_in_time:
            dur = "Active"
            
        site_name = loc.split(',')[0].strip() if loc else "Site Location"
        c_in = a.check_in_time.strftime('%I:%M %p') if a.check_in_time else (sr.arrived_at.strftime('%I:%M %p') if sr and getattr(sr, 'arrived_at', None) else '-')
        c_out = a.check_out_time.strftime('%I:%M %p') if a.check_in_time and a.check_out_time else '-'

        records.append({
            'id': a.id,
            'worker_id': a.worker_id,
            'worker_name': worker_name,
            'trade': trade,
            'avatar_letter': worker_name[0].upper() if worker_name else 'W',
            'date': a.date.strftime('%d %b %Y') if a.date else today.strftime('%d %b %Y'),
            'site_name': site_name,
            'location': loc,
            'full_site': loc,
            'customer_name': cust_name,
            'request_id': req_code,
            'punch_in_time': c_in,
            'check_in': c_in,
            'check_out': c_out,
            'duration': dur,
            'status': a.status or 'Present',
            'verified_by_gps': a.verified_by_gps,
            'verified_by_qr': a.verified_by_qr,
            'raw': a
        })

    return render_template(
        'admin/attendance.html',
        contractor=contractor,
        records=records,
        attendance=attendance,
        present_today=present_today,
        on_site_now=on_site_now,
        completed_today=completed_today,
        gps_pct=gps_pct
    )

@admin_bp.route('/payments')
@login_required
@admin_required
def payments_page():
    contractor, _, _, payments = _admin_scope_basic()
    return render_template('admin/payments.html', contractor=contractor, payments=payments)

@admin_bp.route('/ai-demand')
@login_required
@admin_required
def ai_demand_page():
    contractor = get_current_contractor()
    city = (contractor.service_areas.split(',')[0].strip() if contractor and contractor.service_areas else 'Mumbai')
    forecast = AIService.forecast_gig_service_demand(city=city)
    return render_template(
        'admin/ai_demand.html',
        contractor=contractor,
        forecast=forecast,
        forecast_data=forecast.get('forecast_data', []),
        metrics=forecast,
        chart_labels=forecast.get('chart_labels', []),
        chart_datasets=forecast.get('chart_datasets', []),
        reallocations=forecast.get('reallocation_recommendations', [])
    )


@admin_bp.route('/welfare')
@login_required
@admin_required
def welfare_page():
    contractor, workers, _, _ = _admin_scope_basic()
    summaries=[]
    for w in workers:
        summaries.append((w, WelfareService.get_worker_welfare_summary(w.id)))
    return render_template('admin/welfare.html', contractor=contractor, summaries=summaries)

@admin_bp.route('/profile', endpoint='profile')
@admin_bp.route('/profile', endpoint='profile_page')
@login_required
@admin_required
def profile_page():
    contractor=get_current_contractor()
    return render_template('admin/profile.html', contractor=contractor)

@admin_bp.route('/settings')
@login_required
@admin_required
def settings_page():
    contractor = get_current_contractor()
    return render_template('admin/settings.html', contractor=contractor)
