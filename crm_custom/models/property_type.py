from odoo import api, fields, models, _


class PropertyType(models.Model):
    _name = "property.type"

    name = fields.Char(string="Property Type")
