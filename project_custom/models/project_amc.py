from odoo import api, fields , models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
import datetime


class ProjectAmc(models.Model):
    _name = "project.amc"
    _description = "AMC"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = 'project_name'

    def default_get(self, fields):
        res = super(ProjectAmc, self).default_get(fields)
        res['start_date'] = datetime.date.today()
        return res

    company_name = fields.Many2one("res.partner", string="Customer")
    project_name = fields.Many2one("project.project",string="Project Name")
    start_date = fields.Date(string="Start Date (MM/DD/YY)")
    expiry_date = fields.Date(string="Expiry Date (MM/DD/YY)",compute='_compute_expiry_date', store=True)
    amc_cost = fields.Integer(string="Annual maintenance Charge :",required=True)
    amc_inc_perc = fields.Integer(string="Annual raise percentage :", required=True)
    payment_term = fields.Selection([
        ('monthly','Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annually'),
        ('annual', 'Annually')], string="Payment Terms",required=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancel', 'Cancelled')], string="state", required=True)
    payment_no = fields.Integer(string="Total Payments",compute='_compute_period', store=True)
    count = fields.Integer(string="Already Paid")
    next_payment_date = fields.Date(string="Next Invoice Due(MM/DD/YY) :",compute='_compute_next_payment_date', store=True)

    @api.depends('start_date')
    def _compute_next_payment_date(self):
        for rec in self:
            if rec.payment_term == 'monthly':
                rec.next_payment_date = rec.start_date + timedelta(days=30)
            elif rec.payment_term == 'quarterly':
                rec.next_payment_date = rec.start_date + timedelta(days=90)
            elif rec.payment_term == 'semi_annual':
                rec.next_payment_date = rec.start_date + timedelta(days=180)
            elif rec.payment_term == 'annual':
                rec.next_payment_date = rec.start_date + timedelta(days=365)

    @api.depends('start_date')
    def _compute_expiry_date(self):
        for record in self:
            if record.start_date:
                # start_date = datetime.strptime(record.start_date, '%Y-%m-%d').date()
                expiry_date = record.start_date + timedelta(days=365)
                record.expiry_date = expiry_date
            else:
                record.expiry_date = False

    @api.depends('payment_term')
    def _compute_period(self):
        for record in self:
            if record.payment_term == 'monthly':
                record.payment_no = 12
            elif record.payment_term == 'quarterly':
                record.payment_no = 4
            elif record.payment_term == 'semi_annual':
                record.payment_no = 2
            elif record.payment_term == 'annual':
                record.payment_no = 1
            else:
                record.payment_no = 0  # Set default value if payment term is not recognized

    @api.model
    def cron_fun(self):
        today = date.today()
        print(today)
        tomorrow = fields.Date.today() + timedelta(days=1)
        for rec in self:
            amount = rec.amc_cost/rec.payment_no
            if rec.next_payment_date == today and rec.count != (rec.payment_no - 1):
                # Check if the product already exists
                product_erp = self.env['product.product'].search([('name', '=', 'AMC')], limit=1)
                if not product_erp:
                    # Create the product if it doesn't exist
                    product_template = self.env['product.template'].create({
                        'name': 'AMC',
                        'detailed_type': 'service',
                        'sale_ok': True,
                        'purchase_ok': False,
                        # Add other relevant fields as needed
                    })
                    # Get the product ID from the created product template
                    product_erp_id = product_template.product_variant_id.id
                else:
                    # Use the existing product ID
                    product_erp_id = product_erp.id

                # Create invoice line for the product
                invoice_line_id = [
                    (0, 0, {
                        'product_id': product_erp_id,
                        'price_unit': amount
                    })
                ]
                proposal_date = self.tomorrow.strftime('%Y-%m-%d')
                print("invoice order")
                # Create the account move
                self.env['account.move'].create({
                    'partner_di': rec.company_name.id,
                    'invoice_date': proposal_date,
                    'invoice_line_ids': invoice_line_id,
                    'state': 'draft',
                })

                # Update the count and next payment date
                rec.count += 1
                if rec.payment_term == 'monthly':
                    rec.next_payment_date = rec.next_payment_date + timedelta(days=30)
                elif rec.payment_term == 'quarterly':
                    rec.next_payment_date = rec.next_payment_date + timedelta(days=90)
                elif rec.payment_term == 'semi_annual':
                    rec.next_payment_date = rec.next_payment_date + timedelta(days=180)
                elif rec.payment_term == 'annual':
                    rec.next_payment_date = rec.next_payment_date + timedelta(days=365)

            print(rec.expiry_date, rec.next_payment_date)

            if rec.expiry_date == today:
                rec.state = 'expired'
                new_amc = rec.amc_cost + ((rec.amc_cost * rec.amc_inc_perc) / 100)

                # Create a new AMC record
                self.env['project.amc'].create({
                    'project_name': rec.project_name.id,
                    'start_date': tomorrow,
                    'amc_cost': new_amc,
                    'amc_inc_perc': rec.amc_inc_perc,
                    'payment_term': rec.payment_term,
                    'state': 'active',
                    'count': '0',
                })
