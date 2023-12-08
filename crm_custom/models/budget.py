from odoo import api, fields, models, _


class Budget(models.Model):
    _name = "budget"

    name = fields.Char(string="Customer Type")
