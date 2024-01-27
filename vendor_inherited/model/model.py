from odoo import models, fields, api



class VendorCategory(models.Model):
    _inherit = 'res.partner'

    category = fields.Char("Category")
    # login = fields.Many2one("res.users","Login User")