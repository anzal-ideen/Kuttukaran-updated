from datetime import datetime
from odoo import api, fields, models, _
# import datetime
import base64
import logging
import xlrd
from odoo.exceptions import ValidationError, MissingError, UserError

_logger = logging.getLogger(__name__)


class Bidding(models.Model):
    _name = "bidding"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Bidding"

    name = fields.Char(string="Bidding No", readonly=True, required=True, copy=False, default='New')
    product_request_id = fields.Many2one('product.request', string="Purchase Request",
                                         domain="[('status', '=', 'wait')]")
    product_request_line_id = fields.Many2one('product.request.line', string="Purchase Request")
    product = fields.Many2one('product.template', string="Product")
    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Float(string="Unit price", required=True)
    date = fields.Date(string="Bidding Date", required=True)
    time = fields.Float(string='Time')
    status = fields.Selection(
        selection=[('draft', 'DRAFT'), ('live', 'LIVE'), ('cancel', 'CANCEL'), ('complete', 'COMPLETE')],
        string='Bidding Status',
        default='draft',
        required=True
    )
    deadline = fields.Date(string='DeadLine', required=True)
    vendors = fields.Many2many("res.partner", string="Vendors")
    top_vendor = fields.Many2one("res.partner", string="Top Vendor", tracking=True)
    top_vendor_price = fields.Float(string="Updating Price")
    bid_request_id = fields.Many2one(string="Bid Request ID")
    duration = fields.Float(string="Duration")
    task_timer = fields.Boolean(string='Timer', default=False)
    is_user_working = fields.Boolean(
        'Is Current User Working', compute='_compute_is_user_working',
        help="Technical field indicating whether the current user is working. ")
    bid_cancel_check = fields.Boolean(string="Bid Cancel Button Check")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bidding') or 'New'

        result = super(Bidding, self).create(vals)

        return result

    bidding_line_ids = fields.One2many('bidding.line', 'bidding_id',
                                       string='Bidding Lines', tracking=True)

    @api.onchange('unit_price')
    def onchange_in_unit_price(self):
        self.top_vendor_price = self.unit_price

    @api.onchange('product')
    def onchange_in_product(self):
        if self.product and self.product_request_id:
            bid = self.env['bidding'].sudo().search(
                [('product_request_id', '=', self.product_request_id.id), ('product', '=', self.product.id)], limit=1)
            if bid:
                raise ValidationError("Bid already created")
            pr_line_data = self.env['product.request.line'].sudo().search(
                [('product_request_id', '=', self.product_request_id.id), ('product', '=', self.product.id)], limit=1)
            if pr_line_data:
                self.quantity = pr_line_data.quantity
                self.unit_price = pr_line_data.unit_price
                self.product_request_line_id = pr_line_data.id
            else:
                raise ValidationError("Product not found")

    @api.onchange('product_request_id')
    def onchange_in_product_request_id(self):
        product_data = self.env['product.request.line'].sudo().search(
            [('product_request_id', '=', self.product_request_id.id)])
        product_list = []
        for product_line in product_data:
            product_list.append(product_line.product.id)
        res = {'domain': {'product': [('id', 'in', product_list)]}}
        return res

    def start_bidding(self):
        if len(self.vendors) <= 1:
            raise ValidationError(_("There aren't enough vendors for the bidding."))
        else:
            bid_request = self.env['bid.request'].sudo().search(
                [('bidding_id', '=', self.id), ('status', '=', 'accept')])
            for bid in bid_request:
                bid.status = 'live'
            self.status = 'live'

    def cancel_bidding(self):
        bidding_vendors = self.env['bid.request'].sudo().search(
            [('bidding_id', '=', self.id), ('status', '!=', 'reject')])
        for vendor_bid in bidding_vendors:
            vendor_bid.status = 'cancel'
        self.status = 'cancel'

    def end_bidding(self):
        bidding_vendors_data = self.env['bidding.line'].sudo().search(
            [('bidding_id', '=', self.id)])
        if not bidding_vendors_data:
            raise ValidationError(
                "No vendors participated in the bidding. Consequently, it is advisable to cancel the bid.")
        bidding_vendors = self.env['bid.request'].sudo().search(
            [('bidding_id', '=', self.id)])
        for vendor_bid in bidding_vendors:
            if vendor_bid.rank == 1:
                vendor_bid.write({
                    'bid_status': 'won',
                    'status': 'complete'
                })
                pr_line_data = self.env['product.request.line'].sudo().search(
                    [('product_request_id', '=', vendor_bid.product_requested_id.id),
                     ('product', '=', self.product.id)], limit=1)
            else:
                if vendor_bid.status != 'reject':
                    vendor_bid.write({
                        'bid_status': 'lose',
                        'status': 'complete'
                    })
        tender_record = self.env['product.tender.line'].sudo().create({
            'vendor': self.top_vendor.id,
            'start_date': pr_line_data.from_date,
            'end_date': pr_line_data.to_date,
            # 'purchase_representative': user_id,
            # 'tender_deadline': top_vendor.deadline,
            'product_template_id': self.product.id,
            'company_id': self.product.company_id.id,
            'quantity': self.quantity,
            'unit_price': self.top_vendor_price,
            'total': self.quantity * self.top_vendor_price
        })
        self.status = 'complete'
        # --------------------------------------------------------------------- PO
        data = []
        child = []
        address = ''

        if self.top_vendor.street:
            address = address + str(self.top_vendor.street) + " "
        if self.top_vendor.street2:
            address = address + str(self.top_vendor.street2) + " "
        if self.top_vendor.city:
            address = address + str(self.top_vendor.city) + " "
        if self.top_vendor.state_id.name:
            address = address + str(self.top_vendor.state_id.name) + " "
        if self.top_vendor.zip:
            address = address + str(self.top_vendor.zip) + " "
        if self.top_vendor.country_id.name:
            address = address + str(self.top_vendor.country_id.name)

        if self.top_vendor:
            partner_id = {
                "name": self.top_vendor.name,
                "ref": "",
                "address": address,
                "phone": self.top_vendor.phone,
                "email": self.top_vendor.email,
                "gst_no": self.top_vendor.vat,
                "state": str(self.top_vendor.state_id.name)
            }
            child.append({
                "name": self.product.name,
                "product_qty": self.quantity,
                "discount": 0,
                "rate": self.unit_price,
                "cgst": 0,
                "sgst": 0,
                "igst": 0,
                "price_unit": self.top_vendor_price
            })
            master = {
                "orderID": None,
                "date_approve": datetime.now(),
                "partner_id": partner_id
            }

            data_dict = {
                "master": master,
                "child": child
            }
            data.append(data_dict)

            for row in data:
                invoice_date = row["master"]["date_approve"]
                # date = datetime.strptime(invoice_date, '%d/%m/%Y')
                vendor_gst = row["master"]["partner_id"]["gst_no"]
                if vendor_gst:
                    vendor = vendor_gst and self.env['res.partner'].sudo().search(
                        [('id', '=', self.top_vendor.id)],
                        limit=1) or False
                    if not vendor:
                        raise ValueError("Vendor is missing")
                else:
                    raise ValueError("GST number is missing")

                order_line = []
                for product_line in row["child"]:
                    product_item = product_line["name"]
                    if product_item:
                        product = product_item and self.env['product.product'].sudo().search(
                            [('name', '=', product_item)], limit=1) or False
                        uom_ids = self.env['uom.uom'].sudo().search([])
                        unit_id = self.env.ref('uom.product_uom_unit') and self.env.ref(
                            'uom.product_uom_unit').id or False
                        for record in uom_ids:
                            if record.name == "kg":
                                unit_id = record.id
                        if not product:
                            raise ValueError("Product is missing")
                    if product:
                        order_line.append((0, 0, {
                            'display_type': False,
                            # 'sequence': 10,
                            'product_id': product.id,
                            'name': product.name or '',
                            # 'date_planned': row.TRANSACTION_DATE or False,
                            'account_analytic_id': False,
                            'product_qty': product_line["product_qty"] or 0,
                            'qty_received_manual': 0,
                            # 'discount': discount or 0,
                            # 'product_uom': product.uom_id.id or request.env.ref(
                            #     'uom.product_uom_unit') and request.env.ref('uom.product_uom_unit').id or False,
                            'price_unit': product_line["price_unit"] or 0,
                            # 'taxes_id': tax_variant and [(6, 0, [tax_variant.id])] or [],
                        }))
            if vendor:
                purchase_order_1 = self.env['purchase.order'].create({
                    'partner_id': vendor.id,
                    # 'partner_ref': row.SALES_ORDER_NUMBER or '',
                    # 'origin': row.INVOICE_NUM or '',
                    # 'date_order':row["master"]["date_order"] or False,
                    # 'date_planned':row["master"]["date_approve"] or False,
                    # 'partner_id': self.env.ref('base.main_partner').id,
                    # 'name': row.INVOICE_NUM or '',
                    'order_line': order_line,
                    'tender_rfq_id': self.id,
                    'bill_to': self.product_request_id.bill_to.id,
                    'ship_to': self.product_request_id.ship_to.id,
                    'location': self.product_request_id.ship_to.id,
                    'department_id': self.product_request_id.department_id.id,
                    'expense_type': self.product_request_id.expense_type,
                    'budget_group_id': self.product_request_id.group_id.id
                })
                # purchase_order_1.button_confirm()
                # self.tender_response_qtn_check = True
                self.env.cr.commit()


class BiddingLine(models.Model):
    _name = "bidding.line"
    _description = "Bidding Line"

    vendor = fields.Many2one("res.partner", string="Vendors")
    price = fields.Float(string="Price")

    bidding_id = fields.Many2one('bidding', string="Bidding", tracking=True)
