from odoo import api, fields, models, _
import datetime


class CrmLeadInherit(models.Model):
    _inherit = "crm.lead"

    property_type = fields.Many2one('property.type', string="Property Type")
    customers_type = fields.Many2one('customer.type', string="Customer Type")
    budget = fields.Many2one('budget', string="Budget")
    product_category = fields.Many2one('product.category', string="Product Category")
    region = fields.Char(string='Region')
    municipality = fields.Many2one('location', string='Municipality')
    district = fields.Char(string='District')
    pin_code = fields.Char(string='PIN Code')
    referred = fields.Many2one('res.partner', string="Referred By")
    shared_by = fields.Many2one('res.company', string="Shared By")
    shared_to = fields.Many2many('res.company', string="Shared To")
    shared_by_check = fields.Boolean(string="Is shared data", default=False)
    shared_to_check = fields.Boolean(string="Is data shared or not", default=False)

    @api.onchange('municipality')
    def onchange_in_municipality(self):
        print("self.municipality.id ", self.municipality.id)
        location = self.env['location'].sudo().search(
            [('id', '=', self.municipality.id)], limit=1)
        if location:
            self.district = location.district
            self.pin_code = location.pin_code

    def check_expiration(self):
        crm_stage = self.env['crm.stage'].sudo().search([], order='id desc', limit=1)
        print("crm_stage id ", crm_stage.id)
        print("crm_stage name ", crm_stage.name)
        crm_leads = self.env['crm.lead'].sudo().search([('stage_id', '=', crm_stage.id)], order='id desc')

        date = datetime.datetime.today() + datetime.timedelta(days=3)
        print(date)

        for crm_lead in crm_leads:
            # print("crm_lead id : ", crm_lead.id)
            # print("crm_lead date_last_stage_update : ", crm_lead.date_last_stage_update)
            days = date - crm_lead.date_last_stage_update
            # print("days : ", days.days)
            # print("days : ", type(days.days))
            if int((datetime.datetime.today() - crm_lead.date_last_stage_update).days) >= 3:
                body = (
                    "Dear Vendor,Your vendor registration has been successfully approved and your Login id is")
                vals = {
                    'subject': 'Email send check',
                    'body_html': body,
                    'email_to': 'vjveeranandhan@gmail.com',
                    'auto_delete': False,
                    # 'email_from': ,
                }
                # print(vals)
                mail_id = self.env['mail.mail'].sudo().create(vals)
                mail_id.sudo().send()

    def action_share_crm(self):
        print("innside custom_button_action")

        if self.shared_to_check:
            self.shared_to_check = False
        else:
            self.shared_to_check = True

        dict_data = {
            'name': self.name,
            'expected_revenue': self.expected_revenue,
            # 'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'email_from': self.email_from,
            'phone': self.phone,
            'user_id': self.user_id.id,
            'date_deadline': self.date_deadline,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'property_type': self.property_type.id,
            'customers_type': self.customers_type.id,
            'budget': self.budget.id,
            'product_category': self.product_category.id,
            'region': self.region,
            'municipality': self.municipality.id,
            'district': self.district,
            'pin_code': self.pin_code,
            'crm_id': self.id,
            'shared_by': self.company_id.id,
            'probability': self.probability
        }
        print("dict_data : ", dict_data)
        # pass
        return {
            'type': 'ir.actions.act_window',
            'name': 'Share CRM',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'shared.crm.wizard',
            'context': dict_data
        }
