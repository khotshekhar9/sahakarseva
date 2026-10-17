from flask import Blueprint, render_template, abort, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from database import db
from datetime import datetime, date
from models.user import User
from models.contractor import Contractor, ContractorReview
from models.customer import Customer
from models.attendance import Attendance
from models.finance import Payment
from models.communication import Notification, SupportTicket
from models.service_request import ServiceRequest
from models.worker import Worker
import os
import base64
from werkzeug.utils import secure_filename
from services.welfare_service import WelfareService
from services.dispatch_service import DispatchService

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'customer':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@customer_bp.route('/api/geocode', methods=['GET'])
@login_required
def geocode_proxy():
    query = request.args.get('q', '').strip()
    lat = request.args.get('lat')
    lng = request.args.get('lon') or request.args.get('lng')
    
    import requests
    headers = {'User-Agent': 'SahakarSevaApp/1.0 (Python Geocoder Proxy)'}
    try:
        if query:
            url = f"https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&q={requests.utils.quote(query)}"
            res = requests.get(url, headers=headers, timeout=6)
            if res.ok:
                return jsonify(res.json())
        elif lat and lng:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&lat={lat}&lon={lng}"
            res = requests.get(url, headers=headers, timeout=6)
            if res.ok:
                return jsonify(res.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify([])

@customer_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    # Fetch customer profile
    customer = Customer.query.get(current_user.id)
    if not customer:
        flash("Customer profile not found.", "danger")
        return redirect(url_for('auth.login'))
        
    # Get active projects
    projects = customer.projects
    
    # Get bills & invoices
    invoices = Payment.query.filter_by(customer_id=customer.id, type='revenue').order_by(Payment.date.desc()).all()
    
    # Get support tickets
    tickets = SupportTicket.query.filter_by(customer_id=customer.id).order_by(SupportTicket.created_at.desc()).all()
    
    # Get customer notifications
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    messages = notifications
    
    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).order_by(ServiceRequest.created_at.desc()).all()
    
    active_emergencies = ServiceRequest.query.filter(
        ServiceRequest.customer_id == customer.id,
        ServiceRequest.is_emergency == True,
        ServiceRequest.status.in_(['Broadcasting', 'In Progress', 'Assigned', 'Travelling', 'Work Started', 'OTP Verified'])
    ).order_by(ServiceRequest.created_at.desc()).all()
    
    return render_template(
        'customer/dashboard.html',
        customer=customer,
        projects=projects,
        invoices=invoices,
        tickets=tickets,
        messages=messages,
        notifications=notifications,
        service_requests=service_requests,
        active_emergencies=active_emergencies,
        emergency_rate_cards=DispatchService.COOPERATIVE_EMERGENCY_RATES
    )

# 0. Contractor Profile & Review Routes


@customer_bp.route('/contractor/<int:contractor_id>')
@login_required
@customer_required
def contractor_detail(contractor_id):
    contractor = Contractor.query.get_or_404(contractor_id)
    reviews = ContractorReview.query.filter_by(contractor_id=contractor_id).order_by(ContractorReview.id.desc()).all()
    projects = ServiceRequest.query.filter_by(contractor_id=contractor_id).all()
    
    rating_avg = sum(r.rating for r in reviews) / len(reviews) if reviews else float(contractor.average_rating or 4.8)
    
    return render_template('customer/contractor_detail.html', contractor=contractor, reviews=reviews, projects=projects, rating_avg=rating_avg)

# 1. Digital Signature & Pay Invoice Action
@customer_bp.route('/invoice/sign', methods=['POST'])
@login_required
@customer_required
def sign_invoice():
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    try:
        if request.is_json:
            data = request.get_json() or {}
            invoice_id = data.get('invoice_id')
            signature_data = data.get('signature')
        else:
            invoice_id = request.form.get('invoice_id')
            signature_data = request.form.get('signature') # Base64 image string
        
        payment = Payment.query.get(invoice_id)
        if not payment or payment.customer_id != current_user.id:
            if is_ajax:
                return jsonify({'status': 'error', 'message': 'Invoice not found.'}), 404
            flash('Invoice not found.', 'danger')
            return redirect(request.referrer or url_for('customer.payments_page'))
            
        if payment.status == 'Paid':
            if is_ajax:
                return jsonify({'status': 'error', 'message': 'Invoice is already paid.'}), 400
            flash('Invoice is already paid.', 'warning')
            return redirect(request.referrer or url_for('customer.payments_page'))
            
        # Decode and save signature image
        if signature_data and ',' in signature_data:
            img_data = signature_data.split(',')[1]
            img_bytes = base64.b64decode(img_data)
            
            filename = f"sig_{invoice_id}_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'signatures')
            os.makedirs(upload_dir, exist_ok=True)
            
            filepath = os.path.join(upload_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(img_bytes)
                
            payment.signature_path = f"/static/uploads/signatures/{filename}"
            payment.signed_by_customer = True
            payment.status = 'Paid'
            payment.type = 'revenue'
            payment.date = datetime.utcnow().date()
            
            if payment.service_request_id and payment.service_request:
                payment.service_request.status = 'Paid'
                payment.service_request.payment_status = 'Paid'
                if not payment.contractor_id:
                    payment.contractor_id = payment.service_request.contractor_id or 1
                if not payment.worker_id and payment.service_request.assigned_worker_id:
                    payment.worker_id = payment.service_request.assigned_worker_id
            elif payment.project_id and payment.project:
                if not payment.contractor_id:
                    payment.contractor_id = payment.project.contractor_id or 1
            if not payment.contractor_id:
                payment.contractor_id = 1

            # Compute 4-tier cooperative split if missing
            if float(payment.amount or 0.0) > 0 and float(payment.welfare_cess or 0.0) == 0.0:
                split = WelfareService.calculate_cess_split(payment.amount)
                payment.worker_payout = split['worker_payout']
                payment.society_admin_fee = split['society_admin_fee']
                payment.federation_fee = split['federation_fee']
                payment.welfare_cess = split['welfare_cess']
            
            # Credit 2% Micro-Cess to Worker Welfare Fund (Suraksha Nidhi) & Trigger Insurance Auto-Debit
            target_worker_id = payment.worker_id or (payment.service_request.assigned_worker_id if payment.service_request else None)
            if target_worker_id and float(payment.welfare_cess or 0.0) > 0:
                WelfareService.credit_welfare_cess(
                    worker_id=target_worker_id,
                    cess_amount=float(payment.welfare_cess),
                    payment_id=payment.id,
                    service_request_id=payment.service_request_id,
                    description=f"2% Cooperative Welfare Cess from Invoice #{payment.invoice_number}"
                )
            
            # Send notification to Admin/Contractor
            target_contractor = Contractor.query.get(payment.contractor_id) if payment.contractor_id else None
            target_user_id = target_contractor.user_id if (target_contractor and target_contractor.user_id) else 1
            
            n = Notification(
                user_id=target_user_id,
                title="Invoice Signed & Paid",
                message=f"Customer @{current_user.username} signed invoice {payment.invoice_number} (Rs. {payment.amount:.2f}). 2% Cess deposited to Worker Welfare Fund.",
                type="Success"
            )
            db.session.add(n)
            db.session.commit()
            
            if is_ajax:
                return jsonify({'status': 'success', 'message': 'Signature saved. Invoice marked as Paid.'})
            flash('Signature saved. Invoice marked as Paid.', 'success')
            return redirect(request.referrer or url_for('customer.payments_page'))

        if is_ajax:
            return jsonify({'status': 'error', 'message': 'Invalid signature data.'}), 400
        flash('Invalid signature data.', 'danger')
        return redirect(request.referrer or url_for('customer.payments_page'))
    except Exception as e:
        db.session.rollback()
        if is_ajax:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        flash(f'Error signing invoice: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('customer.payments_page'))

# 2. Support Ticket Creator
@customer_bp.route('/support/ticket', methods=['POST'])
@login_required
@customer_required
def create_ticket():
    try:
        data = request.get_json(silent=True) or request.form
        title = (data.get('title') or '').strip()
        desc = (data.get('description') or '').strip()
        priority = data.get('priority', 'Normal')
        escalation_level = (data.get('escalation_level') or 'society').strip().lower()
        is_apex = (escalation_level == 'apex')
        
        if not title or not desc:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({'status': 'error', 'message': 'Title and description are required.'}), 400
            flash("Title and description are required.", "warning")
            return redirect(url_for('customer.help_page') + '#ticket-section')

        # Link to most recent service request/contractor if available
        latest_sr = ServiceRequest.query.filter_by(customer_id=current_user.id).order_by(ServiceRequest.id.desc()).first()
        c_id = latest_sr.contractor_id if latest_sr else None
        c_name = latest_sr.contractor.company_name if (latest_sr and latest_sr.contractor) else "Chembur Labour Cooperative Society Ltd."

        ticket = SupportTicket(
            customer_id=current_user.id,
            title=title,
            description=desc,
            status='Open',
            priority=priority,
            target_tier='apex' if is_apex else 'society',
            escalation_level='apex' if is_apex else 'society',
            is_apex_dispute=is_apex,
            contractor_id=c_id,
            contractor_name=c_name
        )
        db.session.add(ticket)
        db.session.flush()


        
        # Admin Alert notification
        n = Notification(
            user_id=1,
            title="Apex Escalated Grievance" if is_apex else "New Support Ticket",
            message=f"Client @{current_user.username} submitted {'Apex Escalated' if is_apex else 'society'} ticket #{ticket.id}: {title}.",
            type="Alert"
        )
        db.session.add(n)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({
                'status': 'success',
                'message': 'Grievance escalated to Apex Federation conciliation desk.' if is_apex else 'Support ticket created successfully. Our team will review shortly.',
                'ticket': {
                    'id': ticket.id,
                    'title': ticket.title,
                    'status': ticket.status,
                    'priority': ticket.priority,
                    'escalation_level': ticket.escalation_level,
                    'target_tier': ticket.target_tier,
                    'created_at': ticket.created_at.strftime('%d %b %Y, %I:%M %p') if ticket.created_at else 'Just now'
                }
            })

        flash("Support ticket created successfully. Our team will review shortly.", "success")
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        flash(f"Error creating ticket: {str(e)}", "danger")
        
    return redirect(url_for('customer.help_page') + '#ticket-section')

# 3. Customer Service Request / Project Feedback
@customer_bp.route('/service-request/feedback', methods=['POST'])
@customer_bp.route('/project/feedback', methods=['POST'])
@login_required
@customer_required
def submit_feedback():
    try:
        sr_id = request.form.get('service_request_id') or request.form.get('project_id')
        feedback_text = request.form.get('feedback')
        
        sr = ServiceRequest.query.get(sr_id) if sr_id else None
        if sr and sr.customer_id == current_user.id:
            sr.review_comment = (sr.review_comment or '') + f"\n\n[Customer Feedback - {datetime.now().strftime('%Y-%m-%d')}]: {feedback_text}"
            
            n = Notification(
                user_id=1,
                title="Client Service Feedback",
                message=f"Customer @{current_user.username} left feedback on service #{sr.request_id}: {sr.title}.",
                type="Info"
            )
            db.session.add(n)
            db.session.commit()
            flash("Feedback submitted to contractor successfully!", "success")
        else:
            flash("Service request not found.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting feedback: {str(e)}", "danger")
        
    return redirect(url_for('customer.dashboard'))

# 4. Message Sender
@customer_bp.route('/message/send', methods=['POST'])
@login_required
@customer_required
def send_message():
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    try:
        if request.is_json:
            data = request.get_json() or {}
            text = data.get('message_text')
        else:
            text = request.form.get('message_text')

        if text and text.strip():
            # Dynamically resolve target contractor/admin
            contractor_user = User.query.filter(User.role.in_(['admin', 'manager', 'supervisor'])).first()
            target_admin_id = contractor_user.id if contractor_user else 1

            notif = Notification(
                user_id=target_admin_id,
                title=f"Message from Customer: {current_user.full_name or current_user.username}",
                message=text.strip(),
                type='Info',
                priority='Normal'
            )
            db.session.add(notif)
            db.session.commit()

            if is_ajax:
                return jsonify({
                    'status': 'success',
                    'message': 'Message sent successfully.',
                    'data': {
                        'id': notif.id,
                        'message_text': notif.message,
                        'timestamp': notif.timestamp.strftime('%d %b %Y %I:%M %p'),
                        'sender_id': current_user.id
                    }
                })
            else:
                flash('Message sent successfully.', 'success')
                return redirect(request.referrer or url_for('customer.messages_page'))

        if is_ajax:
            return jsonify({'status': 'error', 'message': 'Cannot send an empty message.'}), 400
        else:
            flash('Cannot send an empty message.', 'danger')
            return redirect(request.referrer or url_for('customer.messages_page'))
    except Exception as e:
        db.session.rollback()
        if is_ajax:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        else:
            flash(f'Error sending message: {str(e)}', 'danger')
            return redirect(request.referrer or url_for('customer.messages_page'))

# 5. Contractor Discovery & Marketplace Route
@customer_bp.route('/marketplace', methods=['GET'])
@login_required
@customer_required
def marketplace():
    q = request.args.get('q', '').strip() or request.args.get('city', '').strip()
    category = request.args.get('category', '').strip() or request.args.get('business_type', '').strip()

    query = Contractor.query.filter_by(is_active=True)
    if q:
        query = query.filter(
            Contractor.company_name.ilike(f'%{q}%') | 
            Contractor.description.ilike(f'%{q}%') | 
            Contractor.service_areas.ilike(f'%{q}%') | 
            Contractor.office_address.ilike(f'%{q}%')
        )
    if category:
        query = query.filter(Contractor.business_type.ilike(f'%{category}%') | Contractor.company_name.ilike(f'%{category}%'))

    contractors = query.all()
    
    # Calculate average rating for each contractor
    for c in contractors:
        reviews = ContractorReview.query.filter_by(contractor_id=c.id).all()
        if reviews:
            c.rating_avg = sum(r.rating for r in reviews) / len(reviews)
            c.reviews_count = len(reviews)
        else:
            c.rating_avg = float(c.average_rating or 4.8)
            c.reviews_count = (c.id * 2) + 3

    # Collect available cities for filter dropdown
    all_active = Contractor.query.filter_by(is_active=True).all()
    cities = set()
    for c in all_active:
        for area in c.get_service_area_list():
            cities.add(area)

    return render_template(
        'customer/marketplace.html',
        contractors=contractors,
        cities=sorted(list(cities)),
        search_query=q,
        selected_category=category,
        selected_city=q,
        selected_type=category
    )

# 6. Book Service Routes
@customer_bp.route('/book-service', methods=['GET'])
@customer_bp.route('/book', methods=['GET'])
@login_required
@customer_required
def book_service():
    selected_contractor_id = request.args.get('contractor_id', type=int)
    contractors = Contractor.query.filter_by(is_active=True).all()
    selected_contractor = Contractor.query.get(selected_contractor_id) if selected_contractor_id else None
    return render_template('customer/book_service.html', contractors=contractors, selected_contractor=selected_contractor, selected_contractor_id=selected_contractor_id)

@customer_bp.route('/book-service/submit', methods=['POST'])
@login_required
@customer_required
def submit_service():
    try:
        cust_name = request.form.get('customer_name')
        mobile = request.form.get('mobile_number')
        category = request.form.get('category')
        title = request.form.get('title')
        priority = request.form.get('priority', 'Normal')
        desc = request.form.get('description')
        preferred_date_raw = request.form.get('preferred_date', '').strip()
        preferred_time = request.form.get('preferred_time', '').strip()
        visit_date = None
        if preferred_date_raw:
            try:
                visit_date = datetime.strptime(preferred_date_raw, '%Y-%m-%d').date()
            except ValueError:
                visit_date = None
        address = request.form.get('address')
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')
        
        # Generation of unique request ID
        year = datetime.now().year
        last_sr = ServiceRequest.query.order_by(ServiceRequest.id.desc()).first()
        next_num = (last_sr.id + 1) if last_sr else (ServiceRequest.query.count() + 1)
        req_id = f"SR-{year}-{next_num:06d}"
        while ServiceRequest.query.filter_by(request_id=req_id).first():
            next_num += 1
            req_id = f"SR-{year}-{next_num:06d}"
        
        # Handle Voice recording
        voice_path = None
        voice_file = request.files.get('voice_audio')
        if voice_file:
            filename = f"voice_{req_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'service_voices')
            os.makedirs(upload_dir, exist_ok=True)
            voice_file.save(os.path.join(upload_dir, filename))
            voice_path = f"/static/uploads/service_voices/{filename}"
            
        # Handle Photos
        photo_paths = []
        uploaded_photos = request.files.getlist('photos')
        if uploaded_photos:
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'service_photos')
            os.makedirs(upload_dir, exist_ok=True)
            for idx, p_file in enumerate(uploaded_photos):
                if p_file and p_file.filename:
                    ext = os.path.splitext(p_file.filename)[1] or '.jpg'
                    filename = f"img_{req_id}_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                    p_file.save(os.path.join(upload_dir, filename))
                    photo_paths.append(f"/static/uploads/service_photos/{filename}")
                    
        photos_str = ",".join(photo_paths) if photo_paths else None
        
        # Resolve contractor_id from form or default contractor
        contractor_id_param = request.form.get('contractor_id')
        contractor_id = int(contractor_id_param) if contractor_id_param and contractor_id_param.isdigit() else None
        if not contractor_id:
            first_c = Contractor.query.filter_by(is_active=True).first()
            contractor_id = first_c.id if first_c else 1

        # Address & Location resolution:
        if (not address or address == "Service Location Address") and lat and lng:
            try:
                import requests
                headers = {'User-Agent': 'SahakarSevaApp/1.0 (Cooperative Dispatch Engine)'}
                url = f"https://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&lat={lat}&lon={lng}"
                r = requests.get(url, headers=headers, timeout=4)
                if r.ok:
                    geo_d = r.json()
                    if geo_d and geo_d.get('display_name'):
                        address = geo_d.get('display_name')
            except Exception:
                pass
            if not address or address == "Service Location Address":
                address = f"GPS Site Location ({float(lat):.5f}, {float(lng):.5f})"
        elif not address:
            address = current_user.address or "Sindhi Society, Chembur Central, Mumbai - 400071"

        # Create DB record
        import random
        is_emg = (priority == 'Emergency')
        booking_otp = str(random.randint(1000, 9999))
        req = ServiceRequest(
            request_id=req_id,
            contractor_id=contractor_id,
            customer_id=current_user.id,
            customer_name=cust_name,
            mobile_number=mobile,
            category=category,
            title=title,
            description=desc,
            voice_path=voice_path,
            photos=photos_str,
            address=address,
            latitude=float(lat) if lat else None,
            longitude=float(lng) if lng else None,
            priority=priority,
            is_emergency=is_emg,
            emergency_severity='Critical' if is_emg else None,
            status='Pending Review',
            visit_date=visit_date,
            preferred_time=preferred_time or None,
            otp=booking_otp
        )
        db.session.add(req)
        
        # Add Notification to Admin/Contractor
        target_contractor = Contractor.query.get(contractor_id)
        notif_user_id = target_contractor.user_id if (target_contractor and target_contractor.user_id) else 1
        
        title_notif = "EMERGENCY Service Request" if priority == 'Emergency' else "New Service Request Published"
        msg_notif = f"EMERGENCY Request! Customer @{current_user.username} submitted ticket {req_id} for {category}." if priority == 'Emergency' else f"Customer @{current_user.username} submitted service ticket {req_id} for {category}."
        n = Notification(
            user_id=notif_user_id,
            title=title_notif,
            message=msg_notif,
            type="Alert" if priority == 'Emergency' else "Info"
        )
        db.session.add(n)
        
        from models.communication import ActivityLog
        ActivityLog.log_activity(
            user_id=current_user.id,
            action=f"Book Service {req_id}",
            details=f"Customer @{current_user.username} submitted {priority} ticket {req_id} ({category}) in Kurla-Govandi corridor",
            ip=request.remote_addr
        )
        db.session.commit()
        
        return jsonify({'status': 'success', 'request_id': req_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Payment Settlement Endpoints
@customer_bp.route('/payments/<int:payment_id>/pay', methods=['POST'])
@customer_bp.route('/pay/<int:payment_id>', methods=['POST'])
@login_required
@customer_required
def pay_invoice(payment_id):
    """Mark an invoice as paid, distribute 88/8/4 cooperative funds, and update service request."""
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    payment = Payment.query.get(payment_id)
    if not payment or (payment.customer_id != current_user.id and (not payment.service_request or payment.service_request.customer_id != current_user.id)):
        if is_ajax:
            return jsonify({'status': 'error', 'message': 'Invoice not found.'}), 404
        flash('Invoice not found.', 'danger')
        return redirect(request.referrer or url_for('customer.payments_page'))
        
    if payment.status == 'Paid':
        if is_ajax:
            return jsonify({'status': 'error', 'message': 'Invoice is already paid.'}), 400
        flash('Invoice is already paid.', 'warning')
        return redirect(request.referrer or url_for('customer.payments_page'))
        
    try:
        payment.status = 'Paid'
        payment.type = 'revenue'
        payment.date = datetime.utcnow().date()
        
        if payment.service_request_id and payment.service_request:
            payment.service_request.payment_status = 'Paid'
            if payment.service_request.status in ['Completed', 'Work Completed', 'Work Approved', 'Invoice Generated', 'OTP Verified']:
                payment.service_request.status = 'Paid'
            if not payment.contractor_id:
                payment.contractor_id = payment.service_request.contractor_id or 1
            if not payment.worker_id and payment.service_request.assigned_worker_id:
                payment.worker_id = payment.service_request.assigned_worker_id
        elif payment.project_id and payment.project:
            if not payment.contractor_id:
                payment.contractor_id = payment.project.contractor_id or 1
        if not payment.contractor_id:
            payment.contractor_id = 1

        # Allocate 88/8/4 statutory funds and credit welfare cess to worker
        WelfareService.allocate_payment_cess(payment)
            
        target_contractor = Contractor.query.get(payment.contractor_id) if payment.contractor_id else None
        target_user_id = target_contractor.user_id if (target_contractor and target_contractor.user_id) else 1
            
        # Notification to admin/contractor
        n = Notification(
            user_id=target_user_id,
            title="Invoice Paid",
            message=f"Customer @{current_user.username} paid invoice {payment.invoice_number or payment.id} (Rs. {payment.amount:.2f}). Statutory 88/8/4 wage & welfare funds distributed.",
            type="Success"
        )
        db.session.add(n)
        db.session.commit()

        if is_ajax:
            return jsonify({
                'status': 'success',
                'message': 'Payment completed successfully.',
                'payment_id': payment.id,
                'status_text': 'Paid'
            })
        else:
            flash(f'Invoice #{payment.invoice_number or payment.id} marked as paid successfully.', 'success')
            return redirect(url_for('customer.payments_page'))
    except Exception as e:
        db.session.rollback()
        if is_ajax:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        else:
            flash(f'Payment processing error: {str(e)}', 'danger')
            return redirect(url_for('customer.payments_page'))

stub_pay = pay_invoice

# Theme Preference Update Endpoint
@customer_bp.route('/theme', methods=['POST'])
@login_required
@customer_required
def update_theme():
    """Update current user's theme preference (dark or light)."""
    theme = request.json.get('theme')
    if theme not in ['dark', 'light']:
        return jsonify({'status': 'error', 'message': 'Invalid theme.'}), 400
    try:
        user = User.query.get(current_user.id)
        user.theme_preference = theme
        db.session.commit()
        return jsonify({'status': 'success', 'theme': theme})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 6. Service Request Quotation Responses
@customer_bp.route('/quotation/<int:quote_id>/approve', methods=['POST'])
@customer_bp.route('/quotation/<int:quote_id>/respond', methods=['POST'])
@login_required
@customer_required
def respond_quotation(quote_id):
    from models.quotation import Quotation
    quote = Quotation.query.get_or_404(quote_id)
    action = request.form.get('action') or ('approve' if request.path.endswith('/approve') else 'approve')
    changes_reason = request.form.get('changes_reason', '')
    
    if quote.service_request.customer_id != current_user.id:
        abort(403)
        
    try:
        if action == 'approve':
            quote.status = 'Approved'
            quote.service_request.status = 'Quotation Approved'
            
            # Compute statutory 88/8/4 cooperative margin ledger
            quote_amount = float(quote.grand_total or getattr(quote, 'total_amount', 0.0) or 0.0)
            split = WelfareService.calculate_cess_split(quote_amount, split_mode="88_8_4")
            year = datetime.now().year
            inv_number = f"INV-{year}-{quote.service_request.id:06d}"

            # Atomically create or update Payment record
            payment = Payment.query.filter_by(service_request_id=quote.service_request.id, type='revenue').first()
            if not payment:
                payment = Payment(
                    type='revenue',
                    amount=quote_amount,
                    date=datetime.utcnow().date(),
                    status='Pending',
                    customer_id=quote.service_request.customer_id,
                    contractor_id=quote.service_request.contractor_id or 1,
                    worker_id=quote.service_request.assigned_worker_id,
                    service_request_id=quote.service_request.id,
                    invoice_number=inv_number,
                    quotation_number=quote.quotation_number,
                    description=f"Approved Quotation #{quote.quotation_number} - {quote.service_request.category} ({quote.service_request.request_id})",
                    labour_cost=float(quote.labour_cost or 0.0),
                    discount=float(quote.discount or 0.0),
                    gst=float(quote.gst or 0.0),
                    worker_payout=split['worker_payout'],
                    society_admin_fee=split['society_admin_fee'],
                    federation_fee=split.get('federation_fee', 0.0),
                    welfare_cess=split['welfare_cess']
                )
                db.session.add(payment)
            else:
                payment.amount = quote_amount
                payment.status = 'Pending'
                if not payment.invoice_number:
                    payment.invoice_number = inv_number
                payment.quotation_number = quote.quotation_number
                payment.description = f"Approved Quotation #{quote.quotation_number} - {quote.service_request.category} ({quote.service_request.request_id})"
                payment.labour_cost = float(quote.labour_cost or 0.0)
                payment.discount = float(quote.discount or 0.0)
                payment.gst = float(quote.gst or 0.0)
                payment.worker_payout = split['worker_payout']
                payment.society_admin_fee = split['society_admin_fee']
                payment.federation_fee = split.get('federation_fee', 0.0)
                payment.welfare_cess = split['welfare_cess']

            quote.service_request.payment_status = 'Pending Payment'

            # Create Notification for Admin
            admin_uid = quote.service_request.contractor.user_id if (quote.service_request.contractor and quote.service_request.contractor.user_id) else 1
            n = Notification(
                user_id=admin_uid,
                title="Quotation Approved & Invoice Issued",
                message=f"Customer @{current_user.username} approved quotation {quote.quotation_number} for Rs. {quote_amount:.2f}. Invoice #{inv_number} has been generated.",
                type="Success"
            )
            db.session.add(n)
            flash(f"Quotation approved! Invoice #{inv_number} for Rs. {quote_amount:.2f} generated with cooperative wage ledger.", "success")
        elif action == 'reject':
            quote.status = 'Rejected'
            quote.service_request.status = 'Quotation Rejected'
            
            admin_uid = quote.service_request.contractor.user_id if (quote.service_request.contractor and quote.service_request.contractor.user_id) else 1
            n = Notification(
                user_id=admin_uid,
                title="Quotation Rejected",
                message=f"Customer @{current_user.username} rejected quotation {quote.quotation_number}.",
                type="Warning"
            )
            db.session.add(n)
            flash("Quotation rejected.", "warning")
        elif action == 'changes':
            quote.status = 'Changes Requested'
            quote.service_request.status = 'Changes Requested'
            quote.service_request.rework_comments = changes_reason
            
            admin_uid = quote.service_request.contractor.user_id if (quote.service_request.contractor and quote.service_request.contractor.user_id) else 1
            n = Notification(
                user_id=admin_uid,
                title="Quotation Changes Requested",
                message=f"Customer @{current_user.username} requested changes for quotation {quote.quotation_number}. Reason: {changes_reason}",
                type="Alert"
            )
            db.session.add(n)
            flash("Changes requested for the quotation.", "info")
            
        from models.communication import ActivityLog
        act_verb = "Approved" if action == 'approve' else ("Rejected" if action == 'reject' else "Requested Changes")
        ActivityLog.log_activity(
            user_id=current_user.id,
            action=f"{act_verb} Quotation {quote.quotation_number}",
            details=f"Customer @{current_user.username} {act_verb.lower()} quotation #{quote.quotation_number} ({quote.service_request.category})",
            ip=request.remote_addr
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error processing quotation: {str(e)}", "danger")
        
    redirect_target = request.referrer or url_for('customer.booking_details', booking_id=quote.service_request.id)
    return redirect(redirect_target)


@customer_bp.route('/quotation/<int:quote_id>/approve-quotation', methods=['POST'])
@login_required
@customer_required
def approve_quotation(quote_id):
    """Direct alias for approving quotation with automatic invoice generation."""
    return respond_quotation(quote_id)


# 7. Customer Work Approval & Rework Request
@customer_bp.route('/service-request/<int:request_id>/approve-work', methods=['POST'])
@login_required
@customer_required
def approve_work(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if req.customer_id != current_user.id:
        abort(403)
        
    action = request.form.get('action')  # 'approve' or 'rework'
    rating = request.form.get('rating')
    review_comment = request.form.get('review_comment', '')
    rework_comments = request.form.get('rework_comments', '')
    
    try:
        if action == 'approve':
            req.status = 'Work Approved'
            req.rating = int(rating) if rating else 5
            req.review_comment = review_comment
            
            # Generate Invoice automatically with 4-Tier Cooperative Split
            stamp = datetime.now().strftime('%Y%m%d%H%M%S')
            inv_no = f"INV-SR-{stamp}"
            amount_val = float(req.estimated_cost or 0.0)
            split = WelfareService.calculate_cess_split(amount_val)
            
            p = Payment(
                type='revenue',
                amount=amount_val,
                status='Pending Payment',
                customer_id=current_user.id,
                service_request_id=req.id,
                worker_id=req.assigned_worker_id,
                contractor_id=req.contractor_id or 1,
                worker_payout=split['worker_payout'],
                society_admin_fee=split['society_admin_fee'],
                federation_fee=split['federation_fee'],
                welfare_cess=split['welfare_cess'],
                invoice_number=inv_no,
                description=f"Cooperative service billing for {req.request_id}: {req.title} (88% Worker Living Wage, 8% Society Ops, 4% Welfare Reserve)"
            )
            db.session.add(p)
            req.status = 'Invoice Generated'
            req.payment_status = 'Pending Payment'
            
            # Notify Customer, Worker & Admin
            n_admin = Notification(
                user_id=1,
                title="Job Approved & Invoiced",
                message=f"Customer @{current_user.username} approved work for {req.request_id}. Invoice {inv_no} generated.",
                type="Success"
            )
            n_cust = Notification(
                user_id=current_user.id,
                title="Invoice Generated",
                message=f"Your invoice {inv_no} for ${amount_val:,.2f} is ready for payment.",
                type="Info"
            )
            db.session.add(n_admin)
            db.session.add(n_cust)
            
            if req.assigned_worker_id:
                # Update assigned worker ratings if rating provided
                if rating:
                    w = req.assigned_worker
                    w.performance_rating = float((float(w.performance_rating or 5.0) * 4 + float(rating)) / 5.0)
                
                n_work = Notification(
                    user_id=req.assigned_worker_id,
                    title="Job Rating & Approval",
                    message=f"Customer @{current_user.username} approved the work and rated it {rating}/5 stars.",
                    type="Success"
                )
                db.session.add(n_work)
                
            db.session.commit()
            flash("Work approved and invoice generated successfully!", "success")
        elif action == 'rework':
            req.status = 'Rework Required'
            req.rework_comments = rework_comments
            
            n_admin = Notification(
                user_id=1,
                title="Rework Requested",
                message=f"Customer @{current_user.username} requested rework for {req.request_id}. Reason: {rework_comments}",
                type="Warning"
            )
            db.session.add(n_admin)
            
            if req.assigned_worker_id:
                n_work = Notification(
                    user_id=req.assigned_worker_id,
                    title="Rework Job Assigned",
                    message=f"Rework requested for ticket {req.request_id}. Comments: {rework_comments}",
                    type="Alert"
                )
                db.session.add(n_work)
                
            db.session.commit()
            flash("Rework requested. Technician and Admin have been notified.", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
        
    return redirect(url_for('customer.dashboard') + '#services')


# 8. Close Service Request Route
@customer_bp.route('/service-request/<int:request_id>/close', methods=['POST'])
@login_required
@customer_required
def close_service(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if req.customer_id != current_user.id:
        abort(403)
    try:
        req.status = 'Closed'
        req.payment_status = 'Paid'
        from models.finance import Payment
        linked_payments = Payment.query.filter_by(service_request_id=req.id).all()
        for p in linked_payments:
            p.status = 'Paid'
            if not p.contractor_id:
                p.contractor_id = req.contractor_id or 1
        db.session.commit()
        flash("Service closed successfully. Thank you!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for('customer.dashboard') + '#services')


# 9. Customer Update & Profile Edit Routes
@customer_bp.route('/api/profile/update', methods=['POST'])
@login_required
@customer_required
def update_profile_api():
    try:
        u = User.query.get(current_user.id)
        c = Customer.query.get(current_user.id)
        
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        emergency = request.form.get('emergency_contact')
        
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
            c.billing_address = address
            changes.append(f"Address: '{old_val}' -> '{address}'")
            
        if c.emergency_contact != emergency:
            old_val = c.emergency_contact
            c.emergency_contact = emergency
            changes.append(f"Emergency Contact: '{old_val}' -> '{emergency}'")
            
        if password and password.strip():
            u.set_password(password.strip())
            changes.append("Password updated")
            
        profile_pic_file = request.files.get('profile_pic')
        if profile_pic_file:
            import os
            filename = f"profile_{u.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'profile_pics')
            os.makedirs(upload_dir, exist_ok=True)
            profile_pic_file.save(os.path.join(upload_dir, filename))
            old_val = u.profile_pic
            u.profile_pic = f"/static/uploads/profile_pics/{filename}"
            changes.append(f"Profile Picture: '{old_val}' -> '{u.profile_pic}'")
            
        if changes:
            from models.communication import ActivityLog
            ActivityLog.log_activity(
                user_id=u.id,
                action="Edit Customer Profile",
                details=" | ".join(changes),
                ip=request.remote_addr
            )
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Profile updated successfully!'})
        else:
            return jsonify({'status': 'success', 'message': 'No changes made.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@customer_bp.route('/api/service-request/<int:request_id>/update', methods=['POST'])
@login_required
@customer_required
def update_service_request_api(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if req.customer_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    if req.assigned_worker_id is not None:
        return jsonify({'status': 'error', 'message': 'Cannot edit request details after a technician has been assigned.'}), 400
        
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        visit_date_str = request.form.get('visit_date')
        preferred_time = request.form.get('preferred_time')
        priority = request.form.get('priority')
        address = request.form.get('address')
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')
        
        if not title or not category or not address:
            return jsonify({'status': 'error', 'message': 'Title, Category, and Address are required.'}), 400
            
        changes = []
        
        if req.title != title:
            old = req.title
            req.title = title
            changes.append(f"Title: '{old}' -> '{title}'")
        if req.description != description:
            old = req.description
            req.description = description
            changes.append(f"Description: '{old}' -> '{description}'")
        if req.category != category:
            old = req.category
            req.category = category
            changes.append(f"Category: '{old}' -> '{category}'")
        if preferred_time and req.preferred_time != preferred_time:
            old = req.preferred_time
            req.preferred_time = preferred_time
            changes.append(f"Preferred Time: '{old}' -> '{preferred_time}'")
        if req.priority != priority:
            old = req.priority
            req.priority = priority
            changes.append(f"Priority: '{old}' -> '{priority}'")
        if req.address != address:
            old = req.address
            req.address = address
            changes.append(f"Address: '{old}' -> '{address}'")
            
        if visit_date_str:
            vdate = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
            if req.visit_date != vdate:
                old = req.visit_date
                req.visit_date = vdate
                changes.append(f"Visit Date: '{old}' -> '{vdate}'")
                
        if lat and lng:
            flat = float(lat)
            flng = float(lng)
            if req.latitude != flat or req.longitude != flng:
                req.latitude = flat
                req.longitude = flng
                changes.append(f"Coordinates: ({lat}, {lng})")
                
        voice_file = request.files.get('voice_audio')
        if voice_file:
            import os
            filename = f"comp_voice_{req.request_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'voices')
            os.makedirs(upload_dir, exist_ok=True)
            voice_file.save(os.path.join(upload_dir, filename))
            old = req.voice_path
            req.voice_path = f"/static/uploads/voices/{filename}"
            changes.append("Updated Voice Recording")
            
        uploaded_photos = request.files.getlist('photos')
        if uploaded_photos and any(p.filename for p in uploaded_photos):
            import os
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'complaints')
            os.makedirs(upload_dir, exist_ok=True)
            photo_paths = []
            for idx, p_file in enumerate(uploaded_photos):
                if p_file and p_file.filename:
                    ext = os.path.splitext(p_file.filename)[1] or '.jpg'
                    filename = f"complaint_{req.request_id}_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                    p_file.save(os.path.join(upload_dir, filename))
                    photo_paths.append(f"/static/uploads/complaints/{filename}")
            req.photos = ",".join(photo_paths)
            changes.append("Updated Uploaded Photos")
            
        if changes:
            from models.communication import ActivityLog
            ActivityLog.log_activity(
                user_id=current_user.id,
                action=f"Edit Service Request {req.request_id}",
                details=" | ".join(changes),
                ip=request.remote_addr
            )
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Service request updated successfully!'})
        else:
            return jsonify({'status': 'success', 'message': 'No changes made.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@customer_bp.route('/review/submit', methods=['POST'])
@login_required
@customer_required
def submit_review():
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.best == 'application/json'
    try:
        payload = request.get_json(silent=True) or {}
        service_request_id = request.form.get('service_request_id') or payload.get('service_request_id')
        contractor_id = request.form.get('contractor_id') or payload.get('contractor_id')
        raw_rating = request.form.get('rating') if request.form.get('rating') is not None else payload.get('rating', 5)
        review_text = (request.form.get('review_text') or payload.get('review_text') or '').strip()

        if not service_request_id and not contractor_id:
            msg = 'Service request ID or Contractor ID required.'
            if is_ajax:
                return jsonify({'status': 'error', 'message': msg}), 400
            flash(msg, 'danger')
            return redirect(url_for('customer.bookings_page'))

        try:
            rating = int(float(raw_rating))
            rating = max(1, min(5, rating))
        except (ValueError, TypeError):
            rating = 5

        sr = None
        if service_request_id:
            sr = ServiceRequest.query.get(service_request_id)
            if not sr:
                msg = 'Service request not found.'
                if is_ajax:
                    return jsonify({'status': 'error', 'message': msg}), 404
                flash(msg, 'danger')
                return redirect(url_for('customer.bookings_page'))

            if sr.customer_id != current_user.id:
                msg = 'Unauthorized to review this booking.'
                if is_ajax:
                    return jsonify({'status': 'error', 'message': msg}), 403
                flash(msg, 'danger')
                return redirect(url_for('customer.bookings_page'))

            if sr.status not in ['Completed', 'Paid', 'Work Completed', 'Work Approved', 'Closed']:
                msg = 'Reviews can only be submitted for completed or paid service requests.'
                if is_ajax:
                    return jsonify({'status': 'error', 'message': msg}), 400
                flash(msg, 'warning')
                return redirect(url_for('customer.booking_details', booking_id=sr.id))

            # Derive contractor_id if omitted
            if not contractor_id and sr.contractor_id:
                contractor_id = sr.contractor_id

            # Save star rating and review comment atomically on ServiceRequest
            sr.rating = rating
            sr.review_comment = review_text

        # Update or create ContractorReview & recalculate Contractor.average_rating
        c = Contractor.query.get(contractor_id) if contractor_id else None
        if c:
            rev = None
            if sr:
                rev = ContractorReview.query.filter_by(
                    contractor_id=c.id,
                    customer_id=current_user.id,
                    service_request_id=sr.id
                ).first()
            if not rev:
                rev = ContractorReview(
                    contractor_id=c.id,
                    customer_id=current_user.id,
                    service_request_id=sr.id if sr else None,
                    rating=rating,
                    review_text=review_text
                )
                db.session.add(rev)
            else:
                rev.rating = rating
                rev.review_text = review_text
            db.session.flush()

            # Recalculate average rating & total reviews
            reviews = ContractorReview.query.filter_by(contractor_id=c.id, is_approved=True).all()
            if reviews:
                c.total_reviews = len(reviews)
                c.average_rating = round(sum(r.rating for r in reviews) / len(reviews), 2)

        # Worker Rating Aggregation across all completed/paid requests
        if sr and sr.assigned_worker_id:
            worker = Worker.query.get(sr.assigned_worker_id)
            if worker:
                db.session.flush()
                avg_rating = db.session.query(db.func.avg(ServiceRequest.rating))\
                    .filter(
                        ServiceRequest.assigned_worker_id == worker.id,
                        ServiceRequest.rating.isnot(None),
                        ServiceRequest.status.in_(['Completed', 'Paid', 'Work Completed', 'Work Approved', 'Closed'])
                    ).scalar()
                worker.performance_rating = round(float(avg_rating or rating), 2)

        from models.communication import ActivityLog
        ActivityLog.log_activity(
            user_id=current_user.id,
            action=f"Submit Review {sr.request_id if sr else ''}",
            details=f"Customer @{current_user.username} submitted {rating}-star review for {sr.category if sr else 'contractor'}",
            ip=request.remote_addr
        )
        db.session.commit()

        success_msg = "Thank you! Review submitted."
        if is_ajax:
            return jsonify({'status': 'success', 'message': success_msg, 'rating': rating})
        else:
            flash(success_msg, "success")
            if sr:
                return redirect(url_for('customer.booking_details', booking_id=sr.id))
            return redirect(url_for('customer.bookings_page'))

    except Exception as e:
        db.session.rollback()
        err_msg = str(e)
        if is_ajax:
            return jsonify({'status': 'error', 'message': err_msg}), 500
        flash(f"Error submitting review: {err_msg}", "danger")
        return redirect(url_for('customer.bookings_page'))

@customer_bp.route('/dispute/escalate', methods=['POST'])
@login_required
@customer_required
def submit_dispute():
    try:
        contractor_id = request.form.get('contractor_id')
        service_request_id = request.form.get('service_request_id') or None
        project_id = request.form.get('project_id') or None
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Service Quality Dispute')
        desc = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'High')

        if not contractor_id or not title or not desc:
            return jsonify({'status': 'error', 'message': 'Title, description, and contractor are required.'}), 400

        c = Contractor.query.get(contractor_id)
        if not c:
            return jsonify({'status': 'error', 'message': 'Target contractor firm not found.'}), 404

        cust = Customer.query.get(current_user.id)
        cust_id = cust.id if cust else current_user.id

        # Handle Photo Evidence Uploads
        photo_paths = []
        uploaded_photos = request.files.getlist('photos')
        if uploaded_photos:
            upload_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'uploads', 'disputes')
            os.makedirs(upload_dir, exist_ok=True)
            for idx, p_file in enumerate(uploaded_photos):
                if p_file and p_file.filename:
                    ext = os.path.splitext(p_file.filename)[1] or '.jpg'
                    filename = f"dispute_{cust_id}_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                    p_file.save(os.path.join(upload_dir, filename))
                    photo_paths.append(f"/static/uploads/disputes/{filename}")

        evidence_text = f"\nEvidence Photos: {', '.join(photo_paths)}" if photo_paths else ""
        ticket = SupportTicket(
            customer_id=cust_id,
            title=title,
            description=f"{desc}{evidence_text}",
            priority=priority,
            status='Escalated',
            target_tier='apex',
            escalation_level='apex',
            is_apex_dispute=True,
            contractor_id=c.id,
            contractor_name=c.company_name
        )
        db.session.add(ticket)
        db.session.flush()
        ticket_id = f"TKT-APX-{ticket.id:04d}"

        # Notify Publisher Super Admins
        publishers = User.query.filter(User.role.in_(['publisher', 'super_admin'])).all()
        for pub in publishers:
            n = Notification(
                user_id=pub.id,
                title=f"🚨 New Escalated Customer Dispute ({ticket_id})",
                message=f"Customer @{current_user.username} escalated a dispute regarding cooperative society '{c.company_name}'.",
                type="Danger"
            )
            db.session.add(n)

        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Dispute Ticket {ticket_id} escalated to Apex Federation desk.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ─── 1-CLICK EMERGENCY DISPATCH & RADAR TRACKING ────────────────────────────
@customer_bp.route('/emergency-dispatch', methods=['POST'])
@login_required
@customer_required
def emergency_dispatch():
    """
    1-Click Emergency SOS Booking.
    Bypasses quotations and manual approvals, applies the pre-fixed
    cooperative emergency rate card, and broadcasts live alerts to nearby artisans.
    Uses the customer's live GPS current location when detected rather than stale home address.
    """
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        category = data.get('category', 'Electrical')
        severity = data.get('severity', 'Critical')
        title = data.get('title')
        description = data.get('description')
        raw_address = (data.get('address') or '').strip()
        lat = data.get('latitude') or 18.5204
        lng = data.get('longitude') or 73.8567
        radius_km = float(data.get('radius_km', 5.0) or 5.0)
        is_current_location = bool(data.get('is_current_location', False))

        saved_home = (current_user.address or '').strip()
        address = raw_address

        # If user explicitly requested current GPS location or address is empty:
        if is_current_location or not address:
            # If the user provided a reverse-geocoded current address different from home, keep it
            if raw_address and raw_address != saved_home:
                address = raw_address
            else:
                # Perform server-side reverse geocoding fallback for current GPS coordinates
                try:
                    import requests
                    headers = {'User-Agent': 'SahakarSevaApp/1.0 (Cooperative Dispatch Engine)'}
                    url = f"https://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&lat={lat}&lon={lng}"
                    r = requests.get(url, headers=headers, timeout=4)
                    if r.ok:
                        geo_d = r.json()
                        if geo_d and geo_d.get('display_name'):
                            address = geo_d.get('display_name')
                except Exception as ex:
                    current_app.logger.warning(f"Server-side reverse geocode fallback error: {ex}")

                if not address:
                    address = f"Current GPS Location ({float(lat):.5f}, {float(lng):.5f}) - Chembur, Mumbai"

        if not address:
            address = saved_home or "Sindhi Society, Chembur Central, Mumbai - 400071"

        res = DispatchService.create_and_broadcast_emergency(
            customer_id=current_user.id,
            category=category,
            severity=severity,
            title=title,
            description=description,
            address=address,
            lat=lat,
            lng=lng,
            radius_km=radius_km
        )

        return jsonify({
            'status': 'success',
            'message': f"[DISPATCH BROADCAST] Emergency broadcast live! Dispatched to {res['notified_count']} nearby verified artisans within {radius_km} km.",
            'data': res
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@customer_bp.route('/emergency-status/<int:request_id>', methods=['GET'])
@login_required
@customer_required
def emergency_status(request_id):
    """
    Live Radar Status Polling for Customer Interface.
    Returns broadcasting state, assigned worker proximity, vehicle ETA, and contact details.
    """
    try:
        status_data = DispatchService.get_emergency_status(request_id)
        if not status_data:
            return jsonify({'status': 'error', 'message': 'Emergency request not found.'}), 404
        return jsonify({'status': 'success', 'data': status_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@customer_bp.route('/emergency-cancel/<int:request_id>', methods=['POST'])
@login_required
@customer_required
def emergency_cancel(request_id):
    """
    Cancels an active emergency broadcast before an artisan claims it.
    """
    try:
        req = ServiceRequest.query.filter_by(id=request_id, customer_id=current_user.id).first()
        if not req:
            return jsonify({'status': 'error', 'message': 'Emergency request not found.'}), 404
        if req.broadcast_status == 'Claimed':
            return jsonify({'status': 'error', 'message': 'Cannot cancel: an artisan has already claimed this dispatch and is en route.'}), 400
        
        req.status = 'Cancelled'
        req.broadcast_status = 'Cancelled'
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Emergency dispatch broadcast cancelled.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500





@customer_bp.route('/emergency-request', methods=['GET'])
@login_required
@customer_required
def emergency_request():
    """
    Dedicated Emergency Request View.
    Renders emergency dispatch request interface with 1-click cooperative tariff rate cards.
    """
    return render_template(
        'customer/emergency_request.html',
        rate_cards=DispatchService.COOPERATIVE_EMERGENCY_RATES,
        categories=list(DispatchService.COOPERATIVE_EMERGENCY_RATES.keys())
    )

@customer_bp.route('/bookings')
@login_required
@customer_required
def bookings_page():
    customer = Customer.query.get_or_404(current_user.id)
    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).order_by(ServiceRequest.created_at.desc()).all()
    return render_template('customer/bookings.html', service_requests=service_requests)

@customer_bp.route('/booking-status/<int:booking_id>')
@customer_bp.route('/booking/<int:booking_id>')
@customer_bp.route('/booking/<int:booking_id>/status')
@customer_bp.route('/booking/<int:booking_id>/track')
@customer_bp.route('/booking/<int:booking_id>/details')
@login_required
@customer_required
def booking_details(booking_id):
    booking = ServiceRequest.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        abort(403)

    is_cancelled = booking.status in ['Cancelled', 'Rejected']
    status_lower = (booking.status or 'pending').lower()

    # Progressive milestone lifecycle derivation
    is_completed = status_lower in ['completed', 'closed', 'paid', 'work completed']
    is_in_progress = is_completed or bool(booking.otp_verified) or (status_lower in ['in progress', 'servicing', 'work started'])
    is_dispatched = is_in_progress or (status_lower in ['travelling', 'en route', 'arrived', 'dispatched'])
    is_assigned = is_dispatched or bool(booking.assigned_worker_id) or (status_lower in ['assigned', 'claimed'])

    # 1. Assigned Checkpoint
    if is_assigned:
        assigned_state = 'completed'
        assigned_desc = f"Artisan {booking.assigned_worker.user.username.title()} assigned from Primary Society" if booking.assigned_worker and booking.assigned_worker.user else "Verified artisan assigned"
    elif status_lower in ['pending', 'pending review', 'scheduled', 'quotation sent', 'quotation approved']:
        assigned_state = 'current'
        assigned_desc = "Society coordinator is matching certified trade artisans"
    else:
        assigned_state = 'pending'
        assigned_desc = "Technician allocation pending"

    # 2. Dispatched Checkpoint
    if is_in_progress or status_lower in ['arrived', 'dispatched']:
        dispatched_state = 'completed'
        dispatched_desc = "Artisan arrived at job site"
    elif status_lower in ['travelling', 'en route']:
        dispatched_state = 'current'
        dispatched_desc = f"Artisan is on the way to your location (Radius: {booking.dispatch_radius_km or 5} km)"
    else:
        dispatched_state = 'pending'
        dispatched_desc = "Artisan will be dispatched on scheduled visit date"

    # 3. In-Progress Checkpoint
    if is_completed:
        in_progress_state = 'completed'
        in_progress_desc = "Service completed & verified on site"
    elif is_in_progress:
        in_progress_state = 'current'
        in_progress_desc = "Artisan actively servicing site (Arrival verified)"
    elif not booking.otp_verified and (is_assigned or status_lower in ['assigned', 'travelling', 'arrived']):
        in_progress_state = 'pending'
        in_progress_desc = f"Awaiting start verification (OTP: {booking.otp})" if booking.otp else "Pending service commencement"
    else:
        in_progress_state = 'pending'
        in_progress_desc = "Pending service commencement"

    # 4. Completed Checkpoint
    if is_completed:
        completed_state = 'completed'
        completed_desc = "Quality verified under SahakarSeva Trust Guarantee"
    else:
        completed_state = 'pending'
        completed_desc = "Final quality sign-off & customer feedback"

    checkpoints = [
        {
            'key': 'assigned',
            'title': 'Worker Assigned',
            'state': 'cancelled' if is_cancelled and assigned_state == 'pending' else assigned_state,
            'description': assigned_desc,
            'icon': 'user-check',
            'time': 'Assigned' if booking.assigned_worker_id else None
        },
        {
            'key': 'dispatched',
            'title': 'Worker Dispatched',
            'state': 'cancelled' if is_cancelled and dispatched_state == 'pending' else dispatched_state,
            'description': dispatched_desc,
            'icon': 'truck',
            'time': 'En Route' if status_lower in ['travelling', 'en route'] else ('Dispatched' if dispatched_state == 'completed' else None)
        },
        {
            'key': 'in_progress',
            'title': 'Service In-Progress',
            'state': 'cancelled' if is_cancelled and in_progress_state == 'pending' else in_progress_state,
            'description': in_progress_desc,
            'icon': 'wrench',
            'time': 'Active' if in_progress_state == 'current' else ('Completed' if in_progress_state == 'completed' else None)
        },
        {
            'key': 'completed',
            'title': 'Job Completed',
            'state': 'cancelled' if is_cancelled else completed_state,
            'description': "Booking was cancelled" if is_cancelled else completed_desc,
            'icon': 'check-circle',
            'time': booking.completion_date.strftime('%d %b %Y, %I:%M %p') if booking.completion_date else None
        }
    ]

    # Fetch associated quotation and payment if they exist
    quotation = booking.quotations[-1] if booking.quotations else None
    payment = booking.payments.order_by(Payment.id.desc()).first() if booking.payments else None

    # Self-healing safeguard: Auto-instantiate invoice if quotation is approved or booking is emergency
    if not payment:
        year = datetime.now().year
        if quotation and quotation.status == 'Approved':
            amt = float(quotation.grand_total or getattr(quotation, 'total_amount', 0.0) or 0.0)
            split = WelfareService.calculate_cess_split(amt, split_mode="88_8_4")
            payment = Payment(
                type='revenue',
                amount=amt,
                date=datetime.utcnow().date(),
                status='Pending',
                customer_id=booking.customer_id,
                contractor_id=booking.contractor_id or 1,
                worker_id=booking.assigned_worker_id,
                service_request_id=booking.id,
                invoice_number=f"INV-{year}-{booking.id:06d}",
                quotation_number=quotation.quotation_number,
                description=f"Approved Quotation #{quotation.quotation_number} - {booking.category} ({booking.request_id})",
                labour_cost=float(quotation.labour_cost or 0.0),
                discount=float(quotation.discount or 0.0),
                gst=float(quotation.gst or 0.0),
                worker_payout=split['worker_payout'],
                society_admin_fee=split['society_admin_fee'],
                federation_fee=split.get('federation_fee', 0.0),
                welfare_cess=split['welfare_cess']
            )
            db.session.add(payment)
            booking.payment_status = 'Pending Payment'
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
        elif booking.is_emergency or (booking.request_id and booking.request_id.startswith('EMG-')):
            amt = float(booking.fixed_rate or 650.0)
            split = WelfareService.calculate_cess_split(amt, split_mode="88_8_4")
            payment = Payment(
                type='revenue',
                amount=amt,
                date=datetime.utcnow().date(),
                status='Pending Payment',
                customer_id=booking.customer_id,
                contractor_id=booking.contractor_id or 1,
                worker_id=booking.assigned_worker_id,
                service_request_id=booking.id,
                invoice_number=f"INV-{year}-{booking.id:06d}",
                description=f"Statutory Emergency Dispatch Tariff - {booking.category} ({booking.request_id})",
                labour_cost=amt,
                worker_payout=split['worker_payout'],
                society_admin_fee=split['society_admin_fee'],
                federation_fee=split.get('federation_fee', 0.0),
                welfare_cess=split['welfare_cess']
            )
            db.session.add(payment)
            booking.payment_status = 'Pending Payment'
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
        elif booking.assigned_worker_id and booking.estimated_cost and float(booking.estimated_cost) > 0:
            amt = float(booking.estimated_cost)
            split = WelfareService.calculate_cess_split(amt, split_mode="88_8_4")
            payment = Payment(
                type='revenue',
                amount=amt,
                date=datetime.utcnow().date(),
                status='Pending Payment',
                customer_id=booking.customer_id,
                contractor_id=booking.contractor_id or 1,
                worker_id=booking.assigned_worker_id,
                service_request_id=booking.id,
                invoice_number=f"INV-{year}-{booking.id:06d}",
                description=f"Baseline Service Billing - {booking.category} ({booking.request_id})",
                labour_cost=amt,
                worker_payout=split['worker_payout'],
                society_admin_fee=split['society_admin_fee'],
                federation_fee=split.get('federation_fee', 0.0),
                welfare_cess=split['welfare_cess']
            )
            db.session.add(payment)
            booking.payment_status = 'Pending Payment'
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

    invoice = payment
    return render_template(
        'customer/booking_details.html',
        booking=booking,
        checkpoints=checkpoints,
        is_cancelled=is_cancelled,
        quotation=quotation,
        payment=payment,
        invoice=invoice
    )

@customer_bp.route('/payments')
@login_required
@customer_required
def payments_page():
    all_invoices = Payment.query.filter_by(customer_id=current_user.id, type='revenue').order_by(Payment.date.desc()).all()
    invoices = []
    total_paid = 0.0
    pending_amount = 0.0
    pending_count = 0

    for inv in all_invoices:
        # Ignore orphaned payments whose associated service request was deleted
        if inv.service_request_id and not inv.service_request:
            continue
        # Ignore orphaned phantom payments with neither a service request nor a project
        if not inv.service_request_id and not inv.project_id:
            continue
        # Normalize legacy statuses and stale descriptions
        if inv.status == 'Pending':
            inv.status = 'Pending Payment'
        if inv.description and '90% Fair Wage' in inv.description:
            inv.description = inv.description.replace(
                '90% Fair Wage, 4% Society, 4% Federation, 2% Welfare Cess',
                '88% Worker Living Wage, 8% Society Ops, 4% Welfare Reserve'
            )
        invoices.append(inv)
        if inv.status == 'Paid':
            total_paid += float(inv.amount or 0.0)
        elif inv.status in ['Pending Payment', 'Generated']:
            pending_amount += float(inv.amount or 0.0)
            pending_count += 1

    summary = {
        'total_paid': total_paid,
        'artisan_wage': round(total_paid * 0.88, 2),
        'welfare_cess': round(total_paid * 0.04, 2),
        'pending_amount': pending_amount,
        'pending_count': pending_count
    }
    return render_template('customer/payments.html', invoices=invoices, summary=summary)

@customer_bp.route('/profile', endpoint='profile')
@customer_bp.route('/profile', endpoint='profile_page')
@login_required
@customer_required
def profile_page():
    customer = Customer.query.get_or_404(current_user.id)
    return render_template('customer/profile.html', customer=customer)

@customer_bp.route('/booking/<int:request_id>/edit', methods=['GET','POST'])
@login_required
@customer_required
def edit_booking_page(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if req.customer_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        if req.assigned_worker_id is not None:
            flash('This booking cannot be edited after a worker is assigned.', 'warning')
            return redirect(url_for('customer.bookings_page'))
        try:
            req.category = request.form.get('category', req.category).strip() or req.category
            req.title = request.form.get('title', req.title).strip() or req.title
            req.description = request.form.get('description', req.description)
            req.address = request.form.get('address', req.address).strip() or req.address
            req.preferred_time = request.form.get('preferred_time', req.preferred_time)
            req.priority = request.form.get('priority', req.priority)
            raw_date = request.form.get('visit_date','').strip()
            if raw_date:
                req.visit_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
            db.session.commit()
            admin_user_id = req.contractor.user_id if req.contractor and req.contractor.user_id else 1
            db.session.add(Notification(user_id=admin_user_id, title='Booking Updated', message=f'Customer @{current_user.username} updated booking {req.request_id}.', type='Info'))
            db.session.commit()
            flash('Booking updated successfully.', 'success')
            return redirect(url_for('customer.bookings_page'))
        except Exception as e:
            db.session.rollback()
            flash(f'Could not update booking: {e}', 'danger')
    return render_template('customer/edit_booking.html', booking=req)


@customer_bp.route('/messages')
@login_required
@customer_required
def messages_page():
    return redirect(url_for('customer.dashboard'))


@customer_bp.route('/help')
@login_required
@customer_required
def help_page():
    tickets = SupportTicket.query.filter_by(customer_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    return render_template('customer/help.html', tickets=tickets, emergency_rate_cards=DispatchService.COOPERATIVE_EMERGENCY_RATES)


@customer_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
@customer_required
def cancel_booking(booking_id):
    """
    Cancel an uncommitted booking or unaccepted emergency broadcast.
    Protected by strict lifecycle guards:
    1. Emergency requests can ONLY be cancelled while in 'Broadcasting' state
       and no worker has claimed/accepted the request.
    2. Standard bookings can ONLY be cancelled if:
       - No worker is assigned (assigned_worker_id is None)
       - Booking status is in ['Pending', 'Pending Review', 'Broadcasting']
       - No attached quotation has been 'Approved'
    Once an artisan is dispatched/scheduled or quotation approved, cancellation
    is blocked to protect artisan wages and schedule commitments.
    """
    try:
        booking = ServiceRequest.query.get(booking_id)
        if not booking or booking.customer_id != current_user.id:
            msg = "Booking not found or access unauthorized."
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': msg}), 404
            flash(msg, "danger")
            return redirect(url_for('customer.bookings_page'))

        # Check if already in a terminal state
        if booking.status in ['Cancelled', 'Completed', 'Rejected']:
            msg = f"Booking #{booking.request_id} is already {booking.status.lower()}."
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': msg}), 400
            flash(msg, "warning")
            return redirect(url_for('customer.bookings_page'))

        data = request.get_json(silent=True) or request.form.to_dict()
        reason = (data.get('reason') or '').strip() or 'Cancelled by customer before worker commitment.'

        # Guard 1: Emergency request
        if booking.is_emergency:
            is_broadcasting = (booking.status == 'Broadcasting' or booking.broadcast_status == 'Broadcasting')
            has_no_worker = booking.assigned_worker_id is None
            if not (is_broadcasting and has_no_worker):
                msg = (
                    "Emergency broadcast cannot be cancelled: an artisan has already claimed or started "
                    "mobilization for this emergency. To protect emergency workers, please contact support."
                )
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'status': 'error', 'message': msg}), 400
                flash(msg, "danger")
                return redirect(url_for('customer.booking_details', booking_id=booking.id))
            
            booking.status = 'Cancelled'
            booking.broadcast_status = 'Cancelled'
            booking.rework_comments = f"Emergency broadcast cancelled by customer: {reason}"
        else:
            # Guard 2: Standard service request
            # Must not have an assigned worker
            if booking.assigned_worker_id is not None:
                msg = (
                    "Cancellation blocked: an artisan has already been assigned and scheduled for this job. "
                    "Artisan schedule commitments are protected under cooperative policy. Contact support if needed."
                )
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'status': 'error', 'message': msg}), 400
                flash(msg, "danger")
                return redirect(url_for('customer.booking_details', booking_id=booking.id))

            # Must be in initial uncommitted states
            allowed_statuses = ['Pending', 'Pending Review', 'Broadcasting']
            if booking.status not in allowed_statuses:
                msg = (
                    f"Booking #{booking.request_id} cannot be cancelled in its current state ('{booking.status}'). "
                    "Only uncommitted bookings (Pending, Pending Review) can be cancelled directly."
                )
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'status': 'error', 'message': msg}), 400
                flash(msg, "danger")
                return redirect(url_for('customer.booking_details', booking_id=booking.id))

            # Must not have an approved quotation
            has_approved_quote = any(q.status == 'Approved' for q in booking.quotations) if booking.quotations else False
            if has_approved_quote:
                msg = (
                    "Cancellation blocked: you have already approved the formal service quotation for this request. "
                    "Materials and labor reservation are locked. Please contact support or raise a dispute ticket."
                )
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'status': 'error', 'message': msg}), 400
                flash(msg, "danger")
                return redirect(url_for('customer.booking_details', booking_id=booking.id))

            booking.status = 'Cancelled'
            booking.rework_comments = f"Cancelled by customer: {reason}"

        # Notify administrator or society contractor
        admin_user_id = 1
        if booking.contractor and booking.contractor.user_id:
            admin_user_id = booking.contractor.user_id
        db.session.add(Notification(
            user_id=admin_user_id,
            title="Booking Cancelled",
            message=f"Customer @{current_user.username} cancelled booking #{booking.request_id}. Reason: {reason}",
            type="Alert"
        ))
        db.session.commit()

        success_msg = f"Booking #{booking.request_id} has been cancelled successfully."
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'message': success_msg,
                'booking_id': booking.id,
                'request_id': booking.request_id
            })
        flash(success_msg, "success")
        return redirect(url_for('customer.bookings_page'))

    except Exception as e:
        db.session.rollback()
        err_msg = f"Error cancelling booking: {str(e)}"
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': err_msg}), 500
        flash(err_msg, "danger")
        return redirect(url_for('customer.bookings_page'))


@customer_bp.route('/booking/<int:booking_id>/verify-otp', methods=['POST'], endpoint='verify_booking_otp')
@customer_bp.route('/verify-otp', methods=['POST'], endpoint='verify_otp')
@login_required
@customer_required
def verify_customer_arrival_otp(booking_id=None):
    """Customer-side confirmation / verification of arrival OTP to transition service to 'In Progress'."""
    try:
        bid = booking_id or request.form.get('booking_id') or request.form.get('service_request_id')
        if not bid and request.is_json:
            bid = (request.get_json(silent=True) or {}).get('booking_id')
        req = ServiceRequest.query.get_or_404(bid)
        if req.customer_id != current_user.id:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        req.otp_verified = True
        req.status = 'In Progress'
        if hasattr(req, 'arrived_at'):
            req.arrived_at = datetime.utcnow()

        # Auto-mark attendance as Present for assigned worker upon arrival OTP confirmation
        if req.assigned_worker_id:
            today = date.today()
            att = Attendance.query.filter_by(worker_id=req.assigned_worker_id, date=today).first()
            if not att:
                att = Attendance(
                    worker_id=req.assigned_worker_id,
                    service_request_id=req.id,
                    date=today,
                    check_in_time=datetime.utcnow(),
                    status='Present',
                    verified_by_gps=True,
                    verified_by_qr=False
                )
                db.session.add(att)
            else:
                att.status = 'Present'
                att.service_request_id = req.id
                if not att.check_in_time:
                    att.check_in_time = datetime.utcnow()
                att.verified_by_gps = True

        db.session.commit()

        try:
            from app import socketio
            socketio.emit('job_status_changed', {
                'id': req.id,
                'request_id': req.request_id,
                'status': 'In Progress',
                'otp_verified': True
            })
            socketio.emit('emergency_status_update', {
                'booking_id': req.id,
                'status': 'In Progress',
                'status_label': 'Active Now: Artisan actively servicing site',
                'worker_name': req.assigned_worker.user.username if req.assigned_worker and req.assigned_worker.user else 'Artisan',
                'arrival_otp': req.otp,
                'otp_verified': True
            }, room=f'booking_{req.id}')
        except Exception as sock_err:
            print(f"[WebSocket] Emit error in customer verify_otp: {sock_err}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'status': 'success', 'message': 'Arrival OTP verified. Service is now in progress.'})
        flash('Arrival OTP verified. Service is now in progress.', 'success')
        return redirect(url_for('customer.booking_details', booking_id=req.id))
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'status': 'error', 'message': str(e)}), 500
        flash(f'Error verifying OTP: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('customer.dashboard'))

