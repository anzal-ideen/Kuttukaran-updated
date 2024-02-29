from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime

class Project(models.Model):
    _inherit = "project.project"

    total_amc = fields.Integer(string='Total AMC Count', compute='_compute_total_amc', store=True)
    amc_ids = fields.One2many('project.amc', 'project_name', string="amc ids")
    total_proposals = fields.Integer(string='Total Proposals Count', compute='_compute_total_proposals', store=True)
    proposal_ids = fields.One2many('project.proposals', 'project_name', string="proposals ids")

    def _compute_total_amc(self):
        amcs = self.env['project.amc'].read_group(domain=[], fields=['project_name'],
                                                  groupby=['project_name'])
        for amc in amcs:
            project_name = amc.get('project_name')[0]
            amc_rec = self.filtered(lambda p: p.id == project_name)
            amc_rec.total_amc = amc['project_name_count']
            self -= amc_rec
        self.total_amc = 0

    def _compute_total_proposals(self):
        proposals = self.env['project.proposals'].read_group(domain=[], fields=['project_name'],
                                                                groupby=['project_name'])
        for proposal in proposals:
            project_name = proposal.get('project_name')[0]
            proposal_rec = self.browse(project_name)
            proposal_rec.total_proposals = proposal['project_name_count']
            self = self - proposal_rec
        self.total_proposals = 0


    def action_open_proposals(self):
        return {
            'name': _('Proposals'),
            'view_mode': 'tree,form',
            'res_model': 'project.proposals',
            'type': 'ir.actions.act_window',
            'context': {'default_project_name': self.id,
                        'default_company_name': self.partner_id.id,},
            'domain': [('project_name', '=', self.id)],
            'target': 'current',
        }
    def action_open_amc(self):
        return {
            'name': _('AMC'),
            'view_mode': 'tree,form',
            'res_model': 'project.amc',
            'type': 'ir.actions.act_window',
            'context': {'default_project_name': self.id,
                        'default_company_name': self.partner_id.id,},
            'domain': [('project_name', '=', self.id)],
            'target': 'current',
        }


class ProjectProposals(models.Model):
    _name = "project.proposals"
    _description = "Proposals"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'proposal_name'
    _order = 'id desc'

    def default_get(self, fields):
        res = super(ProjectProposals, self).default_get(fields)
        res['proposal_date'] = datetime.date.today()
        return res
    project_name = fields.Many2one("project.project",string="Project Name")
    proposal_name = fields.Char(string="Proposal Name",required=True)
    company_name = fields.Many2one("res.partner",string="Customer")
    state = fields.Selection([
        ('draft','Draft'),
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')], default="draft", string="Status")
    proposal_date = fields.Date(string="Proposal Date")
    free_service_month = fields.Char(string="Free Service Month(Words)")
    free_service_hour = fields.Integer(string="Free Service Hour")
    effective_from = fields.Date(string="Effective from Date", required=True)
    effective_month_and_year = fields.Char(string="Month and Year", compute='_compute_month_and_year', store=True)
    timeline = fields.Char(string="Timeline")

    html_content = fields.Html(string="HTML Content")

    required_collection =  fields.Integer("Required Collection(In Days)")
    develop_training = fields.Integer("Development and Training(In Days)")

    def get_formatted_date(self):
        # Check if the date field is set
        if self.proposal_date:
            # Format the date to 'day month year' format
            formatted_date = self.proposal_date.strftime('%d %B %Y')
            return formatted_date
        else:
            return ''
    @api.depends('effective_from')
    def _compute_month_and_year(self):
        for record in self:
            if record.effective_from:
                month_year = record.effective_from.strftime("%B %Y")
                record.effective_month_and_year = month_year
            else:
                record.effective_month_and_year = False

    @api.model
    def create(self, vals):
        res = super(ProjectProposals, self).create(vals)
        if res.effective_from:
            res._compute_month_and_year()
        return res

    def write(self, vals):
        res = super(ProjectProposals, self).write(vals)
        if 'effective_from' in vals:
            self._compute_month_and_year()
        return res

    def in_draft(self):
        for rec in self:
            rec.state = 'draft'

    def in_waiting(self):
        for rec in self:

            rec.state = 'waiting'

    def in_approved(self):
        print("product creation")
        self.env['product.template'].create({
            'name': self.proposal_name,
            'detailed_type': 'service',
            'sale_ok': True,
            'purchase_ok': False,
            # Add other relevant fields as needed
        })
        product_erp = self.env['product.product'].search([('name', '=', self.proposal_name)], limit=1)
        if product_erp:
            product_erp_id = product_erp.id
        order_lines = [
            (0, 0, {
               'product_id': product_erp_id
            })
        ]
        proposal_date = self.proposal_date.strftime('%Y-%m-%d')
        print("sale order")
        self.env['sale.order'].create({
            'partner_id': self.company_name.id,
            'date_order': proposal_date,
            'order_line': order_lines,
            # Add other relevant fields as needed
        })
        for rec in self:
            rec.state = 'approved'

    def in_cancel(self):
        for rec in self:
            rec.state = 'cancel'

