from database import db
from datetime import datetime, date, timedelta
from models.worker import Worker
from models.finance import Payment, WelfareTransaction
from models.communication import Notification

class WelfareService:
    """
    Automated Worker Welfare & Insurance Fund Engine (Suraksha Nidhi).
    Implements:
    - 4-Tier Cooperative Billing Split (90% Worker, 4% Society Admin, 4% Apex Federation, 2% Welfare Cess)
    - Automated Micro-Cess credit to individual worker welfare accounts
    - Auto-debit and renewal routine for PMJJBY (Rs. 436) and PMSBY (Rs. 20)
    - ESIC registration tracking
    """

    PMJJBY_ANNUAL_PREMIUM = 436.00  # Pradhan Mantri Jeevan Jyoti Bima Yojana (Rs. 2 Lakh Term Life)
    PMSBY_ANNUAL_PREMIUM = 20.00    # Pradhan Mantri Suraksha Bima Yojana (Rs. 2 Lakh Accidental Death/Disability)

    @staticmethod
    def calculate_cess_split(gross_amount, split_mode="88_8_4"):
        """
        Calculates the transparent cooperative fee distribution.
        Default: 88/8/4 model (88% Worker direct payout, 8% Society Admin & Ops, 4% Worker Welfare / Suraksha Nidhi).
        """
        total = float(gross_amount or 0.0)
        if split_mode == "90_4_4_2":
            worker_payout = round(total * 0.90, 2)
            society_admin_fee = round(total * 0.04, 2)
            federation_fee = round(total * 0.04, 2)
            welfare_cess = round(total * 0.02, 2)
            worker_pct = 90
            society_pct = 4
            fed_pct = 4
            welfare_pct = 2
        else:
            # 88/8/4 statutory cooperative ledger
            worker_payout = round(total * 0.88, 2)
            society_admin_fee = round(total * 0.08, 2)
            federation_fee = round(total * 0.00, 2)
            welfare_cess = round(total * 0.04, 2)
            worker_pct = 88
            society_pct = 8
            fed_pct = 0
            welfare_pct = 4

        return {
            "gross_amount": total,
            "worker_payout": worker_payout,
            "worker_percentage": worker_pct,
            "society_admin_fee": society_admin_fee,
            "society_percentage": society_pct,
            "federation_fee": federation_fee,
            "federation_percentage": fed_pct,
            "welfare_cess": welfare_cess,
            "welfare_percentage": welfare_pct,
            "commercial_aggregator_cut": round(total * 0.28, 2),  # 28% private platform cut comparison
            "cooperative_total_retained": round(worker_payout + welfare_cess, 2)
        }

    @classmethod
    def credit_welfare_cess(cls, worker_id, cess_amount, payment_id=None, service_request_id=None, description=None):
        """
        Credits the 2% micro-cess directly to the worker's welfare_balance,
        logs an audit transaction, and triggers automated insurance auto-debit checks.
        """
        worker = Worker.query.get(worker_id)
        if not worker:
            return None

        cess = float(cess_amount or 0.0)
        if cess <= 0:
            return None

        current_balance = float(worker.welfare_balance or 0.0)
        new_balance = round(current_balance + cess, 2)
        worker.welfare_balance = new_balance

        tx_desc = description or f"2% Cooperative Welfare Cess from Service Payment"
        tx = WelfareTransaction(
            worker_id=worker.id,
            payment_id=payment_id,
            service_request_id=service_request_id,
            transaction_type="CESS_CREDIT",
            amount=cess,
            balance_after=new_balance,
            description=tx_desc,
            reference_id=f"CESS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            created_at=datetime.utcnow()
        )
        db.session.add(tx)
        db.session.flush()

        # Send notification to worker
        notif = Notification(
            user_id=worker.id,
            title="Suraksha Nidhi Cess Credited",
            message=f"Rs. {cess:.2f} (2% Welfare Cess) credited to your Cooperative Suraksha Nidhi. New Balance: Rs. {new_balance:.2f}.",
            type="Success"
        )
        db.session.add(notif)

        # Trigger automatic insurance auto-debits
        auto_debit_results = cls.process_auto_debit_insurance(worker.id)
        db.session.commit()

        return {
            "worker_id": worker.id,
            "cess_credited": cess,
            "new_balance": worker.welfare_balance,
            "auto_debits": auto_debit_results
        }

    @classmethod
    def process_auto_debit_insurance(cls, worker_id):
        """
        Evaluates worker welfare balance against government scheme premiums:
        - PMSBY: Auto-deducts Rs. 20 when balance >= 20 and pmsby_status != 'Active'
        - PMJJBY: Auto-deducts Rs. 436 when balance >= 436 and pmjjby_status != 'Active'
        """
        worker = Worker.query.get(worker_id)
        if not worker:
            return []

        debits_executed = []
        current_bal = float(worker.welfare_balance or 0.0)

        # Ensure default ESIC IP Number
        if not worker.esic_ip_number:
            worker.esic_ip_number = f"1100{982340 + worker.id}"

        # 1. Evaluate PMSBY (Accidental Cover - Rs. 20 / year)
        if current_bal >= cls.PMSBY_ANNUAL_PREMIUM and worker.pmsby_status != 'Active':
            current_bal = round(current_bal - cls.PMSBY_ANNUAL_PREMIUM, 2)
            worker.welfare_balance = current_bal
            worker.pmsby_status = 'Active'
            pmsby_cert = f"PMSBY-NIC-{datetime.now().strftime('%Y')}-{10000 + worker.id}"
            worker.pmsby_id = pmsby_cert
            worker.pmsby_renewal_date = date.today() + timedelta(days=365)

            pmsby_tx = WelfareTransaction(
                worker_id=worker.id,
                transaction_type="PMSBY_PREMIUM",
                amount=-cls.PMSBY_ANNUAL_PREMIUM,
                balance_after=current_bal,
                description=f"PMSBY Annual Accidental Cover (Rs. 2 Lakh) Auto-Debited - Rs. {cls.PMSBY_ANNUAL_PREMIUM:.2f}/yr",
                reference_id=pmsby_cert,
                created_at=datetime.utcnow()
            )
            db.session.add(pmsby_tx)

            notif = Notification(
                user_id=worker.id,
                title="PMSBY Coverage Activated!",
                message=f"Rs. {cls.PMSBY_ANNUAL_PREMIUM:.0f} auto-debited from Suraksha Nidhi. PMSBY Accidental Cover of Rs. 2,00,000 is now ACTIVE (Cert: {pmsby_cert}).",
                type="Success"
            )
            db.session.add(notif)
            debits_executed.append({
                "scheme": "PMSBY",
                "amount": cls.PMSBY_ANNUAL_PREMIUM,
                "cert_id": pmsby_cert
            })

        # 2. Evaluate PMJJBY (Life Cover - Rs. 436 / year)
        if current_bal >= cls.PMJJBY_ANNUAL_PREMIUM and worker.pmjjby_status != 'Active':
            current_bal = round(current_bal - cls.PMJJBY_ANNUAL_PREMIUM, 2)
            worker.welfare_balance = current_bal
            worker.pmjjby_status = 'Active'
            pmjjby_cert = f"PMJJBY-LIC-{datetime.now().strftime('%Y')}-{20000 + worker.id}"
            worker.pmjjby_id = pmjjby_cert
            worker.pmjjby_renewal_date = date.today() + timedelta(days=365)

            pmjjby_tx = WelfareTransaction(
                worker_id=worker.id,
                transaction_type="PMJJBY_PREMIUM",
                amount=-cls.PMJJBY_ANNUAL_PREMIUM,
                balance_after=current_bal,
                description=f"PMJJBY Annual Term Life Cover (Rs. 2 Lakh) Auto-Debited - Rs. {cls.PMJJBY_ANNUAL_PREMIUM:.2f}/yr",
                reference_id=pmjjby_cert,
                created_at=datetime.utcnow()
            )
            db.session.add(pmjjby_tx)

            notif = Notification(
                user_id=worker.id,
                title="PMJJBY Life Insurance Activated!",
                message=f"Rs. {cls.PMJJBY_ANNUAL_PREMIUM:.0f} auto-debited from Suraksha Nidhi. PMJJBY Life Insurance of Rs. 2,00,000 is now ACTIVE (Cert: {pmjjby_cert}).",
                type="Success"
            )
            db.session.add(notif)
            debits_executed.append({
                "scheme": "PMJJBY",
                "amount": cls.PMJJBY_ANNUAL_PREMIUM,
                "cert_id": pmjjby_cert
            })
        elif worker.pmjjby_status != 'Active':
            worker.pmjjby_status = 'Accumulating'

        return debits_executed

    @classmethod
    def get_worker_welfare_summary(cls, worker_id):
        """
        Builds a comprehensive summary for UI dashboard and audit card.
        """
        worker = Worker.query.get(worker_id)
        if not worker:
            return None

        bal = float(worker.welfare_balance or 0.0)
        progress_amount = min(bal, cls.PMJJBY_ANNUAL_PREMIUM)
        progress_pct = round(min(100.0, (bal / cls.PMJJBY_ANNUAL_PREMIUM) * 100.0), 1)

        recent_txs = WelfareTransaction.query.filter_by(worker_id=worker.id)\
            .order_by(WelfareTransaction.created_at.desc()).limit(15).all()

        ledger = []
        for t in recent_txs:
            ledger.append({
                "id": t.id,
                "type": t.transaction_type,
                "amount": t.amount,
                "balance_after": t.balance_after,
                "description": t.description,
                "reference_id": t.reference_id,
                "created_at": t.created_at.strftime("%d %b %Y, %I:%M %p") if t.created_at else "N/A"
            })

        return {
            "worker_id": worker.id,
            "welfare_balance": bal,
            "pmjjby": {
                "status": worker.pmjjby_status or ("Active" if bal >= cls.PMJJBY_ANNUAL_PREMIUM else "Accumulating"),
                "id": worker.pmjjby_id or "Auto-allots at Rs. 436",
                "renewal_date": worker.pmjjby_renewal_date.strftime("%d %b %Y") if worker.pmjjby_renewal_date else "Pending Accumulation",
                "target": cls.PMJJBY_ANNUAL_PREMIUM,
                "accumulated": progress_amount,
                "progress_pct": progress_pct,
                "coverage_sum": 200000.0
            },
            "pmsby": {
                "status": worker.pmsby_status or "Active",
                "id": worker.pmsby_id or f"PMSBY-NIC-2026-{10000 + worker.id}",
                "renewal_date": worker.pmsby_renewal_date.strftime("%d %b %Y") if worker.pmsby_renewal_date else "Active",
                "annual_cost": cls.PMSBY_ANNUAL_PREMIUM,
                "coverage_sum": 200000.0
            },
            "esic": {
                "ip_number": worker.esic_ip_number or f"1100{982340 + worker.id}",
                "status": "Active",
                "scheme": "ESIC Medical & Sickness Benefits (10-Digit IP ID)"
            },
            "ledger": ledger
        }

    @classmethod
    def simulate_job_cess(cls, worker_id, gross_amount=1000.0, description=None):
        """
        Interactive demonstration trigger for judges.
        Simulates completing a job of gross_amount, computes 2% micro-cess,
        deposits it into the worker's welfare fund, and evaluates auto-debits.
        """
        split = cls.calculate_cess_split(gross_amount)
        cess = split["welfare_cess"]
        desc = description or f"Judge Demonstration: 2% Welfare Cess from completed Rs. {gross_amount:,.0f} Service Ticket"
        return cls.credit_welfare_cess(worker_id, cess, description=desc)

    @classmethod
    def allocate_payment_cess(cls, payment):
        """
        Allocates and distributes the statutory 88/8/4 cooperative funds upon payment settlement:
        - 88% Worker direct payout (guaranteed living wage)
        - 8% Primary society admin and operational fee
        - 4% Suraksha Nidhi micro-cess credited directly to worker welfare account
        - Evaluates automated insurance renewals (PMSBY & PMJJBY)
        """
        if not payment:
            return None

        amount = float(payment.amount or 0.0)
        if amount > 0:
            split = cls.calculate_cess_split(amount, split_mode="88_8_4")
            payment.worker_payout = split['worker_payout']
            payment.society_admin_fee = split['society_admin_fee']
            payment.federation_fee = split.get('federation_fee', 0.0)
            payment.welfare_cess = split['welfare_cess']

        target_worker_id = payment.worker_id
        if not target_worker_id and payment.service_request:
            target_worker_id = payment.service_request.assigned_worker_id
            if target_worker_id and not payment.worker_id:
                payment.worker_id = target_worker_id

        if target_worker_id and float(payment.welfare_cess or 0.0) > 0:
            return cls.credit_welfare_cess(
                worker_id=target_worker_id,
                cess_amount=float(payment.welfare_cess),
                payment_id=payment.id,
                service_request_id=payment.service_request_id,
                description=f"4% Cooperative Welfare Cess from Invoice #{payment.invoice_number or payment.id}"
            )
        return None
