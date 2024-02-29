from odoo import models, fields, api



class ProductTypes(models.Model):
    _name = 'product.types'

    name = fields.Char("Name")
    reference = fields.Char("Reference")
    disc = fields.Text("Description")



class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    product_type = fields.Many2one('product.types',"Product Category Type")