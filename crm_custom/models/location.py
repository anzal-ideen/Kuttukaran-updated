from odoo import api, fields, models, _


class Location(models.Model):
    _name = "location"

    name = fields.Char(string="Municipality")
    district = fields.Char(string="District")
    pin_code = fields.Char(string="PIN")

