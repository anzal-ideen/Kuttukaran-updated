from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, MissingError, UserError
from datetime import date, datetime


class TendersInherit(models.Model):
    _inherit = "tenders"
    _description = 'tender'

    bid_request_check = fields.Boolean(string="Bid Request check", default=False)
    bidding_id = fields.Many2one('bidding', string="Bidding ID")

    def action_add_to_bidding(self):
        print("Inside Bidding")
        # dict_data = {
        #     'product_id': self.product.id,
        #     'quantity': self.quantity,
        #     'unit_price': self.unit_price,
        #     'total_price': self.total_price,
        #     'requested_date': datetime.now(),
        #     # 'time': self.time,
        #     'deadline': self.bidding_id.date,
        #     'status': self.status,
        #     'bidding_date': self.bidding_id.date,
        #     'request_from': self.company_id.id,
        #     'request_to': self.response_from.id,
        #     'user_id': self.user_id.id,
        #     'bidding_id': self.bidding_id.id,
        #     'response_id': self.id,
        #     'product_requested_id': self.product_requested_id,
        #     'product_request_line_id': self.product_request_line_id.id
        # }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add to Bidding wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'add.to.bidding.wizard',
            'context': {
                'product_id': self.product.id,
                'quantity': self.quantity,
                'unit_price': self.unit_price,
                'total_price': self.total_price,
                'requested_date': datetime.now(),
                # 'time': self.time,
                # 'deadline': self.bidding_id.date,
                # 'status': self.status,
                # 'bidding_date': self.bidding_id.date,
                'request_from': self.company_id.id,
                'request_to': self.requested_to.id,
                'user_id': self.user_id.id,
                # 'bidding_id': self.bidding_id.id,
                'tender_id': self.id,
                'pr_id': self.product_requested_id.id,
                # 'product_request_line_id': self.product_request_line_id
            }
        }

    def get_bidding(self):
        print(self.id)
        bidding = self.env['bidding'].sudo().search(
            [('id', '=', self.bidding_id.id)])
        print(bidding)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bid',
            'res_model': 'bidding',
            'domain': [('id', 'in', self.bidding_id.id)],
            'view_mode': 'tree,form',
            'target': 'current'
        }
