from odoo import api,fields,models,_
from odoo.exceptions import ValidationError
class VendorModification(models.Model):
    _inherit = 'res.partner'

    category = fields.Char("Category")
    login = fields.Many2one("res.users","Login User",compute="_compute_login_user")



    def action_generate_user(self):
        if self.email:
            user_generated = self.env['res.users'].sudo().create({
                'name': self.name,
                'login': self.email,
                # 'password': ,
                'partner_id': self.id,
            })
        else:
            raise ValidationError("Please Enter User Email address")


    def _compute_login_user(self):
        for rec in self:
            if rec.name:
                vendor_user_id = self.env['res.users'].sudo().search([
                ('partner_id', '=', rec.id)])
                print(vendor_user_id.login)
                print(vendor_user_id.id)
                if vendor_user_id:
                    self.login = vendor_user_id.id
                else:
                    self.login = False
            else:
                self.login = False