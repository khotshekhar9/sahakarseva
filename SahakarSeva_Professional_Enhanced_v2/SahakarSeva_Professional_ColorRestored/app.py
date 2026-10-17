import os
import re
from flask import Flask, redirect, url_for, render_template, jsonify, request, session, flash, make_response, send_from_directory
from flask_login import LoginManager, current_user, login_required

# 1. Monkey-patch SQLAlchemy MySQL Dialect for legacy MySQL 6.0 compatibility
from sqlalchemy.dialects.mysql.base import MySQLDialect

original_get_isolation_level = MySQLDialect.get_isolation_level
def patched_get_isolation_level(self, dbapi_connection):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT @@tx_isolation")
        row = cursor.fetchone()
    except Exception:
        cursor.close()
        return original_get_isolation_level(self, dbapi_connection)
    val = row[0]
    cursor.close()
    if isinstance(val, bytes):
        val = val.decode()
    return val.upper().replace("-", " ")
MySQLDialect.get_isolation_level = patched_get_isolation_level

original_fetch_setting = MySQLDialect._fetch_setting
def patched_fetch_setting(self, connection, setting_name):
    try:
        return original_fetch_setting(self, connection, setting_name)
    except Exception:
        sql = "SHOW VARIABLES LIKE '%s'" % setting_name
        show_var = connection.exec_driver_sql(sql)
        row = self._compat_first(show_var, charset=self._connection_charset)
        if not row:
            return None
        return row[1]
MySQLDialect._fetch_setting = patched_fetch_setting

# 2. Initialize application
app = Flask(__name__)

# Initialize Flask-SocketIO Emergency Dispatch Server
from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=20,
    ping_interval=10
)

# ─── REAL-TIME WEBSOCKET DISPATCH & SUBSCRIPTION HANDLERS ─────────
@socketio.on('connect')
def handle_connect():
    """Client handshake for emergency dispatch stream."""
    pass

@socketio.on('join_trade_room')
def handle_join_trade(data):
    """Subscribes an artisan to their trade emergency broadcast room."""
    if not isinstance(data, dict):
        return
    trade = data.get('trade_category')
    trades = data.get('trades', [])
    worker_id = data.get('worker_id')
    if trade:
        join_room(f"trade_{trade}")
        join_room(f"trade_{trade.lower()}")
    if isinstance(trades, list):
        for t in trades:
            if t:
                join_room(f"trade_{t}")
                join_room(f"trade_{t.lower()}")
    if worker_id:
        join_room(f"worker_{worker_id}")

@socketio.on('track_booking_room')
def handle_track_booking(data):
    """Subscribes a customer tracking screen to real-time status updates for a booking."""
    if not isinstance(data, dict):
        return
    booking_id = data.get('booking_id')
    if booking_id:
        join_room(f"booking_{booking_id}")

# Load config
from config import Config
app.config.from_object(Config)

# Initialize folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'signatures'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'work_photos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'audio_notes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'service_voices'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'service_photos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'completion_photos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'completion_voices'), exist_ok=True)

# Initialize Database
from database import db
db.init_app(app)

def create_app():
    """Application factory returning the configured Flask app instance."""
    return app

# Initialize Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)


# Load user loader
from models.user import User
from models.service_request import ServiceRequest
from models.contractor import Contractor
from models.finance import Payment
from models.communication import Notification
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
from routes.public import public_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.publisher import publisher_bp
from routes.worker import worker_bp
from routes.customer import customer_bp

app.register_blueprint(public_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(publisher_bp)
app.register_blueprint(worker_bp)
app.register_blueprint(customer_bp)

# Global variables context processor
@app.context_processor
def inject_global_data():
    from datetime import datetime
    return {
        'now': datetime.utcnow(),
        'year': datetime.utcnow().year
    }

# Emergency Lockout Middleware
@app.before_request
def check_emergency_lockouts():
    if request.endpoint and (request.endpoint.startswith('static') or request.endpoint in ('auth.login', 'auth.logout', 'auth.login_2fa', 'auth.register', 'auth.register_contractor', 'api_translate')):
        return
    if current_user.is_authenticated and current_user.role not in ('publisher', 'super_admin'):
        from models.communication import SystemSettings as PlatformSetting
        from flask_login import logout_user

        # 1. Check Global Maintenance Mode Switch
        if PlatformSetting.get_val('maintenance_mode', 'false') == 'true':
            logout_user()
            session.clear()
            flash("🚨 Platform Maintenance Mode is currently ACTIVE. Contractor login and portal access are restricted during software updates.", "danger")
            resp = make_response(redirect(url_for('auth.login')))
            resp.delete_cookie('remember_token')
            return resp

        # 2. Check Emergency Force Logout Signal across all active user sessions
        force_logout_ts = PlatformSetting.get_val('force_logout_timestamp', '0')
        try:
            force_logout_float = float(force_logout_ts)
        except (ValueError, TypeError):
            force_logout_float = 0.0

        session_login_time = float(session.get('login_time', 0.0))

        if force_logout_float > 0 and session_login_time < force_logout_float:
            logout_user()
            session.clear()
            flash("🚨 Emergency force logout executed by Publisher. Please sign in again.", "warning")
            resp = make_response(redirect(url_for('auth.login')))
            resp.delete_cookie('remember_token')
            return resp

        # 2. Check Role-Based Lockout Switches
        if current_user.role == 'worker' and PlatformSetting.get_val('lockout_workers', 'false') == 'true':
            logout_user()
            session.clear()
            flash("🚨 Worker portal access is locked out by Publisher for emergency maintenance.", "danger")
            resp = make_response(redirect(url_for('auth.login')))
            resp.delete_cookie('remember_token')
            return resp

        if current_user.role == 'customer' and PlatformSetting.get_val('lockout_customers', 'false') == 'true':
            logout_user()
            session.clear()
            flash("🚨 Customer Portal access is locked out by Publisher for emergency maintenance.", "danger")
            resp = make_response(redirect(url_for('auth.login')))
            resp.delete_cookie('remember_token')
            return resp

        if current_user.role in ('admin', 'manager', 'supervisor') and PlatformSetting.get_val('lockout_contractors', 'false') == 'true':
            logout_user()
            session.clear()
            flash("🚨 Contractor Admin Portal is locked out by Publisher for emergency maintenance.", "danger")
            resp = make_response(redirect(url_for('auth.login')))
            resp.delete_cookie('remember_token')
            return resp


# Smart, role-limited Service Assistant with contextual state management & intent recognition
@app.route('/api/assistant', methods=['POST'])
@login_required
def service_assistant():
    data = request.get_json(silent=True) or {}
    raw = str(data.get('message', '')).strip()
    message = raw.lower()
    language = data.get('language') or 'en'
    role = getattr(current_user, 'role', '')
    from datetime import timedelta, date as dt_date
    from services.ai_service import AIService

    def result(reply, url=None, action=None, state=None):
        payload = {'reply': reply}
        if url: payload['url'] = url
        if action: payload['action'] = action
        if state: payload['state'] = state
        return jsonify(payload)

    if not raw:
        return result('Hi! How can I assist you with SahakarSeva services today?')

    # Robust multi-intent classifier and entity extraction
    intent = AIService.classify_assistant_intent(raw, role=role)
    entities = AIService.extract_assistant_entities(raw)

    if role == 'customer':
        flow = session.get('assistant_booking') or {}

        # 1. CONTEXT SWITCHING & CANCELLATION GUARD:
        # If the user asks about status, complaints, FAQs, payment, emergency, or asks to cancel,
        # IMMEDIATELY interrupt slot-filling, clear session, and route to the new intent!
        if flow.get('step'):
            if intent in (
                AIService.INTENT_CHECK_STATUS,
                AIService.INTENT_CANCEL_FLOW,
                AIService.INTENT_COMPLAINT_OR_HELP,
                AIService.INTENT_GENERAL_FAQ,
                AIService.INTENT_PAYMENT,
                AIService.INTENT_EMERGENCY,
                AIService.INTENT_RESCHEDULE_OR_EDIT
            ):
                session.pop('assistant_booking', None)
                flow = {}
                # Fall through to execute the new intent below!

        # 2. ACTIVE BOOKING FLOW (if still in flow after context switch check)
        if flow.get('step'):
            step = flow['step']

            if step == 'category':
                chosen = entities.get('category')
                if chosen:
                    flow['category'] = chosen
                    flow['step'] = 'problem'
                    session['assistant_booking'] = flow
                    return result(f"Great. {chosen} service. What is the problem or service requirement?", state='booking_problem')

                # Strict validation: NEVER echo raw prompt into category slot
                return result(
                    'Which service do you need? Please choose from: Electrician, Plumber, Cleaning, AC Service, Carpenter, Painting, Driver, Gardener, Cook, or Caregiver.',
                    state='booking_category'
                )

            if step == 'problem':
                flow['title'] = raw.strip() or 'Service Request'
                flow['step'] = 'address'
                session['assistant_booking'] = flow
                return result('Got it. Where do you need the service? Type the address or say “use my saved address”.', state='booking_address')

            if step == 'address':
                addr = current_user.address or '' if any(k in message for k in ('saved','my address','mera address','मेरा पता','माझा पत्ता')) else raw.strip()
                if not addr:
                    return result('Please tell me the service address.')
                flow['address'] = addr
                flow['step'] = 'date'
                session['assistant_booking'] = flow
                return result('What date do you need the worker? Say today, tomorrow, or a date like 20-09-2026.', state='booking_date')

            if step == 'date':
                try:
                    d = entities.get('date')
                    if not d:
                        if 'tomorrow' in message or 'कल' in message or 'उद्या' in message:
                            d = dt_date.today() + timedelta(days=1)
                        elif 'today' in message or 'आज' in message or 'आजच' in message:
                            d = dt_date.today()
                        else:
                            match = re.search(r'(20\d\d)[-/](\d\d?)[-/](\d\d?)', message)
                            if not match:
                                match = re.search(r'(\d\d?)[-/](\d\d?)[-/](20\d\d)', message)
                                d = datetime.strptime(f'{match.group(3)}-{match.group(2)}-{match.group(1)}','%Y-%m-%d').date() if match else None
                            else:
                                d = datetime.strptime(f'{match.group(1)}-{match.group(2)}-{match.group(3)}','%Y-%m-%d').date()
                    if not d or d < dt_date.today():
                        raise ValueError
                    flow['visit_date'] = d.isoformat()
                    flow['step'] = 'time'
                    session['assistant_booking'] = flow
                    return result('What time is best for you? For example: 10 AM, 2 PM, or evening.', state='booking_time')
                except Exception:
                    return result('Please give a future date like 20-09-2026, or say today/tomorrow.')

            if step == 'time':
                flow['preferred_time'] = raw.strip() or 'Any time'
                flow['step'] = 'confirm'
                session['assistant_booking'] = flow
                return result(f"Please check your booking details:\n• Service: {flow.get('category')} — {flow.get('title')}\n• Address: {flow.get('address')}\n• Date: {flow.get('visit_date')}\n• Time: {flow.get('preferred_time')}\n\nSay YES to confirm booking. Say CHANGE to edit or CANCEL to exit.", state='booking_confirm')

            if step == 'confirm':
                if any(x in message for x in ('yes','y','haan','ha','हाँ','हो','book it','confirm','कर दो','कर')):
                    try:
                        count = ServiceRequest.query.count() + 1
                        rid = f"SR-{datetime.now().year}-{count:06d}"
                        contractor = Contractor.query.filter_by(is_active=True).first()
                        req = ServiceRequest(
                            request_id=rid,
                            contractor_id=contractor.id if contractor else 1,
                            customer_id=current_user.id,
                            customer_name=current_user.username,
                            mobile_number=current_user.phone or '',
                            category=flow.get('category') or 'General',
                            title=flow.get('title') or 'Service Request',
                            description=flow.get('title') or '',
                            address=flow.get('address') or current_user.address or 'Location to be confirmed',
                            status='Pending Review',
                            visit_date=datetime.strptime(flow.get('visit_date'),'%Y-%m-%d').date() if flow.get('visit_date') else None,
                            preferred_time=flow.get('preferred_time') or None,
                            priority='Normal'
                        )
                        db.session.add(req)
                        db.session.flush()
                        # Notify operational admins
                        admin_users = User.query.filter(User.role.in_(['admin','manager','supervisor'])).all()
                        if not admin_users:
                            admin_users = [User.query.get(1)] if User.query.get(1) else []
                        for admin_user in admin_users:
                            db.session.add(Notification(user_id=admin_user.id, title='New Service Booking', message=f'{current_user.username} created booking {rid}.', type='Info'))
                        db.session.commit()
                        session.pop('assistant_booking', None)
                        return result(f'Booked ✅ Your booking number is {rid}. The cooperative society has received it.', url_for('customer.bookings_page'), 'Open My Bookings', 'booking_created')
                    except Exception:
                        db.session.rollback()
                        session.pop('assistant_booking', None)
                        return result('I could not create the booking right now. Please try again or use Book Service.', state='booking_error')
                if any(x in message for x in ('change','edit','बदल','गलत')):
                    flow['step'] = 'category'
                    session['assistant_booking'] = flow
                    return result('No problem. Which service do you need? We can start again.', state='booking_change')
                if any(x in message for x in ('no','n','नहीं','cancel','abort')):
                    session.pop('assistant_booking', None)
                    return result('Booking cancelled. How else can I assist you today?')
                return result('Please say YES to confirm, CHANGE to edit, or CANCEL to stop.')

        # 3. ROOT INTENT ROUTING (outside booking flow or context switched)
        if intent == AIService.INTENT_CANCEL_FLOW:
            session.pop('assistant_booking', None)
            return result('Booking cancelled. How else can I assist you with SahakarSeva services today?')

        # Status & tracking intent
        if intent == AIService.INTENT_CHECK_STATUS:
            status_res = AIService.lookup_booking_status(customer_id=current_user.id, entities=entities, language=language)
            return result(status_res['reply'], url=status_res.get('url', url_for('customer.bookings_page')), action=status_res.get('action', 'Open My Bookings'), state='booking_status')

        # New service booking intent
        if intent == AIService.INTENT_BOOK_SERVICE:
            category = entities.get('category')
            if category:
                session['assistant_booking'] = {'step': 'problem', 'category': category}
                return result(f"Sure, booking {category} service. What is the problem or service requirement?", state='booking_problem')
            else:
                session['assistant_booking'] = {'step': 'category'}
                return result('Sure! What type of service do you need? You can choose Electrician, Plumber, Cleaning, AC Service, Carpenter, Painting, Driver, Gardener, Cook, or Caregiver.', state='booking_category')

        # Reschedule / edit booking
        if intent == AIService.INTENT_RESCHEDULE_OR_EDIT:
            latest = ServiceRequest.query.filter_by(customer_id=current_user.id).order_by(ServiceRequest.created_at.desc()).first()
            if not latest:
                return result('You do not have any bookings to reschedule yet.', url_for('customer.book_service'), 'Book a Service')
            if latest.assigned_worker_id and latest.status in ('In Progress', 'Travelling'):
                return result(f'Booking {latest.request_id} is already in progress with worker. Please message support to coordinate changes.', url_for('customer.messages_page'), 'Message Support')
            changed = []
            date_value = entities.get('date')
            if not date_value:
                if 'tomorrow' in message or 'कल' in message or 'उद्या' in message:
                    date_value = dt_date.today() + timedelta(days=1)
                elif 'today' in message or 'आज' in message:
                    date_value = dt_date.today()
            if date_value:
                latest.visit_date = date_value
                changed.append(f'date to {date_value.strftime("%d %b %Y")}')
            mtime = re.search(r'\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', message)
            if mtime:
                latest.preferred_time = mtime.group(0).upper()
                changed.append(f'time to {latest.preferred_time}')
            if changed:
                db.session.add(Notification(user_id=(latest.contractor.user_id if latest.contractor and latest.contractor.user_id else 1), title='Booking Updated', message=f'Customer {current_user.username} updated booking {latest.request_id}.', type='Info'))
                db.session.commit()
                return result(f"Done ✅ Booking {latest.request_id} updated: {', '.join(changed)}.", url_for('customer.bookings_page'), 'Open My Bookings')
            return result(f'Yes, I can update booking {latest.request_id}. Tell me the new date or time, or open the edit page.', url_for('customer.edit_booking_page', request_id=latest.id), 'Edit Booking')

        # Payment intent
        if intent == AIService.INTENT_PAYMENT:
            faq_res = AIService.get_faq_or_help_response(intent, raw, language=language)
            return result(faq_res['reply'], url=faq_res.get('url', url_for('customer.payments_page')), action=faq_res.get('action', 'Open Payments'))

        # Emergency intent
        if intent == AIService.INTENT_EMERGENCY:
            faq_res = AIService.get_faq_or_help_response(intent, raw, language=language)
            return result(faq_res['reply'], url=faq_res.get('url', url_for('customer.dashboard') + '#emergency'), action=faq_res.get('action', 'Emergency Help'))

        # Complaint & support intent
        if intent == AIService.INTENT_COMPLAINT_OR_HELP:
            faq_res = AIService.get_faq_or_help_response(intent, raw, language=language)
            return result(faq_res['reply'], url=faq_res.get('url', url_for('customer.messages_page')), action=faq_res.get('action', 'Lodge Complaint / Support'))

        # General FAQ intent
        if intent == AIService.INTENT_GENERAL_FAQ:
            faq_res = AIService.get_faq_or_help_response(intent, raw, language=language)
            return result(faq_res['reply'], url=faq_res.get('url', url_for('customer.book_service')), action=faq_res.get('action', 'Explore Services'))

        if any(k in message for k in ('profile','name change','phone change','address change','प्रोफाइल')):
            return result('You can update your name, phone and address from Profile.', url_for('customer.profile_page'), 'Open Profile')

        return result('I can help you book a service, check booking status, reschedule, handle payments, and access emergency support. How can I assist you today?')

    if role == 'worker':
        if intent == AIService.INTENT_WORKER_JOBS:
            job = ServiceRequest.query.filter_by(assigned_worker_id=current_user.id).order_by(ServiceRequest.created_at.desc()).first()
            if job:
                text = f"Your latest job: {job.category} — {job.title}. Status: {str(job.status).replace('_',' ')}."
                if job.address: text += f" Address: {job.address}."
                return result(text, url_for('worker.service_requests'), 'Open Jobs')
            return result('You have no assigned jobs right now.', url_for('worker.service_requests'), 'Open Jobs')

        if intent == AIService.INTENT_WORKER_ATTENDANCE:
            return result('Check in when you reach the job location. Your GPS attendance and timestamps are recorded securely.', url_for('worker.attendance_page'), 'Open Attendance')

        if intent == AIService.INTENT_WORKER_EARNINGS:
            total = Payment.query.filter_by(worker_id=current_user.id, type='salary').all()
            month_total = sum(float(x.amount or 0) for x in total)
            return result((f'Your recorded earnings are ₹{month_total:,.2f}. 88% direct cooperative living wage guaranteed.' if total else 'No worker earnings are recorded yet.'), url_for('worker.earnings_page'), 'Open Earnings')

        if intent == AIService.INTENT_WORKER_BENEFITS:
            return result('Your PMJJBY/PMSBY welfare coverage, insurance policy status, and skill certificates are on Benefits.', url_for('worker.benefits_page'), 'Open Benefits')

        if intent == AIService.INTENT_WORKER_PROFILE:
            return result('You can edit your work skills, trade certifications, and contact details from Profile.', url_for('worker.profile_page'), 'Open Profile')

        if intent == AIService.INTENT_WORKER_MESSAGES:
            return result('For work-related coordination or help, you can message Admin from Messages.', url_for('worker.messages_page'), 'Open Messages')

        return result('I can help with your assigned jobs, GPS attendance check-in, earnings, welfare benefits, and work messages.')

    return result('This assistant is available only to customers and workers for service-related help.')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(app.static_folder, 'service-worker.js', mimetype='application/javascript')

# Public landing alias for backward compatibility
@app.route('/landing')
def home():
    return redirect(url_for('public.index'))

# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', error=str(e)), 500

# Global Search API
@app.route('/api/search')
@login_required
def global_search():
    q = request.args.get('q', '').strip().lower()
    if not q or len(q) < 2:
        return jsonify([])

    results = []
    role = current_user.role

    # Navigation-based quick links
    nav_links = []
    if role == 'admin':
        nav_links = [
            {'title': 'Admin Dashboard', 'url': url_for('admin.dashboard'), 'type': 'Page'},
            {'title': 'Service Requests', 'url': url_for('admin.service_requests'), 'type': 'Page'},
            {'title': 'Workers', 'url': url_for('admin.dashboard') + '#workers', 'type': 'Page'},
            {'title': 'Customers', 'url': url_for('admin.dashboard') + '#customers', 'type': 'Page'},
            {'title': 'Payments & Invoices', 'url': url_for('admin.dashboard') + '#payments', 'type': 'Page'},
            {'title': 'Materials Inventory', 'url': url_for('admin.dashboard') + '#materials', 'type': 'Page'},
            {'title': 'Equipment Registry', 'url': url_for('admin.dashboard') + '#equipment', 'type': 'Page'},
            {'title': 'Reports Generator', 'url': url_for('admin.dashboard') + '#reports', 'type': 'Page'},
            {'title': 'Analytics', 'url': url_for('admin.dashboard') + '#analytics', 'type': 'Page'},
        ]
    elif role == 'worker':
        nav_links = [
            {'title': 'Worker Dashboard', 'url': url_for('worker.dashboard'), 'type': 'Page'},
            {'title': "Today's Jobs", 'url': url_for('worker.dashboard') + '#jobs', 'type': 'Page'},
            {'title': 'Service Jobs', 'url': url_for('worker.service_requests'), 'type': 'Page'},
            {'title': 'GPS Check-In', 'url': url_for('worker.dashboard') + '#attendance', 'type': 'Page'},
        ]
    elif role == 'customer':
        nav_links = [
            {'title': 'Client Hub', 'url': url_for('customer.dashboard'), 'type': 'Page'},
            {'title': 'Book Service', 'url': url_for('customer.book_service'), 'type': 'Page'},
            {'title': 'My Services', 'url': url_for('customer.dashboard') + '#services', 'type': 'Page'},
            {'title': 'Invoices & Pay', 'url': url_for('customer.dashboard') + '#payments', 'type': 'Page'},
        ]

    results = [l for l in nav_links if q in l['title'].lower()]
    return jsonify(results[:10])

from flask import Response
from services.pdf_service import PDFService

@app.route('/api/pdf/invoice/<int:payment_id>')
@login_required
def download_invoice(payment_id):
    try:
        pdf_data = PDFService.generate_invoice_pdf(payment_id)
        if pdf_data is None:
            return "Invoice not found", 404
        return Response(
            pdf_data,
            mimetype="application/pdf",
            headers={"Content-disposition": f"attachment; filename=invoice_{payment_id}.pdf"}
        )
    except Exception as e:
        return str(e), 500

@app.route('/api/pdf/report/<string:report_type>')
@login_required
def download_report(report_type):
    try:
        pdf_data = PDFService.generate_report_pdf(report_type)
        return Response(
            pdf_data,
            mimetype="application/pdf",
            headers={"Content-disposition": f"attachment; filename=report_{report_type}.pdf"}
        )
    except Exception as e:
        return str(e), 500

@app.route('/api/pdf/quotation/<int:quotation_id>')
@login_required
def download_quotation(quotation_id):
    try:
        pdf_data = PDFService.generate_quotation_pdf(quotation_id)
        if pdf_data is None:
            return "Quotation not found", 404
        return Response(
            pdf_data,
            mimetype="application/pdf",
            headers={"Content-disposition": f"attachment; filename=quotation_{quotation_id}.pdf"}
        )
    except Exception as e:
        return str(e), 500

# ─── GOOGLE TRANSLATE API BATCH PROXY ─────────────────────────────
import urllib.request
import urllib.parse
import json
import re

_TRANSLATION_CACHE = {}

@app.route('/api/translate', methods=['POST'])
def api_translate():
    try:
        data = request.get_json(force=True, silent=True) or {}
        texts = data.get('texts', [])
        target = data.get('target', 'mr')
        
        if not texts or target == 'en':
            return jsonify({'translations': texts})
        
        results = {}
        untranslated = []
        
        for idx, t in enumerate(texts):
            clean_t = t.strip() if isinstance(t, str) else ''
            if not clean_t:
                results[idx] = t
                continue
            cache_key = f"{target}:{clean_t}"
            if cache_key in _TRANSLATION_CACHE:
                results[idx] = _TRANSLATION_CACHE[cache_key]
            else:
                untranslated.append((idx, clean_t))
        
        if untranslated:
            batch_size = 35
            for i in range(0, len(untranslated), batch_size):
                batch = untranslated[i:i + batch_size]
                combined = ' |@| '.join([item[1] for item in batch])
                url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target}&dt=t&q={urllib.parse.quote(combined)}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                try:
                    with urllib.request.urlopen(req, timeout=6) as resp:
                        res = json.loads(resp.read().decode('utf-8'))
                        translated_combined = ''.join([part[0] for part in res[0] if part[0]])
                        translated_parts = [p.strip() for p in re.split(r'\s*\|\s*@\s*\|\s*', translated_combined)]
                        
                        for k, (orig_idx, orig_text) in enumerate(batch):
                            tr_part = translated_parts[k] if k < len(translated_parts) else orig_text
                            cache_key = f"{target}:{orig_text}"
                            _TRANSLATION_CACHE[cache_key] = tr_part
                            results[orig_idx] = tr_part
                except Exception as ex:
                    for orig_idx, orig_text in batch:
                        results[orig_idx] = orig_text
        
        final_translations = [results.get(i, texts[i]) for i in range(len(texts))]
        return jsonify({'translations': final_translations})
    except Exception as e:
        return jsonify({'error': str(e), 'translations': texts}), 500

if __name__ == '__main__':
    import sys, socket
    
    # Auto-detect LAN IP for mobile access
    lan_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            lan_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            pass

    use_ssl = '--ssl' in sys.argv or os.environ.get('USE_SSL', '').lower() in ('1', 'true', 'yes')
    proto = 'https' if use_ssl else 'http'

    print("=" * 72)
    print("  🚀 SahakarSeva Cooperative Services Platform is Running!")
    print("=" * 72)
    print(f"  💻 Localhost:       {proto}://127.0.0.1:5000")
    print(f"  📱 Mobile / LAN:    {proto}://{lan_ip}:5000")
    print("-" * 72)
    if not use_ssl:
        print("  ⚠️  CRITICAL FOR MOBILE BROWSERS:")
        print("  • Type the full URL including 'http://' explicitly in your phone browser:")
        print(f"      👉  http://{lan_ip}:5000")
        print("  • DO NOT omit 'http://' — mobile Chrome & Safari default to HTTPS,")
        print("    which causes 'Bad request version / 400 Bad Request'.")
    else:
        print("  🔒 Running in HTTPS mode (adhoc SSL certificate).")
        print("  • Mobile browsers will show an untrusted certificate warning.")
        print("    Tap 'Advanced' -> 'Proceed' to open the app.")
    print("=" * 72)

    if use_ssl:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')
    else:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)


