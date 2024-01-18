from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, MissingError, UserError
from datetime import date
from num2words import num2words


class PoInhrerited(models.Model):
    _inherit = "purchase.order"
    _description = 'Purchase Order'

    terms_conditions = fields.Text("Terms and Conditions")
    is_terms = fields.Boolean("With Annexure")

    def amount_total_in_words(self):
        # Replace 'self.amount_total' with your actual field
        amount = self.amount_total or 0.0
        return num2words(amount, lang='en_IN')



