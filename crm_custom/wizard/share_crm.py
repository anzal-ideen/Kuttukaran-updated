from odoo import api, fields, models
from odoo.exceptions import ValidationError, MissingError, UserError


class SharedCrmWizard(models.TransientModel):
    _name = "shared.crm.wizard"
    _description = "Shared CRM Wizard"

    name = fields.Char(string="Opportunity")
    expected_revenue = fields.Monetary(string='Expected Revenue', currency_field='currency_id')
    probability = fields.Float(string='Probability')
    currency_id = fields.Many2one('res.currency', string='Currency')
    partner_id = fields.Many2one("res.partner", string="Customer")
    email_from = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    user_id = fields.Many2one('res.users', string="Salesperson")
    date_deadline = fields.Date(string="Expected Closing")
    tag_ids = fields.Many2many('crm.tags', string="Tags")
    shared_by = fields.Many2one('res.company', string="Shared By")
    shared_to = fields.Many2one('res.company', string="Shared To")
    property_type = fields.Many2one('property.type', string="Property Type")
    customers_type = fields.Many2one('customer.type', string="Customer Type")
    budget = fields.Many2one('budget', string="Budget")
    product_category = fields.Many2one('product.category', string="Product Category")
    region = fields.Char(string='Region')
    municipality = fields.Many2one('location', string='Municipality')
    district = fields.Char(string='District')
    pin_code = fields.Char(string='PIN Code')
    crm_id = fields.Many2one('crm.lead', string="crm_id")
    company_id = fields.Many2one('res.company', string="Company")

    def share_crm_data(self):
        print("Inside crm dfuuiii")
        print("self.pin_code ", self.pin_code)
        crm_lead_obj = self.env['crm.lead']
        partner = self.env['res.partner'].sudo().search(
            [('id', '=', self.partner_id.id), ('company_id', '=', self.shared_to.id
                                               )], limit=1)
        if not partner:
            partner_data = self.env['res.partner'].sudo().search(
                [('id', '=', self.partner_id.id)], limit=1)     # company_id condition not added
            partner_obj = self.env['res.partner']
            partner_obj = partner_obj.sudo().create({
                "name": partner_data.name,
                "email": partner_data.email,
                "website": partner_data.website,
                "phone": partner_data.phone,
                "street": partner_data.street,
                "zip": partner_data.zip,
                "city": partner_data.city,
                "state_id": partner_data.state_id.id,
                "country_id": partner_data.country_id.id,
                "company_name": partner_data.name,
                "company_id": self.shared_to.id})
            partner = partner_obj

        crm_lead_obj.sudo().create({
            'name': self.name,
            'expected_revenue': self.expected_revenue,
            'probability': self.probability,
            # 'currency_id': self.currency_id.id,
            'partner_id': partner.id,
            'email_from': self.email_from,
            'phone': self.phone,
            'user_id': self.user_id.id,
            'date_deadline': self.date_deadline,
            # 'tag_ids': [(6, 0, self.tag_ids.ids)],
            'property_type': self.property_type.id,
            'customers_type': self.customers_type.id,
            'budget': self.budget.id,
            'product_category': self.product_category.id,
            'region': self.region,
            'municipality': self.municipality.id,
            'district': self.district,
            'pin_code': self.pin_code,
            'company_id': self.shared_to.id,
            'shared_by': self.shared_by.id,
            'shared_by_check': True
        })

        crm_leads = self.env['crm.lead'].sudo().search([('id', '=', self.crm_id.id)], limit=1)
        crm_leads.write({'shared_to': [(4, self.shared_to.id)]})
        crm_leads.shared_to_check = True

    @api.model
    def default_get(self, fields):
        res = super(SharedCrmWizard, self).default_get(fields)
        # Set the value of example_field based on the context
        res['name'] = self.env.context.get('name')
        res['expected_revenue'] = self.env.context.get('expected_revenue')
        res['probability'] = self.env.context.get('probability')
        res['partner_id'] = self.env.context.get('partner_id')
        res['email_from'] = self.env.context.get('email_from')
        res['phone'] = self.env.context.get('phone')
        res['user_id'] = self.env.context.get('user_id')
        res['date_deadline'] = self.env.context.get('date_deadline')
        res['property_type'] = self.env.context.get('property_type')
        res['customers_type'] = self.env.context.get('customers_type')
        res['budget'] = self.env.context.get('budget')
        res['product_category'] = self.env.context.get('product_category')
        res['region'] = self.env.context.get('region')
        res['municipality'] = self.env.context.get('municipality')
        res['district'] = self.env.context.get('district')
        res['company_id'] = self.env.context.get('company_id')
        res['shared_by'] = self.env.context.get('shared_by')
        res['crm_id'] = self.env.context.get('crm_id')
        res['pin_code'] = self.env.context.get('pin_code')
        # print("Default Get")
        return res
