from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from database import db
from models.contractor import Contractor
from models.service_request import ServiceRequest
from models.worker import Worker
from models.finance import Payment

public_bp = Blueprint('public', __name__)

@public_bp.route('/home')
@public_bp.route('/')
def index():
    # Fetch active cooperative societies for the showcase
    try:
        societies = Contractor.query.filter_by(is_active=True).limit(6).all()
    except Exception:
        societies = []

    # Calculate real-time snapshot metrics or fallback to prototype metrics
    metrics = {
        'wages_distributed': '₹2,48,500+',
        'jobs_completed': '1,240+',
        'social_security_coverage': '100%',
        'avg_dispatch_time': '< 15 Mins'
    }

    # Available cooperative trade services (10 core trades under SIH 26089)
    services = [
        {
            'id': 'electrical',
            'title': 'Electrical Systems & Power',
            'category': 'Electrical',
            'icon': 'zap',
            'description': 'Short-circuit fixes, wiring diagnostics, MCB panels, inverter setups & society illumination.',
            'base_rate': '₹299',
            'statutory_split': '88% to Electrician',
            'turnaround': '12 mins dispatch'
        },
        {
            'id': 'plumbing',
            'title': 'Plumbing & Water Sanitation',
            'category': 'Plumbing',
            'icon': 'droplets',
            'description': 'Leakage mitigation, high-pressure line clearing, motor installations & overhead tank sanitization.',
            'base_rate': '₹349',
            'statutory_split': '88% to Plumber',
            'turnaround': '15 mins dispatch'
        },
        {
            'id': 'carpentry',
            'title': 'Carpentry & Structural Woodwork',
            'category': 'Carpentry',
            'icon': 'hammer',
            'description': 'Security lock installation, modular hinge repair, customized shelving & door alignment.',
            'base_rate': '₹399',
            'statutory_split': '88% to Carpenter',
            'turnaround': '25 mins dispatch'
        },
        {
            'id': 'painting',
            'title': 'Painting & Surface Waterproofing',
            'category': 'Painting',
            'icon': 'paint-bucket',
            'description': 'Anti-fungal damp proofing, touch-up wall coatings & cooperative society exterior finishing.',
            'base_rate': '₹599',
            'statutory_split': '88% to Artisan',
            'turnaround': 'Scheduled Visit'
        },
        {
            'id': 'cleaning',
            'title': 'Community & Deep Cleaning',
            'category': 'Housekeeping',
            'icon': 'sparkles',
            'description': 'Apartment floor scrubbing, residential society stairwell & common area eco-sanitization.',
            'base_rate': '₹499',
            'statutory_split': '88% to Cleaning Crew',
            'turnaround': '20 mins dispatch'
        },
        {
            'id': 'domestic_help',
            'title': 'Domestic Helpers & Kitchen Aid',
            'category': 'Housekeeping',
            'icon': 'home',
            'description': 'Verified household daily help, kitchen assistance, dishwashing & laundry support.',
            'base_rate': '₹249',
            'statutory_split': '88% to Domestic Helper',
            'turnaround': 'Scheduled / On-Demand'
        },
        {
            'id': 'caregiver',
            'title': 'Caregiving & Patient Support',
            'category': 'Caregiving',
            'icon': 'heart-pulse',
            'description': 'Compassionate elderly care, mobility assistance, medication scheduling & postoperative aid.',
            'base_rate': '₹499',
            'statutory_split': '88% to Caregiver',
            'turnaround': 'Immediate / Shift'
        },
        {
            'id': 'driver',
            'title': 'Verified Chauffeurs & Drivers',
            'category': 'Drivers',
            'icon': 'car',
            'description': 'Licensed and background-verified personal, family, and intercity cooperative drivers.',
            'base_rate': '₹399',
            'statutory_split': '88% to Driver',
            'turnaround': '30 mins dispatch'
        },
        {
            'id': 'gardener',
            'title': 'Gardening & Horticulture Care',
            'category': 'Gardening',
            'icon': 'flower-2',
            'description': 'Lawn mowing, balcony garden styling, pest prevention, organic fertilizing & tree pruning.',
            'base_rate': '₹349',
            'statutory_split': '88% to Gardener',
            'turnaround': 'Scheduled Visit'
        },
        {
            'id': 'technician',
            'title': 'Technicians & Appliance Maintenance',
            'category': 'Appliance',
            'icon': 'wrench',
            'description': 'AC coil servicing, geyser thermostat diagnostics, washing machine descaling & RO filters.',
            'base_rate': '₹349',
            'statutory_split': '88% to Technician',
            'turnaround': '18 mins dispatch'
        }
    ]

    return render_template(
        'public/index.html',
        societies=societies,
        metrics=metrics,
        services=services
    )

@public_bp.route('/marketplace')
def marketplace():
    return redirect(url_for('customer.marketplace'))

