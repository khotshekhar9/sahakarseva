from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from models.finance import Payment
from models.service_request import ServiceRequest
from models.attendance import Attendance

class PDFService:
    
    @staticmethod
    def generate_invoice_pdf(payment_id):
        """
        Generates a clean, professional PDF invoice displaying transparent 4-tier cooperative
        distribution and statutory 2% Worker Welfare & Social Security Cess contribution.
        """
        payment = Payment.query.get(payment_id)
        if not payment:
            return None
            
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'InvoiceTitle', parent=styles['Heading1'],
            fontSize=22, leading=26, textColor=colors.HexColor('#1e40af'), spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'InvoiceSubtitle', parent=styles['Normal'],
            fontSize=10, leading=14, textColor=colors.HexColor('#475569'), spaceAfter=12
        )
        body_style = ParagraphStyle(
            'InvoiceBody', parent=styles['Normal'],
            fontSize=9, leading=13, textColor=colors.HexColor('#334155')
        )
        header_style = ParagraphStyle(
            'InvoiceHeader', parent=styles['Heading3'],
            fontSize=11, leading=15, textColor=colors.HexColor('#0f172a'), spaceAfter=6
        )
        welfare_banner_style = ParagraphStyle(
            'WelfareBanner', parent=styles['Normal'],
            fontSize=8.5, leading=12, textColor=colors.HexColor('#166534')
        )
        
        # Header Info
        story.append(Paragraph("SahakarSeva Labour Cooperative Federation", title_style))
        story.append(Paragraph("Ministry of Cooperation Compliant - Digital Service Invoice & Welfare Statement", subtitle_style))
        story.append(Spacer(1, 6))

        # Cooperative Mission Highlight Box
        coop_intro = [
            [Paragraph(
                "<b>Cooperative Empowerment Model:</b> This platform operates under cooperative bye-laws ensuring fair wages and worker social security. "
                "Unlike private aggregators charging 25%–30% commissions, SahakarSeva guarantees 90% direct payout to the artisan and earmarks a 2% micro-cess "
                "to fund national social security schemes (PMJJBY & PMSBY).",
                ParagraphStyle('CoopIntro', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor('#1e3a8a'))
            )]
        ]
        t_intro = Table(coop_intro, colWidths=[540])
        t_intro.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#bfdbfe')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_intro)
        story.append(Spacer(1, 12))
        
        # Technician / Worker resolution
        worker_name = "Assigned Cooperative Member"
        worker_skills = "Verified Technician"
        if payment.worker_id and payment.worker and payment.worker.user:
            worker_name = payment.worker.user.username.capitalize()
            worker_skills = payment.worker.skills or "Technician"
        elif payment.service_request and payment.service_request.assigned_worker:
            w_obj = payment.service_request.assigned_worker
            if w_obj.user:
                worker_name = w_obj.user.username.capitalize()
            worker_skills = w_obj.skills or "Technician"

        # Client and Project details
        client_name = payment.customer.company_name if (payment.customer and payment.customer.company_name) else (payment.customer.user.username if payment.customer and payment.customer.user else "Household Client")
        service_title = payment.service_request.title if payment.service_request else (payment.project.name if payment.project else "Household & Community Service")
        
        # Invoice metadata table
        meta_data = [
            ["Invoice Number:", payment.invoice_number or f"INV-LOG-{payment.id}", "Customer Name:", client_name],
            ["Issue Date:", payment.date.strftime('%B %d, %Y') if payment.date else "N/A", "Service Ticket:", service_title[:32]],
            ["Payment Status:", payment.status.upper(), "Assigned Artisan:", f"{worker_name} ({worker_skills})"],
            ["Regulatory Framework:", "Multi-State Cooperative Societies Act", "Social Security Link:", "PMJJBY / PMSBY / ESIC Active"]
        ]
        t_meta = Table(meta_data, colWidths=[110, 160, 110, 160])
        t_meta.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f8fafc')),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 14))

        # Calculate / Retrieve 88/8/4 Cooperative Split
        gross_amt = float(payment.amount or 0.0)
        worker_wage = float(payment.worker_payout or round(gross_amt * 0.88, 2))
        society_fee = float(payment.society_admin_fee or round(gross_amt * 0.08, 2))
        welfare_cess = float(payment.welfare_cess or round(gross_amt * 0.04, 2))
        
        # Financial breakdown table with transparent distribution
        table_data = [
            ["Billing Component & Cooperative Allocation", "Share (%)", "Amount (Rs.)"],
            [f"Gross Service Charge: {payment.description or 'Cooperative Work Item'}", "100%", f"Rs. {gross_amt:,.2f}"],
            ["   ↳ Direct Worker Living Wage (Paid to Artisan Bank A/c)", "88%", f"Rs. {worker_wage:,.2f}"],
            ["   ↳ Primary Labour Cooperative Society (Admin & Operations)", "8%", f"Rs. {society_fee:,.2f}"],
            ["   ↳ Worker Social Security Cess (PMJJBY & PMSBY Suraksha Nidhi)", "4%", f"Rs. {welfare_cess:,.2f}"],
            ["Total Customer Payable (Inclusive of All Cess & Society Fees)", "-", f"Rs. {gross_amt:,.2f}"]
        ]
        t_fin = Table(table_data, colWidths=[350, 70, 120])
        t_fin.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 5),
            # Indented sub-rows styling
            ('TEXTCOLOR', (0,2), (0,4), colors.HexColor('#1e293b')),
            ('BACKGROUND', (0,2), (-1,4), colors.HexColor('#f8fafc')),
            ('FONTNAME', (0,4), (-1,4), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,4), (-1,4), colors.HexColor('#15803d')),
            ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#f0fdf4')),
            # Total row
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ]))
        story.append(t_fin)
        story.append(Spacer(1, 10))

        # Welfare Suraksha Nidhi Box
        welfare_callout = [
            [
                Paragraph(
                    "<b>★ Statutory Welfare & Insurance Contribution Notice:</b><br/>"
                    f"This invoice automatically contributed <b>Rs. {welfare_cess:,.2f} (4% Micro-Cess)</b> directly to the worker's individual "
                    "<b>Cooperative Suraksha Nidhi</b>. This fund automatically finances annual enrollment under the "
                    "<b>Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY - Rs. 436/yr for Rs. 2,00,000 Life Cover)</b> and the "
                    "<b>Pradhan Mantri Suraksha Bima Yojana (PMSBY - Rs. 20/yr for Rs. 2,00,000 Accidental Cover)</b>.",
                    welfare_banner_style
                )
            ]
        ]
        t_welfare = Table(welfare_callout, colWidths=[540])
        t_welfare.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#86efac')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_welfare)
        story.append(Spacer(1, 14))
        
        # Digital Authorization / Signature details
        if payment.signed_by_customer:
            story.append(Paragraph("<b>Digitally Authorized by Customer:</b>", header_style))
            story.append(Paragraph(f"Authorized via SahakarSeva Web Canvas signature pad. Status: <b>PAID & RECONCILED</b>. Invoice Token: <code>{payment.invoice_number}</code>", body_style))
        else:
            story.append(Paragraph("<b>Authorization Status:</b> Awaiting client digital sign & payment verification.", body_style))
            
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_report_pdf(report_type):
        """
        Generates general system summaries (Attendance logs, Projects portfolios, Financial balances).
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=40, bottomMargin=40)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle', parent=styles['Heading1'],
            fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'), spaceAfter=15
        )
        
        story.append(Paragraph(f"SahakarSeva System Report - {report_type.upper()}", title_style))
        story.append(Spacer(1, 15))
        
        if report_type == 'attendance':
            # Attendance Log Sheet
            story.append(Paragraph("Summary logs representing recent field check-ins:", styles['Normal']))
            story.append(Spacer(1, 10))
            logs = Attendance.query.order_by(Attendance.date.desc()).all()
            table_data = [["Worker", "Date", "Service Site", "Check-In", "GPS Verified", "Status"]]
            for l in logs[:10]:
                site_lbl = getattr(l, 'site_name', None) or (l.project.name if l.project else "Service Site")
                table_data.append([
                    l.worker.user.username,
                    l.date.strftime('%Y-%b-%d'),
                    site_lbl[:20],
                    l.check_in_time.strftime('%I:%M %p') if l.check_in_time else '-',
                    "Yes" if l.verified_by_gps else "No",
                    l.status
                ])
            col_widths = [80, 80, 120, 80, 70, 70]
            
        elif report_type == 'financial':
            # Financial Balances Sheet
            story.append(Paragraph("Summarizes general transactional history outflows/inflows:", styles['Normal']))
            story.append(Spacer(1, 10))
            payments = Payment.query.order_by(Payment.date.desc()).all()
            table_data = [["Invoice #", "Type", "Amount", "Date", "Receiver/Client", "Status"]]
            for p in payments:
                table_data.append([
                    p.invoice_number or f"LOG-{p.id}",
                    p.type.upper(),
                    f"${p.amount:,.2f}",
                    p.date.strftime('%Y-%b-%d'),
                    (p.customer.company_name[:20] if p.customer_id else p.worker.user.username if p.worker_id else "General Supplier"),
                    p.status
                ])
            col_widths = [100, 70, 80, 80, 100, 70]
            
        else: # service requests / orders
            # Service Requests Summary Sheet
            story.append(Paragraph("Active cooperative service requests and orders:", styles['Normal']))
            story.append(Spacer(1, 10))
            s_requests = ServiceRequest.query.all()
            table_data = [["Request #", "Title / Client", "Category", "Progress", "Priority", "Status"]]
            for sr in s_requests:
                table_data.append([
                    sr.request_id[:15],
                    (sr.title or sr.customer_name or "Service")[:25],
                    (sr.category or "General")[:15],
                    f"{sr.progress}%",
                    sr.priority or "Normal",
                    sr.status or "Pending"
                ])
            col_widths = [90, 130, 90, 60, 50, 60]
            
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#475569')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_quotation_pdf(quotation_id):
        """
        Generates a professional PDF quotation statement using ReportLab.
        """
        from models.quotation import Quotation
        import json
        
        quote = Quotation.query.get(quotation_id)
        if not quote:
            return None
            
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'QuoteTitle', parent=styles['Heading1'],
            fontSize=24, leading=28, textColor=colors.HexColor('#1a73e8'), spaceAfter=15
        )
        body_style = ParagraphStyle(
            'QuoteBody', parent=styles['Normal'],
            fontSize=10, leading=14, textColor=colors.HexColor('#334155'), spaceAfter=10
        )
        header_style = ParagraphStyle(
            'QuoteHeader', parent=styles['Heading3'],
            fontSize=12, leading=16, textColor=colors.HexColor('#0f172a'), spaceAfter=8
        )
        
        story.append(Paragraph("SahakarSeva Cooperative Services", title_style))
        story.append(Paragraph(f"Digital Quotation Statement - {quote.quotation_number}", header_style))
        story.append(Spacer(1, 10))
        
        # Meta info
        meta_data = [
            ["Quotation Number:", quote.quotation_number],
            ["Issue Date:", quote.created_at.strftime('%B %d, %Y')],
            ["Validity Date:", quote.validity_date.strftime('%B %d, %Y')],
            ["Quotation Status:", quote.status]
        ]
        t_meta = Table(meta_data, colWidths=[120, 300])
        t_meta.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#475569')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 15))
        
        req = quote.service_request
        story.append(Paragraph("<b>Client Contact Information:</b>", header_style))
        story.append(Paragraph(f"Customer Name: {req.customer_name}", body_style))
        story.append(Paragraph(f"Phone Number: {req.mobile_number}", body_style))
        story.append(Paragraph(f"Service Site Address: {req.address}", body_style))
        story.append(Spacer(1, 15))
        
        # Cost Table
        table_data = [["Resource Item Description", "Unit Price", "Qty/Hours", "Total ($)"]]
        
        # Parse materials JSON list
        try:
            mat_items = json.loads(quote.material_list or "[]")
        except Exception:
            mat_items = []
            
        for item in mat_items:
            table_data.append([
                item.get('name', 'Material'),
                f"${float(item.get('price', 0.0)):,.2f}",
                str(item.get('qty', 1)),
                f"${float(item.get('total', 0.0)):,.2f}"
            ])
            
        # Add labor and equipment if non-zero
        if quote.labour_cost and quote.labour_cost > 0:
            table_data.append(["Assigned Field Labor Charges", "-", "-", f"${quote.labour_cost:,.2f}"])
        if quote.equipment_charges and quote.equipment_charges > 0:
            table_data.append(["Assigned Machinery/Equipment Rental", "-", "-", f"${quote.equipment_charges:,.2f}"])
            
        # Summary totals
        table_data.append(["", "", "Labor & Equipment Cost:", f"${float(quote.labour_cost or 0) + float(quote.equipment_charges or 0):,.2f}"])
        table_data.append(["", "", "GST Taxes amount:", f"${quote.gst:,.2f}"])
        table_data.append(["", "", "Discounts / Promos:", f"-${quote.discount:,.2f}"])
        table_data.append(["", "", "Grand Final Cost Estimate:", f"${quote.grand_total:,.2f}"])
        
        t_quote = Table(table_data, colWidths=[200, 70, 70, 100])
        t_quote.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (2,-4), (3,-1), 'Helvetica-Bold'),
            ('BACKGROUND', (0,-4), (-1,-1), colors.HexColor('#f8fafc')),
        ]))
        story.append(t_quote)
        story.append(Spacer(1, 20))
        
        if quote.terms_conditions:
            story.append(Paragraph("<b>Terms & Conditions:</b>", header_style))
            story.append(Paragraph(quote.terms_conditions, body_style))
            
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_tabular_pdf(entity_type, records):
        """
        Generates a tabular export PDF for any entity list using ReportLab.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ExportTitle', parent=styles['Heading1'],
            fontSize=18, leading=22, textColor=colors.HexColor('#1e293b'), spaceAfter=15
        )
        
        story.append(Paragraph(f"Export Report: {entity_type.upper()}", title_style))
        story.append(Spacer(1, 10))
        
        if not records:
            story.append(Paragraph("No records found.", styles['Normal']))
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        # Headers from first record keys
        headers = list(records[0].keys())
        table_data = [headers]
        
        for r in records:
            row = []
            for h in headers:
                val = r.get(h, '')
                # Truncate strings to prevent overflow
                if isinstance(val, str) and len(val) > 30:
                    val = val[:27] + "..."
                row.append(str(val) if val is not None else '')
            table_data.append(row)
            
        # Determine average column widths
        num_cols = len(headers)
        col_width = max(35, 520 / num_cols)
        
        t = Table(table_data, colWidths=[col_width] * num_cols)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

