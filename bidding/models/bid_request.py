from odoo import api, fields, models
from odoo.exceptions import ValidationError, MissingError, UserError
from datetime import date


class BidRequest(models.Model):
    _name = "bid.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Bidding Request"

    name = fields.Char(string="Bid Request No", readonly=True, required=True, copy=False, default='New')
    product_id = fields.Many2one('product.template', string="Product", store=True, force_save=True, required=True)
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit price")
    total_price = fields.Float(string="Total price")
    date = fields.Date(string="Requested Date")
    time = fields.Float(string='Time')
    deadline = fields.Date(string='DeadLine')
    status = fields.Selection(
        selection=[('draft', 'DRAFT'), ('accept', 'ACCEPT'), ('reject', 'REJECT'), ('live', 'LIVE'),
                   ('complete', 'COMPLETE'), ('cancel', 'CANCEL')],
        string='Bidding Status',
        default='draft',
        required=True,
        tracking=True
    )
    bidding_date = fields.Date(string="Bidding Date")
    request_from = fields.Many2one('res.partner', string="Request from")
    request_to = fields.Many2one('res.partner', string="Request To")
    user_id = fields.Many2one('res.users', string="User Id")
    bidding_id = fields.Many2one('bidding', string="Bidding ID")
    product_requested_id = fields.Many2one('product.request', string="Product Request ID")
    product_request_line_id = fields.Many2one('product.request.line', string="Product Requested ID")
    updated_price = fields.Float(string="Price")
    rank = fields.Integer(string="Rank")
    bid_status = fields.Selection(selection=[('won', 'WON'), ('lose', 'Lose')],
                                  string='Bid Status',
                                  )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bid.request') or 'New'
        result = super(BidRequest, self).create(vals)
        return result

    def action_accept_bid(self):
        print("action_accept_bid")
        print(self.bidding_id.id)
        bidding_data = self.env['bidding'].sudo().search(
            [('id', '=', self.bidding_id.id), ('status', '=', 'draft')], limit=1)
        if not bidding_data:
            self.status = 'reject'
            raise ValidationError("The bidding process has already started or been completed")
        bidding_data.write({'vendors': [(4, self.request_to.id)]})
        self.updated_price = self.unit_price
        self.status = "accept"

    def action_reject_bid(self):
        print("action_reject_bid")
        self.status = "reject"

    def action_draft_bid(self):
        print("action_draft_bid")
        self.status = "draft"

    # def action_open_bid(self):
    #     print(self.id)
    #     vendor_bid_data = self.env['vendor.bid'].sudo().search(
    #         [('bid_request_id', '=', self.id)])
    #     print(vendor_bid_data)
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Vendor Bid',
    #         'res_model': 'vendor.bid',
    #         'domain': [('id', 'in', vendor_bid_data.ids)],
    #         'view_mode': 'tree,form',
    #         'target': 'current'
    #     }

    def update_price(self):
        print("Update function")
        current_date = date.today()
        print("current_date ", current_date)
        bidding = self.env['bidding'].sudo().search(
            [('id', '=', self.bidding_id.id), ('status', '=', 'live')], limit=1)
        if bidding:
            print("bidding.top_vendor_price : ", bidding.top_vendor_price)
            print("self.updated_price : ", self.updated_price)
            if bidding.top_vendor_price > self.updated_price:
                print("update_price")
                account_payment = self.env['bidding.line'].sudo().create({
                    'bidding_id': self.bidding_id.id,
                    'vendor': self.request_to.id,
                    'price': self.updated_price
                })

                # vendor_bid = self.env['vendor.bid'].sudo().search(
                #     [('request_to', '=', self.request_to.id), ('bid_id', '=', self.bid_id.id)], limit=1)
                # if vendor_bid:
                #     vendor_bid.updated_price = self.updated_price

                bid_request_vendor = self.env['bid.request'].sudo().search(
                    [('bidding_id', '=', self.bidding_id.id)], order='updated_price asc')
                num = 0
                for vendors in bid_request_vendor:
                    num += 1
                    vendors.rank = num
                    if vendors.rank == 1:
                        bidding = self.env['bidding'].sudo().search(
                            [('id', '=', self.bidding_id.id)], limit=1)
                        bidding.top_vendor = vendors.request_to
                        bidding.top_vendor_price = vendors.updated_price
                    print("vendors", vendors.rank)
                self.bidding_id.bid_cancel_check = True
            else:
                raise ValidationError("The current price of the product is lower than the price you requested.")
